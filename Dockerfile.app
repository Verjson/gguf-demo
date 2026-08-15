FROM python:3.14.7-slim-trixie@sha256:ce40764625a4ff50df3548277632e7f96c4e77fe75fa848aae9885476e7df5a4

# libgomp is the only runtime library required by the prebuilt ML wheels.
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install project from pyproject.toml (editable so mounted src/scripts pick up changes)
COPY pyproject.toml requirements.lock README.md ./
COPY src/__init__.py ./src/__init__.py

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
#
# The floor is 2.1 and there is no ceiling. langchain-community 0.4 requires
# numpy>=2.1 on Python 3.13+, and this base image is 3.14, so the previous `<2` pin
# made the install unsatisfiable — `ResolutionImpossible`, every build, with a green
# test suite (nothing in it resolves anything). Torch 2.13 is built against numpy 2,
# so the ABI argument the old pin rested on no longer applies.
RUN pip install --no-cache-dir "pip==26.2.1" \
    && pip install --no-cache-dir -c requirements.lock "torch==2.13.0" "numpy==2.5.2" \
        --index-url ${TORCH_INDEX_URL} \
        --extra-index-url https://pypi.org/simple \
    && pip install --no-cache-dir -c requirements.lock -e . \
    && case "$TORCH_INDEX_URL" in \
         */cpu|*/cpu/) echo "Skipping GPU-only bitsandbytes dependency" ;; \
         *) pip install --no-cache-dir -c requirements.lock "bitsandbytes==0.50.1" ;; \
       esac \
    && case "$TORCH_INDEX_URL" in \
         */cpu|*/cpu/) \
           pip install --no-cache-dir -c requirements.lock llama-cpp-python==${LLAMA_CPP_VERSION} \
             --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu ;; \
         *cu12*) \
           pip install --no-cache-dir -c requirements.lock llama-cpp-python==${LLAMA_CPP_VERSION} \
             --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cu124 \
           && python -c "from llama_cpp import Llama" \
           || pip install --no-cache-dir --force-reinstall -c requirements.lock llama-cpp-python==${LLAMA_CPP_VERSION} \
             --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu ;; \
         *) \
           echo "torch is newer than CUDA 12: llama.cpp GPU wheels need libcudart.so.12, using the CPU wheel" \
           && pip install --no-cache-dir -c requirements.lock llama-cpp-python==${LLAMA_CPP_VERSION} \
             --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu ;; \
       esac

# Source changes no longer invalidate the multi-gigabyte dependency layer above.
COPY src/ ./src/
COPY scripts/ ./scripts/
COPY prompts/ ./prompts/
COPY config/ ./config/

# Optionally bake models into the image so first run is offline-friendly
ARG PRELOAD_MODELS=false
ARG LLM_MODEL=microsoft/Phi-3-mini-4k-instruct
ARG LLM_REVISION=f39ac1d28e925b323eae81227eaba4464caced4e
ARG EMBED_MODEL=sentence-transformers/all-MiniLM-L6-v2
ARG EMBED_REVISION=1110a243fdf4706b3f48f1d95db1a4f5529b4d41
RUN if [ "$PRELOAD_MODELS" = "true" ]; then \
      LLM_MODEL="$LLM_MODEL" LLM_REVISION="$LLM_REVISION" python -c "import os; from transformers import AutoTokenizer, AutoModelForCausalLM; \
AutoTokenizer.from_pretrained(os.environ['LLM_MODEL'], revision=os.environ['LLM_REVISION']); \
AutoModelForCausalLM.from_pretrained(os.environ['LLM_MODEL'], revision=os.environ['LLM_REVISION'])"; \
      EMBED_MODEL="$EMBED_MODEL" EMBED_REVISION="$EMBED_REVISION" python -c "import os; from sentence_transformers import SentenceTransformer; \
SentenceTransformer(os.environ['EMBED_MODEL'], revision=os.environ['EMBED_REVISION'])"; \
    fi

RUN mkdir -p /app/data/papers /app/data/processed /app/models \
        /app/.cache/huggingface /tmp/prometheus_multiproc /tmp/home /mlflow-artifacts \
    && chmod 1777 /tmp/prometheus_multiproc /tmp/home /mlflow-artifacts \
    && useradd --create-home --uid 1000 --shell /usr/sbin/nologin app \
    && chown -R app:app /app

ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV HF_HOME=/app/.cache/huggingface
ENV PROMETHEUS_MULTIPROC_DIR=/tmp/prometheus_multiproc
ENV MLFLOW_EXPERIMENT_NAME=gguf-demo

USER app

# Persistent Prometheus /metrics; run scripts via `docker compose exec app python scripts/...`
CMD ["python", "scripts/metrics_server.py"]
