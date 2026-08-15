"""
pyproject.toml and Dockerfile.app declare the runtime dependencies twice.

The image installs an explicit list rather than resolving pyproject — `pip install -e .`
runs with `--no-deps` so the torch index selection stays deliberate — which means a bump
applied to one file changes nothing in the other. That is how `langchain` came to be
declared `>=0.3.30,<0.4` in pyproject while the image kept installing 0.1.x, and how
pyproject ended up unsatisfiable (langchain 0.3 needs langchain-core>=0.3.85, pinned here
at <0.2) without any build failing.

Collapsing the two lists means making the image resolve pyproject, which would change how
torch is selected. Until that is worth doing, this test is the cheaper guarantee: the two
lists must agree on every package they both name.
"""

from __future__ import annotations

import re
from pathlib import Path

import tomllib

REPO_ROOT = Path(__file__).resolve().parent.parent
PYPROJECT = REPO_ROOT / "pyproject.toml"
DOCKERFILE = REPO_ROOT / "Dockerfile.app"

_REQUIREMENT = re.compile(r'^\s*"([A-Za-z0-9_.\[\]-]+)\s*((?:[<>=!~][^"]*)?)"', re.MULTILINE)


def _normalize(name: str) -> str:
    return name.lower().replace("_", "-")


def _pyproject_requirements() -> dict[str, str]:
    data = tomllib.loads(PYPROJECT.read_text(encoding="utf-8"))
    found = {}
    for raw in data["project"]["dependencies"]:
        match = re.match(r"([A-Za-z0-9_.\[\]-]+)\s*(.*)", raw)
        found[_normalize(match.group(1))] = match.group(2).replace(" ", "")
    return found


def _dockerfile_requirements() -> dict[str, str]:
    """Packages pinned in the image's explicit `pip install` list."""
    found = {}
    for name, spec in _REQUIREMENT.findall(DOCKERFILE.read_text(encoding="utf-8")):
        if spec:  # a bare quoted word is shell, not a requirement
            found[_normalize(name)] = spec.replace(" ", "")
    return found


def test_the_two_dependency_lists_agree_where_they_overlap():
    pyproject = _pyproject_requirements()
    dockerfile = _dockerfile_requirements()

    shared = sorted(set(pyproject) & set(dockerfile))
    assert shared, "parsed no shared packages — one of the two parsers has stopped working"

    mismatched = {
        name: {"pyproject": pyproject[name], "Dockerfile.app": dockerfile[name]}
        for name in shared
        if pyproject[name] != dockerfile[name]
    }
    assert not mismatched, f"pyproject.toml and Dockerfile.app disagree: {mismatched}"


def test_the_langchain_family_is_declared_as_a_coherent_set():
    """
    langchain-community 0.4 requires langchain-core>=1.4, so the family moves together.

    A bump to one member alone is what made pyproject unsatisfiable; pip refused it with
    "Cannot install langchain-core<0.2,>=0.1.10 and langchain==0.3.30".
    """
    pyproject = _pyproject_requirements()

    assert "langchain" not in pyproject, (
        "the langchain umbrella is unused by this codebase and pins the core version; "
        "importers use langchain-core, langchain-community and langchain-text-splitters"
    )
    for member in ("langchain-core", "langchain-text-splitters"):
        assert pyproject[member].startswith(">=1"), (
            f"{member} must be on the v1 line that langchain-community 0.4 requires, "
            f"got {pyproject[member]}"
        )


def test_the_postgres_vector_store_has_its_psycopg3_driver():
    """langchain-postgres speaks psycopg 3; psycopg2 remains for the direct metrics writes."""
    for requirements in (_pyproject_requirements(), _dockerfile_requirements()):
        assert "psycopg[binary]" in requirements
        assert "psycopg2-binary" in requirements
