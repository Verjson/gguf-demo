from src.latency import attach_generation_meta, attach_latency_metrics, attach_retrieval_meta, llm_run_params
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
    assert metrics["cuda_used"] == 0.0
    assert metrics["cpu_threads"] == 28.0
    assert metrics["cpu_logical"] == 32.0
