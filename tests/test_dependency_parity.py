"""The project metadata is the sole direct-dependency authority for the app image."""

from __future__ import annotations

import re
from pathlib import Path

import tomllib

REPO_ROOT = Path(__file__).resolve().parent.parent
PYPROJECT = REPO_ROOT / "pyproject.toml"
DOCKERFILE = REPO_ROOT / "Dockerfile.app"
MLFLOW_DOCKERFILE = REPO_ROOT / "Dockerfile.mlflow"
COMPOSE_FILE = REPO_ROOT / "docker-compose.yml"
LOCKFILE = REPO_ROOT / "requirements.lock"


def _project():
    return tomllib.loads(PYPROJECT.read_text(encoding="utf-8"))


def _requirements(section="dependencies"):
    if section == "dependencies":
        raw = _project()["project"][section]
    else:
        raw = _project()["project"]["optional-dependencies"][section]
    return {re.match(r"([A-Za-z0-9_.-]+)(.*)", item).group(1).lower(): item for item in raw}


def test_docker_installs_project_dependencies_from_pyproject():
    dockerfile = DOCKERFILE.read_text(encoding="utf-8")
    assert "pip install --no-cache-dir -c requirements.lock -e ." in dockerfile
    assert "-e . --no-deps" not in dockerfile
    assert "transformers==" not in dockerfile


def test_containers_constrain_transitive_dependencies_to_the_reviewed_lock():
    assert "-c requirements.lock" in DOCKERFILE.read_text(encoding="utf-8")
    assert "-c /tmp/requirements.lock" in MLFLOW_DOCKERFILE.read_text(encoding="utf-8")


def test_mlflow_allows_compose_dns_without_disabling_host_validation():
    compose = COMPOSE_FILE.read_text(encoding="utf-8")
    assert (
        "--allowed-hosts mlflow:5000,rag-mlflow:5000,mlflow,rag-mlflow,localhost,127.0.0.1"
        in compose
    )
    assert '--allowed-hosts "*"' not in compose
    assert "--cors-allowed-origins \"*\"" not in compose


def test_every_direct_dependency_is_pinned_in_the_lock():
    locked = {
        match.group(1).lower(): match.group(2)
        for line in LOCKFILE.read_text(encoding="utf-8").splitlines()
        if (match := re.fullmatch(r"([A-Za-z0-9_.-]+)==([^ ;]+)", line))
    }
    requirements = {
        **_requirements(),
        **_requirements("gpu"),
        **_requirements("gguf-cuda"),
        **_requirements("dev"),
    }
    for name, requirement in requirements.items():
        base_name = name.split("[", 1)[0]
        expected = requirement.split("==", 1)[1]
        assert locked[base_name] == expected, f"{requirement} is stale or absent in requirements.lock"


def test_index_selected_dependencies_match_project_versions():
    dockerfile = DOCKERFILE.read_text(encoding="utf-8")
    core = _requirements()
    gpu = _requirements("gpu")
    gguf = _requirements("gguf-cuda")

    assert core["torch"] == "torch==2.13.0"
    assert '"torch==2.13.0"' in dockerfile
    assert gpu["bitsandbytes"] == "bitsandbytes==0.50.1"
    assert '"bitsandbytes==0.50.1"' in dockerfile
    assert gguf["llama-cpp-python"] == "llama-cpp-python==0.3.34"
    assert "ARG LLAMA_CPP_VERSION=0.3.34" in dockerfile


def test_sunset_langchain_community_is_not_a_dependency_or_import():
    assert "langchain-community" not in _requirements()
    importers = list((REPO_ROOT / "src").rglob("*.py")) + list((REPO_ROOT / "scripts").glob("*.py"))
    offenders = [path for path in importers if "langchain_community" in path.read_text(encoding="utf-8")]
    assert not offenders
