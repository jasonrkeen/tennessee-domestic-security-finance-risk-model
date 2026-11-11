"""Tests must never retrieve live source data."""
import pytest
import requests


@pytest.fixture(autouse=True)
def block_live_requests(monkeypatch):
    def blocked(*args, **kwargs):
        pytest.fail("Live HTTP requests are forbidden in offline tests")

    monkeypatch.setattr(requests.sessions.Session, "request", blocked)
