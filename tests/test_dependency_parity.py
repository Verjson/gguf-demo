"""
pyproject.toml and Dockerfile.app declare the runtime dependencies twice.

The image installs an explicit list rather than resolving pyproject — `pip install -e .`
runs with `--no-deps` so the torch index selection stays deliberate — which means a bump
applied to one file changes nothing in the other. That is how `langchain` came to be
declared `>=0.3.30,<0.4` in pyproject while the image kept installing 0.1.x, and how
pyproject ended up unsatisfiable (langchain 0.3 needs langchain-core>=0.3.85, pinned here
at <0.2) without any build failing.

Collapsing the two lists means making the image resolve pyproject, which would change how
torch is selected. Until that is worth doing, this test is the cheaper guarantee.

What "cheaper guarantee" is worth, precisely: comparing the two lists *statically* cannot
tell you whether either one installs. This test passed throughout the period when the image
could not build at all — python:3.14 (base image bump) plus langchain-community 0.4 (which
requires numpy>=2.1 on 3.13+) against a `numpy<2` pin present, identically, in both files.
Agreeing on a contradiction is still agreement.

So the static checks below are now scoped to what they can actually prove — that the two
lists name the same packages at the same versions — and the question they cannot answer,
"does this resolve", belongs to `docker compose build` in CI. Both matter; neither
substitutes for the other. In particular `test_the_two_lists_have_the_same_membership`
exists because the old intersection-only comparison silently ignored `packaging>=23.2,<24`,
which was installed in the image, absent from pyproject, and unexplained.
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


def test_the_two_lists_have_the_same_membership():
    """
    Neither file may name a runtime dependency the other omits.

    The intersection-only comparison above cannot see a package that exists in one
    list and not the other — which is how `packaging>=23.2,<24` lived in the image,
    unmentioned by pyproject and unexplained by anything, for the life of the repo.

    torch and llama-cpp-python are the deliberate exceptions: both are installed from
    a build-arg-selected index rather than from the flat list, so the Dockerfile spells
    them differently on purpose.
    """
    index_selected = {"torch", "llama-cpp-python", "bitsandbytes"}
    pyproject = set(_pyproject_requirements()) - index_selected
    dockerfile = set(_dockerfile_requirements()) - index_selected

    assert not pyproject - dockerfile, (
        "declared in pyproject.toml but never installed in the image: "
        f"{sorted(pyproject - dockerfile)}"
    )
    assert not dockerfile - pyproject, (
        "installed in the image but undeclared in pyproject.toml, so `pip install -e .` "
        f"on a host does not reproduce the container: {sorted(dockerfile - pyproject)}"
    )


def test_numpy_is_not_pinned_below_what_the_python_version_requires():
    """
    The specific contradiction that made the image unbuildable, frozen as a test.

    langchain-community 0.4 requires numpy>=2.1 on Python 3.13+, and Dockerfile.app
    builds on python:3.14-slim. A `<2` ceiling on numpy is therefore not a conservative
    choice, it is an unsatisfiable one — and pip only says so at build time, which is
    why this assertion is cheap enough to keep in the unit suite.
    """
    base_image = re.search(r"^FROM\s+python:(\d+)\.(\d+)", DOCKERFILE.read_text(encoding="utf-8"), re.MULTILINE)
    assert base_image, "could not read the Python version from Dockerfile.app's FROM line"
    major, minor = int(base_image.group(1)), int(base_image.group(2))

    for label, requirements in (
        ("pyproject.toml", _pyproject_requirements()),
        ("Dockerfile.app", _dockerfile_requirements()),
    ):
        spec = requirements.get("numpy", "")
        if (major, minor) >= (3, 13):
            assert "<2" not in spec, (
                f"{label} pins numpy {spec} while the image runs Python {major}.{minor}; "
                "langchain-community 0.4 requires numpy>=2.1 there, so this cannot resolve"
            )


def test_the_postgres_vector_store_has_its_psycopg3_driver():
    """langchain-postgres speaks psycopg 3; psycopg2 remains for the direct metrics writes."""
    for requirements in (_pyproject_requirements(), _dockerfile_requirements()):
        assert "psycopg[binary]" in requirements
        assert "psycopg2-binary" in requirements
