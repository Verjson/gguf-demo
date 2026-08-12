"""
RAG pipeline: load a local LLM, embed PDF chunks, store vectors in Postgres/pgvector,
retrieve relevant context, and generate answers.

Exposes `hardware` (CUDA vs CPU) so callers can log and display device metrics.
"""

from __future__ import annotations

import logging
import os
import time
from typing import Dict, List, Optional

import torch
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import PGVector
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig, pipeline

from src.hardware import HardwareInfo, detect_hardware

logger = logging.getLogger(__name__)


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
        self.setup_components()

    def setup_components(self) -> None:
        """Initialize embeddings and the text-generation LLM (no eager Postgres connect)."""
        use_cuda = self.hardware.cuda_available
        logger.info(
            "Initializing pipeline on %s (cuda_available=%s)",
            self.hardware.device,
            use_cuda,
        )

        self.embeddings = HuggingFaceEmbeddings(
            model_name=self.config["embeddings"]["model"],
            model_kwargs={"device": "cuda" if use_cuda else "cpu"},
        )

        if self.config.get("llm", {}).get("fine_tuned_path"):
            self.llm = self._load_fine_tuned_model()
        else:
            self.llm = self._load_base_model()

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

    def _model_load_kwargs(self) -> dict:
        """Shared dtype / device / 8-bit policy for base and PEFT loads."""
        use_cuda = self.hardware.cuda_available
        kwargs: dict = {
            "torch_dtype": torch.float16 if use_cuda else torch.float32,
        }
        if use_cuda:
            kwargs["device_map"] = "auto"
            load_8bit = self.config.get("llm", {}).get("load_in_8bit", True)
            if load_8bit:
                kwargs["quantization_config"] = BitsAndBytesConfig(load_in_8bit=True)
        return kwargs

    def _load_base_model(self):
        """
        Load the base causal LM from Hugging Face.

        When CUDA is available: float16 + optional 8-bit to fit smaller GPUs.
        When CUDA is not available: float32 on CPU (slower; metrics will show cuda_used=0).
        """
        model_id = self.config["llm"]["model"]
        self.tokenizer = AutoTokenizer.from_pretrained(model_id)
        use_cuda = self.hardware.cuda_available
        load_8bit = bool(self.config.get("llm", {}).get("load_in_8bit", True)) and use_cuda

        model_kwargs = self._model_load_kwargs()
        if use_cuda:
            logger.info("Loading %s with CUDA (8-bit=%s)", model_id, load_8bit)
        else:
            logger.info("Loading %s on CPU (no CUDA)", model_id)

        model = AutoModelForCausalLM.from_pretrained(model_id, **model_kwargs)
        return pipeline(
            "text-generation",
            model=model,
            tokenizer=self.tokenizer,
            **self._generation_kwargs(),
        )

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
            base = AutoModelForCausalLM.from_pretrained(base_id, **self._model_load_kwargs())
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

    def process_pdf(self, pdf_path: str) -> List[Document]:
        """Read one PDF, split into overlapping chunks, return LangChain Documents."""
        loader = PyPDFLoader(pdf_path)
        documents = loader.load()

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.config["chunking"]["chunk_size"],
            chunk_overlap=self.config["chunking"]["chunk_overlap"],
            length_function=len,
            separators=["\n\n", "\n", " ", ""],
        )
        return text_splitter.split_documents(documents)

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

    def create_vector_store(self, documents_dir: str, *, replace: bool = True) -> None:
        """
        Embed every PDF in `documents_dir` and persist vectors in Postgres/pgvector.

        When replace=True (default), clears the collection first to avoid duplicates.
        """
        all_documents: List[Document] = []

        for filename in os.listdir(documents_dir):
            if not filename.endswith(".pdf"):
                continue
            pdf_path = os.path.join(documents_dir, filename)
            chunks = self.process_pdf(pdf_path)
            all_documents.extend(chunks)
            logger.info("Processed %s: %d chunks", filename, len(chunks))

        if not all_documents:
            raise ValueError(f"No PDF chunks found in {documents_dir}")

        if replace:
            self._delete_collection_if_exists()

        self.vector_store = PGVector.from_documents(
            documents=all_documents,
            embedding=self.embeddings,
            connection_string=self._postgres_connection_string(),
            collection_name=self.config["vector_store"]["collection_name"],
            pre_delete_collection=replace,
        )
        logger.info("Created vector store with %d chunks", len(all_documents))

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

    def retrieve_context(self, query: str, k: int = 4) -> str:
        """Semantic search: embed query, find k nearest chunks, concatenate text."""
        if not self.vector_store:
            raise ValueError(
                "Vector store not initialized. Run create_vector_store() or load_vector_store() first."
            )
        docs = self.vector_store.similarity_search(query, k=k)
        return "\n\n".join(doc.page_content for doc in docs)

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

    def generate_response(self, prompt: str, context: Optional[str] = None) -> str:
        """
        Generate text with the local LLM.

        Records last_generation_meta including cuda_used and wall-clock time so
        callers can show CUDA vs CPU performance side by side.

        `cuda_used` here means CUDA was available for this process (same as hardware
        detection). Timing uses CUDA synchronize when available so wall time reflects
        GPU compute, not just CPU-side queueing.
        """
        if context:
            user_text = self.config["prompts"]["rag_template"].format(
                context=context,
                question=prompt,
            )
        else:
            user_text = prompt

        full_prompt = self._format_user_prompt(user_text)

        start = time.perf_counter()
        cuda_live = bool(self.hardware.cuda_available and torch.cuda.is_available())
        if cuda_live:
            torch.cuda.synchronize()

        raw = self.llm(full_prompt)[0]["generated_text"]

        if cuda_live:
            torch.cuda.synchronize()
        elapsed = time.perf_counter() - start

        # return_full_text=False → generated_text is completion only; still strip echo if present
        if raw.startswith(full_prompt):
            answer = raw[len(full_prompt) :].strip()
        else:
            answer = raw.strip()

        self.last_generation_meta = {
            "generation_time": elapsed,
            # 1.0 when this process could use CUDA (availability). Not a kernel-level probe.
            "cuda_used": 1.0 if cuda_live else 0.0,
            "device": "cuda" if cuda_live else "cpu",
            "prompt_chars": float(len(full_prompt)),
            "response_chars": float(len(answer)),
        }
        logger.info(
            "Generated %d chars in %.2fs on %s",
            len(answer),
            elapsed,
            "CUDA" if cuda_live else "CPU",
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
        """No long-lived DB handle; kept for API compatibility with older scripts."""
        self.vector_store = None
