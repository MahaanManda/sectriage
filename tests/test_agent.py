import copy

import pytest

import agent
from tests.fakes import VALID, FakeClient, text, tool_use

ALERT = {"timestamp": "t", "source": "s", "host": "h", "user": "u", "title": "T", "details": "D"}


@pytest.fixture(autouse=True)
def fake_search(monkeypatch):
    monkeypatch.setattr(agent, "search_kb", lambda q, n_results=4: [
        {"source": "org_maintenance_windows.md", "section": "Standing maintenance windows", "text": "Sundays 01:00-05:00"}])


def test_searches_then_submits():
    client = FakeClient([tool_use("search_knowledge_base", {"query": "patch window"})],
                        [tool_use("submit_triage", VALID)])
    result, trace = agent.triage_alert_agent(ALERT, client=client)
    assert result.verdict == "benign"
    assert trace == [{"query": "patch window", "sources": ["org_maintenance_windows.md"]}]
    # the search result went back to the model as a tool_result
    sent_back = client.calls[1]["messages"][-1]["content"][0]
    assert sent_back["type"] == "tool_result" and "Sundays" in sent_back["content"]


def test_first_call_contains_only_the_alert():
    client = FakeClient([tool_use("submit_triage", VALID)])
    agent.triage_alert_agent(ALERT, client=client)
    first = client.calls[0]["messages"][0]["content"]
    assert first.startswith("Alert to triage:") and "label" not in first.lower()


def test_plain_text_reply_gets_nudged():
    client = FakeClient([text("I think it is fine")], [tool_use("submit_triage", VALID)])
    result, _ = agent.triage_alert_agent(ALERT, client=client)
    assert result.verdict == "benign"
    assert "submit_triage" in client.calls[1]["messages"][-1]["content"]


def test_last_turn_forces_a_verdict():
    searches = [[tool_use("search_knowledge_base", {"query": f"q{i}"}, id=f"t{i}")] for i in range(agent.MAX_TURNS - 1)]
    client = FakeClient(*searches, [tool_use("submit_triage", VALID)])
    agent.triage_alert_agent(ALERT, client=client)
    assert len(client.calls) == agent.MAX_TURNS
    assert client.calls[-1]["tool_choice"] == {"type": "tool", "name": "submit_triage"}
    assert client.calls[0]["tool_choice"] == {"type": "auto"}


def test_gives_up_if_model_never_submits():
    client = FakeClient(*[[text("no")] for _ in range(agent.MAX_TURNS)])
    with pytest.raises(RuntimeError):
        agent.triage_alert_agent(ALERT, client=client)


def test_invalid_submission_is_rejected():
    bad = copy.deepcopy(VALID)
    bad["verdict"] = "maybe"
    with pytest.raises(Exception):
        agent.triage_alert_agent(ALERT, client=FakeClient([tool_use("submit_triage", bad)]))
