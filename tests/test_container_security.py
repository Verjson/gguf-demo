from pathlib import Path

import yaml

COMPOSE = yaml.safe_load(
    (Path(__file__).resolve().parent.parent / "docker-compose.yml").read_text(encoding="utf-8")
)
MLFLOW_DOCKERFILE = (
    Path(__file__).resolve().parent.parent / "Dockerfile.mlflow"
).read_text(encoding="utf-8")


def test_python_services_run_non_root_with_read_only_root_filesystems():
    for name in ("app", "mlflow"):
        service = COMPOSE["services"][name]
        assert service["read_only"] is True
        assert "ALL" in service["cap_drop"]
        assert "no-new-privileges:true" in service["security_opt"]
        assert any(entry.startswith("/tmp:") for entry in service["tmpfs"])
    assert COMPOSE["services"]["app"]["user"]
    assert "USER mlflow" in MLFLOW_DOCKERFILE


def test_app_code_and_configuration_mounts_are_read_only():
    volumes = COMPOSE["services"]["app"]["volumes"]
    for destination in ("/app/scripts", "/app/src", "/app/config", "/app/prompts"):
        mount = next(value for value in volumes if f":{destination}" in value)
        assert mount.endswith(":ro")


def test_generated_prompts_are_written_to_the_writable_data_mount():
    app = COMPOSE["services"]["app"]
    assert app["environment"]["PROMPTS_PATH"] == "/app/data/processed/evaluation_prompts.txt"
    data_mount = next(value for value in app["volumes"] if ":/app/data" in value)
    assert not data_mount.endswith(":ro")


def test_all_published_ports_are_bound_to_loopback():
    for name, service in COMPOSE["services"].items():
        for port in service.get("ports", []):
            assert str(port).startswith("127.0.0.1:"), f"{name} publishes {port} beyond loopback"
