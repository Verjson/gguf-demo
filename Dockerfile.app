FROM python:3.10-slim

# Install system dependencies for PDF parsing and builds
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    ninja-build \
    curl \
    git \
    poppler-utils \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install project from pyproject.toml (editable so mounted src/scripts pick up changes)
COPY pyproject.toml README.md ./
COPY src/ ./src/
COPY scripts/ ./scripts/
COPY prompts/ ./prompts/
COPY config/ ./config/

# Install CPU or CUDA torch first (build-arg), then the rest of the project without
# letting pip replace torch from the default PyPI index.
# The portable default is CPU. The GPU Compose overlay selects CUDA 13.0 wheels;
# CUDA 12.6 remains available for hosts with older drivers.
#
# llama-cpp-python is selected from the same build-arg, and the branch matters:
# abetlen publishes prebuilt GPU wheels against CUDA 12.4, which need libcudart.so.12.
# A CUDA 13 torch supplies libcudart.so.13 instead, so on cu130 that wheel can only
# fail to load — and it is 1.9GB, downloaded and discarded on every rebuild (measured:
# ~137s of build time for nothing) before the fallback installs the 23MB CPU wheel.
# Only a cu12x build can use it, so cu13x goes straight to the CPU wheel. The cost is
# that GGUF runs on CPU on a CUDA 13 host; restoring GPU offload means shipping a
# libcudart.so.12 alongside CUDA 13 torch, which needs its own build verification.
ARG TORCH_INDEX_URL=https://download.pytorch.org/whl/cpu
# Pinned exactly: an unpinned install resolves whatever abetlen's index published
# most recently, and that index is fetched over --extra-index-url with no hash to
# check it against. The pin is what makes a build reproducible and stops a newer
# upstream release from entering the image unreviewed.
ARG LLAMA_CPP_VERSION=0.3.34
# numpy is resolved in the same transaction as torch so pip sees both constraints at
# once. Installing it afterwards let a later transaction downgrade numpy underneath an
# already-built torch, which does not fail the build — it fails at `import torch` with
# a C ABI error, far from the cause.
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir torch "numpy>=1.26.3,<2" \
        --index-url ${TORCH_INDEX_URL} \
        --extra-index-url https://pypi.org/simple \
    && pip install --no-cache-dir -e . --no-deps \
    && pip install --no-cache-dir \
        "transformers>=4.36.2,<4.45" \
        "accelerate>=0.25.0" \
        "sentence-transformers>=2.2.2,<3" \
        "langchain>=0.1.0,<0.2" \
        "langchain-community>=0.0.10,<0.1" \
        "langchain-text-splitters>=0.0.1,<0.1" \
        "langchain-core>=0.1.10,<0.2" \
        "pgvector>=0.2.3" \
        "psycopg2-binary>=2.9.9" \
        "sqlalchemy>=2.0.23" \
        "pypdf>=4.2.0" \
        "pdfplumber>=0.10.3" \
        "nltk>=3.8.1" \
        "datasets>=2.16.1" \
        "rouge-score>=0.1.2" \
        "bert-score>=0.3.13" \
        "ragas>=0.1.0,<0.2" \
        "mlflow>=3.1.0,<3.16" \
        "prometheus-client>=0.19.0" \
        "peft>=0.7.1,<0.12" \
        "huggingface_hub>=0.20.0" \
        "pyyaml>=6.0.1" \
        "requests>=2.31.0" \
        "tqdm>=4.66.1" \
        "pandas>=2.1.4" \
        "numpy>=1.26.3,<2" \
        "click>=8.1.7" \
        "rich>=13.7.0" \
        "python-dotenv>=1.0.0" \
        "packaging>=23.2,<24" \
    && case "$TORCH_INDEX_URL" in \
         */cpu|*/cpu/) echo "Skipping GPU-only bitsandbytes dependency" ;; \
         *) pip install --no-cache-dir "bitsandbytes>=0.41.3" ;; \
       esac \
    && case "$TORCH_INDEX_URL" in \
         */cpu|*/cpu/) \
           pip install --no-cache-dir llama-cpp-python==${LLAMA_CPP_VERSION} \
             --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu ;; \
         *cu12*) \
           pip install --no-cache-dir llama-cpp-python==${LLAMA_CPP_VERSION} \
             --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cu124 \
           && python -c "from llama_cpp import Llama" \
           || pip install --no-cache-dir --force-reinstall llama-cpp-python==${LLAMA_CPP_VERSION} \
             --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu ;; \
         *) \
           echo "torch is newer than CUDA 12: llama.cpp GPU wheels need libcudart.so.12, using the CPU wheel" \
           && pip install --no-cache-dir llama-cpp-python==${LLAMA_CPP_VERSION} \
             --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu ;; \
       esac

# Optionally bake models into the image so first run is offline-friendly
ARG PRELOAD_MODELS=false
ARG LLM_MODEL=microsoft/Phi-3-mini-4k-instruct
ARG EMBED_MODEL=sentence-transformers/all-MiniLM-L6-v2
RUN if [ "$PRELOAD_MODELS" = "true" ]; then \
      python -c "from transformers import AutoTokenizer, AutoModelForCausalLM; \
AutoTokenizer.from_pretrained('${LLM_MODEL}'); \
AutoModelForCausalLM.from_pretrained('${LLM_MODEL}')"; \
      python -c "from sentence_transformers import SentenceTransformer; \
SentenceTransformer('${EMBED_MODEL}')"; \
    fi

RUN mkdir -p /app/data/papers /app/data/processed /app/models \
        /app/.cache/huggingface /tmp/prometheus_multiproc /tmp/home /mlflow-artifacts \
    && chmod 1777 /tmp/prometheus_multiproc /tmp/home /mlflow-artifacts

ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV HF_HOME=/app/.cache/huggingface
ENV PROMETHEUS_MULTIPROC_DIR=/tmp/prometheus_multiproc
ENV MLFLOW_EXPERIMENT_NAME=gguf-demo

# Persistent Prometheus /metrics; run scripts via `docker compose exec app python scripts/...`
CMD ["python", "scripts/metrics_server.py"]
