from __future__ import annotations

import importlib.util
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "01_download_papers.py"
SPEC = importlib.util.spec_from_file_location("download_papers_script", SCRIPT)
download_papers = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(download_papers)


class _RedirectResponse:
    url = "https://arxiv.org/pdf/1234.5678.pdf"
    is_redirect = True
    is_permanent_redirect = False
    headers = {"Location": "https://attacker.example/payload"}

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return None

    def raise_for_status(self):
        return None


def test_pdf_download_refuses_redirects_before_writing(monkeypatch, tmp_path):
    calls = []

    def fake_get(url, **kwargs):
        calls.append((url, kwargs))
        return _RedirectResponse()

    monkeypatch.setattr(download_papers.requests, "get", fake_get)
    destination = tmp_path / "paper.pdf"

    result = download_papers.download_pdf.__wrapped__(
        "https://arxiv.org/pdf/1234.5678.pdf", str(destination)
    )

    assert result is False
    assert not destination.exists()
    assert calls[0][1]["allow_redirects"] is False


def test_pdf_allowlist_rejects_lookalike_hosts():
    assert download_papers.pdf_url_is_allowed("https://arxiv.org/pdf/1234.pdf")
    assert not download_papers.pdf_url_is_allowed("https://arxiv.org.attacker.example/a.pdf")
    assert not download_papers.pdf_url_is_allowed("http://arxiv.org/pdf/1234.pdf")
