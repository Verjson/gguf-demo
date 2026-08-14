"""
RAG pipeline: load a local LLM, embed PDF chunks, store vectors in Postgres/pgvector,
retrieve relevant context, and generate answers.

Exposes `hardware` (CUDA vs CPU) so callers can log and display device metrics.
"""

from __future__ import annotations

import gc
import logging
import os
import time
from typing import Dict, List, Optional

import mlflow
import torch
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import PGVector
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from mlflow.entities import SpanType
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig, pipeline

from src.cpu_runtime import configure_threads
from src.hardware import HardwareInfo, detect_hardware
from src.resource_metrics import memory_snapshot

logger = logging.getLogger(__name__)


def _sdpa_available() -> bool:
    """
    True once scaled-dot-product attention can be requested for Phi-3.

    transformers 4.44 ships ``Phi3SdpaAttention`` but leaves ``_supports_sdpa``
    False, so the loader refuses an implementation it already has. Eager attention
    dominates CPU prefill: a 440-token prompt generating 64 tokens took 75s eager
    against 36s with SDPA, for byte-identical output. Flip the flag when the class
    is really present, and let callers fall back if a model rejects it anyway.
    """
    try:
        from transformers.models.phi3 import modeling_phi3
    except ImportError:
        return False
    if "sdpa" not in getattr(modeling_phi3, "PHI3_ATTENTION_CLASSES", {}):
        return False
    modeling_phi3.Phi3PreTrainedModel._supports_sdpa = True
    return True


class RAGPipeline:
    """
    End-to-end helper for:
      1. Splitting PDFs into chunks
      2. Embedding chunks into Postgres (pgvector) via LangChain PGVector
      3. Retrieving top-k similar chunks for a question
      4. Generating an answer with a locally hosted Hugging Face model
    """

    def __init__(self, config: Dict, hardware: HardwareInfo | None = None):
        self.config = config
        self.hardware = hardware or detect_hardware()
        self.embeddings = None
        self.vector_store: Optional[PGVector] = None
        self.llm = None
        self.tokenizer = None
        self.last_generation_meta: dict = {}
        self.last_retrieval_meta: dict = {}
        self.last_load_meta: dict = {}
        self.last_index_meta: dict = {}
        self.setup_components()

    def setup_components(self) -> None:
        """Initialize embeddings and the text-generation LLM (no eager Postgres connect)."""
        use_cuda = self.hardware.cuda_available
        # Also worth doing on GPU hosts: tokenization, embeddings and BERTScore
        # still run through torch's CPU pools.
        configure_threads()
        logger.info(
            "Initializing pipeline on %s (cuda_available=%s)",
            self.hardware.device,
            use_cuda,
        )

        t0 = time.perf_counter()
        with mlflow.start_span(name="load_pipeline", span_type=SpanType.CHAIN) as span:
            self.embeddings = HuggingFaceEmbeddings(
                model_name=self.config["embeddings"]["model"],
                model_kwargs={"device": "cuda" if use_cuda else "cpu"},
            )

            if self.config.get("llm", {}).get("fine_tuned_path"):
                self.llm = self._load_fine_tuned_model()
            else:
                self.llm = self._load_base_model()

            elapsed = time.perf_counter() - t0
            self.last_load_meta = {
                "model_load_seconds": elapsed,
                **memory_snapshot(),
            }
            span.set_outputs(dict(self.last_load_meta))
        logger.info(
            "Pipeline loaded in %.1fs rss=%.0fMiB gpu=%.0fMiB",
            self.last_load_meta["model_load_seconds"],
            self.last_load_meta.get("peak_rss_mb", 0.0),
            self.last_load_meta.get("peak_gpu_mem_mb", 0.0),
        )

    def _postgres_connection_string(self) -> str:
        user = os.getenv("POSTGRES_USER", "raguser")
        password = os.getenv("POSTGRES_PASSWORD", "ragpass")
        host = os.getenv("POSTGRES_HOST", "postgres")
        db = os.getenv("POSTGRES_DB", "rag_eval")
        return f"postgresql+psycopg2://{user}:{password}@{host}/{db}"

    def _generation_kwargs(self) -> dict:
        """Deterministic defaults for evaluation; override via config.llm."""
        llm = self.config.get("llm", {})
        do_sample = bool(llm.get("do_sample", False))
        temperature = float(llm.get("temperature", 0.0))
        kwargs: dict = {
            "max_new_tokens": llm.get("max_new_tokens", 512),
            "do_sample": do_sample,
            "return_full_text": False,
        }
        # Hugging Face rejects temperature=0 with some pipelines; only pass when sampling
        if do_sample:
            kwargs["temperature"] = max(temperature, 1e-5)
        return kwargs

    def _cpu_dtype(self) -> torch.dtype:
        """
        Weight dtype for CPU inference.

        bfloat16 is the default because it is the dtype Phi-3 ships in, and because
        single-token decode is memory-bandwidth bound: halving the bytes read per
        token roughly halves latency and keeps resident memory near 8GB instead of
        the ~15GB an upcast float32 load needs. Set `llm.cpu_dtype: float32` for
        hosts that prefer float32 (faster prompt prefill on AVX2-only CPUs).
        """
        name = str(self.config.get("llm", {}).get("cpu_dtype", "bfloat16"))
        dtype = getattr(torch, name, None)
        if not isinstance(dtype, torch.dtype):
            logger.warning("Unknown llm.cpu_dtype %r; using bfloat16", name)
            return torch.bfloat16
        return dtype

    def _model_load_kwargs(self) -> dict:
        """Shared dtype / device / 8-bit policy for base and PEFT loads."""
        use_cuda = self.hardware.cuda_available
        kwargs: dict = {
            "low_cpu_mem_usage": True,
        }
        if _sdpa_available():
            kwargs["attn_implementation"] = "sdpa"
        if use_cuda:
            # fp16 on a single GPU. 8-bit (bitsandbytes) is disabled by default because
            # current accelerate+transformers stacks often fail with:
            #   ValueError: `.to` is not supported for 8-bit bitsandbytes models
            # when dispatch_model runs after quantization. Phi-3-mini fits in 12GB fp16.
            load_8bit = bool(self.config.get("llm", {}).get("load_in_8bit", False))
            if load_8bit:
                kwargs["quantization_config"] = BitsAndBytesConfig(load_in_8bit=True)
            else:
                kwargs["torch_dtype"] = torch.float16
            kwargs["device_map"] = {"": 0}
        else:
            kwargs["torch_dtype"] = self._cpu_dtype()
        return kwargs

    def _from_pretrained(self, model_id: str):
        """Load causal LM; fall back to fp16 if an 8-bit dispatch fails."""
        model_kwargs = self._model_load_kwargs()
        try:
            return AutoModelForCausalLM.from_pretrained(model_id, **model_kwargs)
        except ValueError as exc:
            msg = str(exc)
            if "scaled_dot_product_attention" in msg and "attn_implementation" in model_kwargs:
                logger.warning("%s does not support SDPA; using the default attention", model_id)
                model_kwargs.pop("attn_implementation")
                return AutoModelForCausalLM.from_pretrained(model_id, **model_kwargs)
            if "8-bit" not in msg and "4-bit" not in msg:
                raise
            logger.warning("Quantized load failed (%s); falling back to float16", exc)
            return AutoModelForCausalLM.from_pretrained(
                model_id,
                torch_dtype=torch.float16,
                device_map={"": 0},
                low_cpu_mem_usage=True,
            )

    @mlflow.trace(name="load_base_model", span_type=SpanType.CHAIN)
    def _load_base_model(self):
        """
        Load the base causal LM from Hugging Face.

        When CUDA is available: float16 + optional 8-bit to fit smaller GPUs.
        When CUDA is not available: bfloat16 on CPU (slower; metrics will show cuda_used=0).
        """
        model_id = self.config["llm"]["model"]
        self.tokenizer = AutoTokenizer.from_pretrained(model_id)
        use_cuda = self.hardware.cuda_available
        load_8bit = bool(self.config.get("llm", {}).get("load_in_8bit", False)) and use_cuda

        if use_cuda:
            logger.info("Loading %s with CUDA (8-bit=%s)", model_id, load_8bit)
        else:
            logger.info("Loading %s on CPU (no CUDA)", model_id)

        model = self._from_pretrained(model_id)
        return pipeline(
            "text-generation",
            model=model,
            tokenizer=self.tokenizer,
            **self._generation_kwargs(),
        )

    @mlflow.trace(name="load_fine_tuned_model", span_type=SpanType.CHAIN)
    def _load_fine_tuned_model(self):
        """Load LoRA/full fine-tuned weights saved by scripts/05_fine_tune.py."""
        model_path = self.config["llm"]["fine_tuned_path"]
        use_cuda = self.hardware.cuda_available
        logger.info(
            "Loading fine-tuned model from %s on %s",
            model_path,
            "CUDA" if use_cuda else "CPU",
        )

        adapter_config = os.path.join(model_path, "adapter_config.json")
        if os.path.isfile(adapter_config):
            from peft import PeftModel

            base_id = self.config["fine_tuning"]["base_model"]
            self.tokenizer = AutoTokenizer.from_pretrained(model_path)
            # Same quantization / dtype policy as the base model path
            base = self._from_pretrained(base_id)
            model = PeftModel.from_pretrained(base, model_path)
            return pipeline(
                "text-generation",
                model=model,
                tokenizer=self.tokenizer,
                **self._generation_kwargs(),
            )

        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        return pipeline(
            "text-generation",
            model=model_path,
            tokenizer=self.tokenizer,
            device=0 if use_cuda else -1,
            **self._generation_kwargs(),
        )

    @mlflow.trace(name="process_pdf", span_type=SpanType.PARSER)
    def process_pdf(self, pdf_path: str) -> List[Document]:
        """Read one PDF, split into overlapping chunks, return LangChain Documents."""
        loader = PyPDFLoader(pdf_path)
        documents = loader.load()

        # Postgres rejects strings containing NUL (0x00); PDF extractors sometimes emit them.
        for doc in documents:
            if doc.page_content:
                doc.page_content = doc.page_content.replace("\x00", " ")

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.config["chunking"]["chunk_size"],
            chunk_overlap=self.config["chunking"]["chunk_overlap"],
            length_function=len,
            separators=["\n\n", "\n", " ", ""],
        )
        chunks = text_splitter.split_documents(documents)
        for chunk in chunks:
            if chunk.page_content:
                chunk.page_content = chunk.page_content.replace("\x00", " ")
        return chunks

    def _delete_collection_if_exists(self) -> None:
        """Drop the pgvector collection so rebuilds do not duplicate embeddings."""
        name = self.config["vector_store"]["collection_name"]
        try:
            store = PGVector(
                connection_string=self._postgres_connection_string(),
                embedding_function=self.embeddings,
                collection_name=name,
            )
            store.delete_collection()
            logger.info("Deleted existing collection %s before rebuild", name)
        except Exception as exc:  # noqa: BLE001
            logger.debug("No existing collection to delete (%s): %s", name, exc)

    @mlflow.trace(name="create_vector_store", span_type=SpanType.RETRIEVER)
    def create_vector_store(self, documents_dir: str, *, replace: bool = True) -> None:
        """
        Embed every PDF in `documents_dir` and persist vectors in Postgres/pgvector.

        When replace=True (default), clears the collection first to avoid duplicates.
        """
        all_documents: List[Document] = []
        doc_stats: List[dict] = []
        t0 = time.perf_counter()

        for filename in sorted(os.listdir(documents_dir)):
            if not filename.endswith(".pdf"):
                continue
            pdf_path = os.path.join(documents_dir, filename)
            chunks = self.process_pdf(pdf_path)
            all_documents.extend(chunks)
            doc_stats.append({"filename": filename, "num_chunks": len(chunks)})
            logger.info("Processed %s: %d chunks", filename, len(chunks))

        if not all_documents:
            raise ValueError(f"No PDF chunks found in {documents_dir}")

        if replace:
            self._delete_collection_if_exists()

        with mlflow.start_span(name="embed_documents", span_type=SpanType.EMBEDDING) as span:
            self.vector_store = PGVector.from_documents(
                documents=all_documents,
                embedding=self.embeddings,
                connection_string=self._postgres_connection_string(),
                collection_name=self.config["vector_store"]["collection_name"],
                pre_delete_collection=replace,
            )
            span.set_outputs({"n_chunks": len(all_documents)})

        elapsed = time.perf_counter() - t0
        self.last_index_meta = {
            "total_chunks": float(len(all_documents)),
            "num_documents": float(len(doc_stats)),
            "index_seconds": elapsed,
            "document_stats": doc_stats,
        }
        logger.info("Created vector store with %d chunks in %.1fs", len(all_documents), elapsed)

    def load_vector_store(self) -> None:
        """Attach to an existing pgvector collection without re-embedding."""
        self.vector_store = PGVector(
            connection_string=self._postgres_connection_string(),
            embedding_function=self.embeddings,
            collection_name=self.config["vector_store"]["collection_name"],
        )
        logger.info(
            "Loaded existing vector store collection: %s",
            self.config["vector_store"]["collection_name"],
        )

    def ensure_vector_store(self, documents_dir: str) -> None:
        """Load existing store if it has documents; otherwise rebuild (without duplicates)."""
        try:
            self.load_vector_store()
            probe = self.vector_store.similarity_search("test", k=1)
            if probe:
                return
            logger.warning("Vector store is empty — rebuilding from %s", documents_dir)
        except Exception as exc:  # noqa: BLE001
            logger.warning("Could not load vector store (%s). Rebuilding...", exc)

        self.create_vector_store(documents_dir, replace=True)

    @mlflow.trace(name="embed_query", span_type=SpanType.EMBEDDING)
    def embed_query(self, query: str) -> List[float]:
        """Embed a query string with the same encoder used at index time."""
        return self.embeddings.embed_query(query)

    @mlflow.trace(name="vector_search", span_type=SpanType.RETRIEVER)
    def _vector_search(self, query: str, embedding: List[float], k: int) -> List[Document]:
        store = self.vector_store
        if store is None:
            raise ValueError("Vector store not initialized")
        if hasattr(store, "similarity_search_by_vector"):
            return store.similarity_search_by_vector(embedding, k=k)
        return store.similarity_search(query, k=k)

    @mlflow.trace(name="retrieve", span_type=SpanType.RETRIEVER)
    def retrieve_context(self, query: str, k: int = 4) -> str:
        """Semantic search: embed query, find k nearest chunks, concatenate text."""
        if not self.vector_store:
            raise ValueError(
                "Vector store not initialized. Run create_vector_store() or load_vector_store() first."
            )
        embedding = self.embed_query(query)
        docs = self._vector_search(query, embedding, k)
        context = "\n\n".join(doc.page_content for doc in docs)
        self.last_retrieval_meta = {
            "n_chunks_retrieved": float(len(docs)),
            "context_chars": float(len(context)),
        }
        return context

    def _format_user_prompt(self, user_text: str) -> str:
        """Apply the tokenizer chat template when available (e.g. Phi-3 Instruct)."""
        tok = self.tokenizer
        if tok is not None and getattr(tok, "chat_template", None):
            try:
                return tok.apply_chat_template(
                    [{"role": "user", "content": user_text}],
                    tokenize=False,
                    add_generation_prompt=True,
                )
            except Exception as exc:  # noqa: BLE001
                logger.warning("chat_template failed (%s); using raw prompt", exc)
        return user_text

    def _count_tokens(self, text: str) -> int:
        tok = self.tokenizer
        if tok is None or not text:
            return 0
        try:
            return len(tok.encode(text, add_special_tokens=False))
        except Exception:  # noqa: BLE001
            return 0

    def _complete(self, full_prompt: str) -> tuple[str, float]:
        """Run the HF text-generation pipeline; return (answer, wall seconds)."""
        start = time.perf_counter()
        cuda_live = bool(self.hardware.cuda_available and torch.cuda.is_available())
        if cuda_live:
            torch.cuda.synchronize()

        raw = self.llm(full_prompt)[0]["generated_text"]

        if cuda_live:
            torch.cuda.synchronize()
        elapsed = time.perf_counter() - start

        if raw.startswith(full_prompt):
            answer = raw[len(full_prompt) :].strip()
        else:
            answer = raw.strip()
        return answer, elapsed

    def _record_generation_meta(self, full_prompt: str, answer: str, elapsed: float) -> None:
        prompt_tokens = float(self._count_tokens(full_prompt))
        completion_tokens = float(self._count_tokens(answer))
        cuda_live = bool(self.hardware.cuda_available and torch.cuda.is_available())
        self.last_generation_meta = {
            "generation_time": elapsed,
            "cuda_used": 1.0 if cuda_live else 0.0,
            "device": "cuda" if cuda_live else "cpu",
            "prompt_chars": float(len(full_prompt)),
            "response_chars": float(len(answer)),
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "tokens_per_sec": (completion_tokens / elapsed) if elapsed > 0 else 0.0,
        }

    @mlflow.trace(name="judge", span_type=SpanType.LLM)
    def judge_response(self, prompt: str) -> str:
        """
        Extra LLM call for groundedness judging.

        Does **not** update last_generation_meta so it cannot clobber the
        answer-generation timings used for latency metrics.
        """
        full_prompt = self._format_user_prompt(prompt)
        answer, _elapsed = self._complete(full_prompt)
        return answer

    @mlflow.trace(name="generate", span_type=SpanType.LLM)
    def generate_response(self, prompt: str, context: Optional[str] = None) -> str:
        """
        Generate text with the local LLM.

        Records last_generation_meta including cuda_used, token counts, and
        wall-clock time so callers can show CUDA vs CPU performance side by side.

        `cuda_used` here means CUDA was available for this process (same as hardware
        detection). Timing uses CUDA synchronize when available so wall time reflects
        GPU compute, not just CPU-side queueing.

        Live ``@mlflow.trace`` so GenAI spans match real retrieve/generate timing.
        """
        if context:
            user_text = self.config["prompts"]["rag_template"].format(
                context=context,
                question=prompt,
            )
        else:
            user_text = prompt

        full_prompt = self._format_user_prompt(user_text)
        answer, elapsed = self._complete(full_prompt)
        self._record_generation_meta(full_prompt, answer, elapsed)
        logger.info(
            "Generated %d chars (%d tok) in %.2fs on %s",
            len(answer),
            int(self.last_generation_meta.get("completion_tokens", 0)),
            elapsed,
            "CUDA" if self.last_generation_meta.get("cuda_used") else "CPU",
        )
        return answer

    def query_pdf(
        self,
        question: str,
        pdf_path: str,
        use_rag: bool = True,
        k: int = 4,
    ) -> Dict[str, str]:
        """Single-document helper: optionally retrieve context, then answer."""
        context = ""
        if use_rag:
            if not self.vector_store:
                parent = os.path.dirname(pdf_path)
                self.ensure_vector_store(parent if parent else "/app/data/papers")
            context = self.retrieve_context(question, k=k)

        response = self.generate_response(question, context=context if use_rag else None)
        return {"question": question, "context": context, "response": response}

    def cleanup(self) -> None:
        """
        Drop the model so the next pipeline in the same process starts from a clean
        budget. Step 06 builds three pipelines back to back; reference cycles inside
        a transformers pipeline can otherwise keep the previous ~8GB copy alive until
        the next collection and double peak memory.
        """
        self.vector_store = None
        self.llm = None
        self.tokenizer = None
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
