import anthropic
import httpx
import pytest
from fastapi.testclient import TestClient

import api
from tests.fakes import VALID
from triage import Triage

ALERT = {"timestamp": "2026-11-11T14:05:00Z", "source": "Windows Security", "host": "multiple",
         "user": "adm_jkhan", "title": "Admin logons", "details": "14 servers from JUMP01"}


@pytest.fixture(autouse=True)
def clean(monkeypatch):
    api._hits.clear()
    monkeypatch.delenv("TRIAGE_API_TOKEN", raising=False)
    monkeypatch.delenv("RATE_LIMIT_PER_MIN", raising=False)


@pytest.fixture
def client():
    return TestClient(api.app)


def fake_agent(alert, client=None):
    return Triage.model_validate(VALID), [{"query": "q", "sources": ["org_maintenance_windows.md"]}]


def fake_rag(alert, use_rag=True, client=None):
    chunks = [{"source": "T1021_remote_services.md", "section": "x", "text": "y"}] if use_rag else []
    return Triage.model_validate(VALID), chunks


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200 and r.json()["status"] == "ok"


def test_triage_agent_mode(client, monkeypatch):
    monkeypatch.setattr(api, "triage_alert_agent", fake_agent)
    r = client.post("/triage", json={"alert": ALERT})
    body = r.json()
    assert r.status_code == 200
    assert body["mode"] == "agent" and body["triage"]["verdict"] == "benign"
    assert body["searches"][0]["query"] == "q"
    assert body["retrieved_sources"] == ["org_maintenance_windows.md"]


@pytest.mark.parametrize("mode,sources", [("rag", ["T1021_remote_services.md"]), ("baseline", [])])
def test_triage_other_modes(client, monkeypatch, mode, sources):
    monkeypatch.setattr(api, "triage_alert", fake_rag)
    r = client.post("/triage", json={"alert": ALERT, "mode": mode})
    assert r.status_code == 200 and r.json()["retrieved_sources"] == sources


def test_rejects_bad_input(client):
    assert client.post("/triage", json={"alert": {**ALERT, "title": ""}}).status_code == 422
    assert client.post("/triage", json={"alert": {**ALERT, "details": "x" * 5000}}).status_code == 422
    missing = {k: v for k, v in ALERT.items() if k != "host"}
    assert client.post("/triage", json={"alert": missing}).status_code == 422
    assert client.post("/triage", json={"alert": ALERT, "mode": "magic"}).status_code == 422


def test_token_required_when_configured(client, monkeypatch):
    monkeypatch.setattr(api, "triage_alert_agent", fake_agent)
    monkeypatch.setenv("TRIAGE_API_TOKEN", "s3cret")
    assert client.post("/triage", json={"alert": ALERT}).status_code == 401
    assert client.post("/triage", json={"alert": ALERT}, headers={"X-API-Key": "wrong"}).status_code == 401
    assert client.post("/triage", json={"alert": ALERT}, headers={"X-API-Key": "s3cret"}).status_code == 200
    assert client.get("/health").status_code == 200  # health stays open


def test_rate_limit(client, monkeypatch):
    monkeypatch.setattr(api, "triage_alert_agent", fake_agent)
    monkeypatch.setenv("RATE_LIMIT_PER_MIN", "2")
    codes = [client.post("/triage", json={"alert": ALERT}).status_code for _ in range(3)]
    assert codes == [200, 200, 429]


def _raiser(exc):
    def f(*a, **k):
        raise exc
    return f


def _req():
    return httpx.Request("POST", "https://api.anthropic.com/v1/messages")


@pytest.mark.parametrize("exc,status", [
    (anthropic.AuthenticationError("x", response=httpx.Response(401, request=_req()), body=None), 500),
    (anthropic.RateLimitError("x", response=httpx.Response(429, request=_req()), body=None), 503),
    (anthropic.APIConnectionError(request=_req()), 502),
    (RuntimeError("Agent did not submit a triage decision"), 502),
])
def test_upstream_errors_map_to_clean_statuses(client, monkeypatch, exc, status):
    monkeypatch.setattr(api, "triage_alert_agent", _raiser(exc))
    r = client.post("/triage", json={"alert": ALERT})
    assert r.status_code == status
    assert "test-key" not in r.text
