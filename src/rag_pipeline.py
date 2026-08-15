"""
RAG pipeline: embed PDF chunks, retrieve context, generate with a swappable LLM engine.

Generation is an ``LlmEngine`` from ``src.llm.factory`` (Transformers or GGUF today).
Retrieval stays LangChain + pgvector regardless of which generator is plugged in.
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
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_postgres import PGVector
from langchain_text_splitters import RecursiveCharacterTextSplitter
from mlflow.entities import SpanType

from src.cpu_runtime import configure_threads
from src.hardware import HardwareInfo, detect_hardware
from src.llm.factory import build_engine
from src.llm.port import LlmEngine
from src.llm.runtime import decode_settings, resolve_runtime
from src.resource_metrics import memory_snapshot

logger = logging.getLogger(__name__)


class RAGPipeline:
    """
    End-to-end helper for:
      1. Splitting PDFs into chunks
      2. Embedding chunks into Postgres (pgvector)
      3. Retrieving top-k similar chunks for a question
      4. Generating an answer with whatever ``LlmEngine`` the factory built
    """

    def __init__(
        self,
        config: Dict,
        hardware: HardwareInfo | None = None,
        *,
        runtime: str | None = None,
        engine: LlmEngine | None = None,
    ):
        self.config = config
        self.hardware = hardware or detect_hardware()
        self.runtime = resolve_runtime(config, runtime)
        self.embeddings = None
        self.vector_store: Optional[PGVector] = None
        self.engine: LlmEngine | None = engine
        self.llm = None  # alias of the engine for older callers
        self.tokenizer = None
        self.last_generation_meta: dict = {}
        self.last_retrieval_meta: dict = {}
        self.last_load_meta: dict = {}
        self.last_index_meta: dict = {}
        self.setup_components()

    def setup_components(self) -> None:
        """Initialize embeddings and the configured LLM engine."""
        use_cuda = self.hardware.cuda_available
        configure_threads()
        logger.info(
            "Initializing pipeline runtime=%s device=%s cuda_available=%s",
            self.runtime,
            self.hardware.device,
            use_cuda,
        )

        t0 = time.perf_counter()
        with mlflow.start_span(name="load_pipeline", span_type=SpanType.CHAIN) as span:
            self.embeddings = HuggingFaceEmbeddings(
                model_name=self.config["embeddings"]["model"],
                model_kwargs={"device": "cuda" if use_cuda else "cpu"},
            )
            if self.engine is None:
                self.engine = build_engine(self.config, self.hardware, runtime=self.runtime)
            self.llm = self.engine
            self.tokenizer = getattr(self.engine, "tokenizer", None)

            elapsed = time.perf_counter() - t0
            engine_meta = self.engine.load_meta() if self.engine is not None else {}
            self.last_load_meta = {
                "model_load_seconds": elapsed,
                **memory_snapshot(),
                **{
                    k: v
                    for k, v in engine_meta.items()
                    if isinstance(v, (int, float)) and not isinstance(v, bool)
                },
            }
            span.set_outputs({**dict(self.last_load_meta), **{k: str(v) for k, v in engine_meta.items()}})
        logger.info(
            "Pipeline loaded runtime=%s in %.1fs rss=%.0fMiB gpu=%.0fMiB",
            self.runtime,
            self.last_load_meta["model_load_seconds"],
            self.last_load_meta.get("peak_rss_mb", 0.0),
            self.last_load_meta.get("peak_gpu_mem_mb", 0.0),
        )

    def _postgres_connection_string(self) -> str:
        user = os.getenv("POSTGRES_USER", "raguser")
        password = os.getenv("POSTGRES_PASSWORD", "ragpass")
        host = os.getenv("POSTGRES_HOST", "postgres")
        db = os.getenv("POSTGRES_DB", "rag_eval")
        return f"postgresql+psycopg://{user}:{password}@{host}/{db}"

    @mlflow.trace(name="process_pdf", span_type=SpanType.PARSER)
    def process_pdf(self, pdf_path: str) -> List[Document]:
        """Read one PDF, split into overlapping chunks, return LangChain Documents."""
        loader = PyPDFLoader(pdf_path)
        documents = loader.load()

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
                connection=self._postgres_connection_string(),
                embeddings=self.embeddings,
                collection_name=name,
            )
            store.delete_collection()
            logger.info("Deleted existing collection %s before rebuild", name)
        except Exception as exc:  # noqa: BLE001
            logger.debug("No existing collection to delete (%s): %s", name, exc)

    @mlflow.trace(name="create_vector_store", span_type=SpanType.RETRIEVER)
    def create_vector_store(self, documents_dir: str, *, replace: bool = True) -> None:
        """Embed every PDF in `documents_dir` and persist vectors in Postgres/pgvector."""
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
                connection=self._postgres_connection_string(),
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
            connection=self._postgres_connection_string(),
            embeddings=self.embeddings,
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
        if self.engine is None:
            return user_text
        return self.engine.format_user_prompt(user_text)

    def _complete(self, full_prompt: str):
        if self.engine is None:
            raise RuntimeError("LLM engine not initialized")
        return self.engine.complete(full_prompt, decode_settings(self.config))

    def _record_generation_meta(self, full_prompt: str, result) -> None:
        cuda_used = float(result.extra.get("cuda_used", 0.0))
        self.last_generation_meta = {
            "generation_time": result.elapsed_seconds,
            "cuda_used": cuda_used,
            "device": "cuda" if cuda_used else "cpu",
            "prompt_chars": float(len(full_prompt)),
            "response_chars": float(len(result.text)),
            "prompt_tokens": result.prompt_tokens,
            "completion_tokens": result.completion_tokens,
            "tokens_per_sec": result.tokens_per_sec,
            "runtime": self.runtime,
        }

    @mlflow.trace(name="judge", span_type=SpanType.LLM)
    def judge_response(self, prompt: str) -> str:
        """Extra LLM call for groundedness; does not clobber last_generation_meta."""
        full_prompt = self._format_user_prompt(prompt)
        result = self._complete(full_prompt)
        return result.text

    @mlflow.trace(name="generate", span_type=SpanType.LLM)
    def generate_response(self, prompt: str, context: Optional[str] = None) -> str:
        """Generate with the plugged-in engine; record last_generation_meta."""
        if context:
            user_text = self.config["prompts"]["rag_template"].format(
                context=context,
                question=prompt,
            )
        else:
            user_text = prompt

        full_prompt = self._format_user_prompt(user_text)
        result = self._complete(full_prompt)
        self._record_generation_meta(full_prompt, result)
        logger.info(
            "Generated %d chars (%d tok) in %.2fs runtime=%s cuda_used=%s",
            len(result.text),
            int(self.last_generation_meta.get("completion_tokens", 0)),
            result.elapsed_seconds,
            self.runtime,
            bool(self.last_generation_meta.get("cuda_used")),
        )
        return result.text

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
        """Drop embeddings + engine so the next pipeline in-process starts clean."""
        self.vector_store = None
        # The sentence-transformer is small next to the LLM, but it is a second model
        # holding VRAM on a GPU run, and leaving it resident contradicts what this
        # method promises its callers.
        self.embeddings = None
        if self.engine is not None:
            self.engine.cleanup()
        self.engine = None
        self.llm = None
        self.tokenizer = None
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
