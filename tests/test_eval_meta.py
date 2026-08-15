from src.latency import (
    attach_generation_meta,
    attach_latency_metrics,
    attach_retrieval_meta,
    llm_run_params,
)
from src.resource_metrics import percentile


def test_percentile_empty_and_single():
    assert percentile([], 50) == 0.0
    assert percentile([4.0], 95) == 4.0


def test_percentile_interpolates():
    values = [1.0, 2.0, 3.0, 4.0]
    assert percentile(values, 0) == 1.0
    assert percentile(values, 100) == 4.0
    assert percentile(values, 50) == 2.5


def test_attach_generation_meta_copies_token_fields():
    metrics: dict[str, float] = {}
    attach_generation_meta(
        metrics,
        {
            "prompt_chars": 10,
            "prompt_tokens": 4,
            "completion_tokens": 8,
            "tokens_per_sec": 2.5,
            "device": "cpu",
        },
    )
    assert metrics["prompt_chars"] == 10.0
    assert metrics["prompt_tokens"] == 4.0
    assert metrics["completion_tokens"] == 8.0
    assert "device" not in metrics


def test_attach_retrieval_meta_and_latency():
    metrics: dict[str, float] = {}
    attach_retrieval_meta(metrics, {"context_chars": 100, "n_chunks_retrieved": 4})
    attach_latency_metrics(
        metrics,
        generation_time=2.0,
        retrieval_time=0.5,
        response_chars=20,
    )
    assert metrics["time_to_response"] == 2.5
    assert metrics["speed_chars_per_sec"] == 10.0
    assert metrics["n_chunks_retrieved"] == 4.0


def test_llm_run_params_defaults():
    params = llm_run_params({"llm": {"max_new_tokens": 128, "cpu_dtype": "bfloat16"}})
    assert params["max_new_tokens"] == 128
    assert params["cpu_dtype"] == "bfloat16"
    assert params["load_in_8bit"] is False
    assert params["runtime"] == "transformers"


def test_hardware_as_metrics_includes_cpu_budget():
    from src.hardware import HardwareInfo

    info = HardwareInfo(
        cuda_available=False,
        device="cpu",
        cuda_device_count=0,
        cuda_device_name=None,
        cuda_capability=None,
        torch_version="2.13.0",
        cuda_version=None,
        cpu_model="Intel i9",
        cpu_logical=32,
        cpu_threads=28,
    )
    metrics = info.as_metrics()
    assert metrics["cpu_threads"] == 28.0
    assert metrics["cpu_logical"] == 32.0


def test_hardware_metrics_do_not_claim_a_generation_ran_on_the_gpu():
    """
    ``cuda_used`` is the engine's to report, not the machine's.

    It used to be emitted here as "a GPU is visible to this process", and because
    every caller applies these with ``metrics.update(...)`` after attaching the
    engine's own measurement, that ambient value overwrote the measured one. On a
    CUDA 13 host the GGUF engine runs on the CPU llama.cpp wheel with n_gpu_layers=0
    and correctly reports ``cuda_used=0.0`` — and the row was still written as
    ``cuda_used=1.0, device=cuda``, which turned the Transformers-vs-GGUF dashboard
    into a GPU-vs-CPU comparison wearing an engine label.
    """
    from src.hardware import HardwareInfo

    on_a_gpu_box = HardwareInfo(
        cuda_available=True,
        device="cuda",
        cuda_device_count=1,
        cuda_device_name="NVIDIA GeForce RTX 4080 Laptop GPU",
        cuda_capability="8.9",
        torch_version="2.13.0+cu130",
        cuda_version="13.0",
        cpu_model="Intel i9",
        cpu_logical=32,
        cpu_threads=28,
    )
    assert "cuda_used" not in on_a_gpu_box.as_metrics()


def test_the_row_device_follows_the_engine_not_the_machine():
    """
    A generation that did not touch the GPU is labelled cpu, on a GPU machine.

    This is the exact case the CUDA-13 llama.cpp fallback produces: the process sees
    a 4080, the GGUF engine offloaded zero layers, and the row must say so.
    """
    from src.hardware import device_for_row

    assert device_for_row(0.0, "cuda") == "cpu"
    assert device_for_row(1.0, "cuda") == "cuda"
    assert device_for_row(0.0, "cpu") == "cpu"
    # No engine measurement at all: fall back to what the process can see rather
    # than asserting cpu, which would be a different wrong answer.
    assert device_for_row(None, "cuda") == "cuda"
