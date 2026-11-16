"""Agentic triage: Claude decides when and what to search in the knowledge base, then submits a verdict."""
import json
import sys

import anthropic
import chromadb

from triage import MODEL, SYSTEM_PROMPT, TOOL as SUBMIT_TOOL, Triage, load_alerts

MAX_TURNS = 6  # hard cap so a confused model cannot loop (or spend) forever

SEARCH_TOOL = {
    "name": "search_knowledge_base",
    "description": (
        "Search the security knowledge base (MITRE-style technique notes and internal playbooks, "
        "including a playbook of known false positives for this environment). "
        "Returns the most relevant passages with their source file names. "
        "Call it with focused queries; you may call it several times."
    ),
    "input_schema": {
        "type": "object",
        "properties": {"query": {"type": "string", "description": "What to look up."}},
        "required": ["query"],
    },
}

AGENT_PROMPT = SYSTEM_PROMPT.replace(
    "If reference material is provided, base your reasoning on it and cite the source file names.",
    "Before deciding, use search_knowledge_base to look up the relevant technique and any known "
    "false-positive patterns. Base your reasoning on what you find and cite source file names. "
    "Then call submit_triage.",
)

_collection = None


def search_kb(query, n_results=4):
    global _collection
    if _collection is None:
        _collection = chromadb.PersistentClient(path="chroma_db").get_collection("security_kb")
    res = _collection.query(query_texts=[query], n_results=n_results)
    return [
        {"source": m["source"], "section": m["section"], "text": d}
        for d, m in zip(res["documents"][0], res["metadatas"][0])
    ]


def format_results(results):
    return "\n\n".join(f"[{r['source']} > {r['section']}]\n{r['text']}" for r in results) or "No results."


def triage_alert_agent(alert, client=None):
    """Return (Triage, trace). trace is a list of {query, sources} for each search the agent made."""
    client = client or anthropic.Anthropic()
    messages = [{"role": "user", "content": "Alert to triage:\n" + json.dumps(alert, indent=2)}]
    trace = []

    for turn in range(MAX_TURNS):
        # On the last allowed turn, force a verdict.
        force = turn == MAX_TURNS - 1
        resp = client.messages.create(
            model=MODEL,
            max_tokens=1500,
            system=AGENT_PROMPT,
            tools=[SEARCH_TOOL, SUBMIT_TOOL],
            tool_choice={"type": "tool", "name": "submit_triage"} if force else {"type": "auto"},
            messages=messages,
        )
        tool_uses = [b for b in resp.content if b.type == "tool_use"]

        submit = next((b for b in tool_uses if b.name == "submit_triage"), None)
        if submit:
            return Triage.model_validate(submit.input), trace

        if not tool_uses:  # model replied with plain text; nudge it
            messages.append({"role": "assistant", "content": resp.content})
            messages.append({"role": "user", "content": "Please call submit_triage with your decision."})
            continue

        messages.append({"role": "assistant", "content": resp.content})
        results = []
        for tu in tool_uses:
            hits = search_kb(tu.input.get("query", "")) if tu.name == "search_knowledge_base" else []
            trace.append({"query": tu.input.get("query"), "sources": sorted({h["source"] for h in hits})})
            results.append({"type": "tool_result", "tool_use_id": tu.id, "content": format_results(hits)})
        messages.append({"role": "user", "content": results})

    raise RuntimeError("Agent did not submit a triage decision")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("Usage: python agent.py A005")
    record = next((r for r in load_alerts() if r["id"] == sys.argv[1]), None)
    if record is None:
        sys.exit(f"No alert with id {sys.argv[1]}")

    result, trace = triage_alert_agent(record["alert"])
    print(f"=== {record['id']}: {record['alert']['title']}  (agent) ===")
    print(result.model_dump_json(indent=2))
    print("\nExpected:", record["label"]["verdict"], "/", record["label"]["category"], "/", record["label"]["severity"])
    print("Searches:")
    for t in trace:
        print(f"  - {t['query']!r} -> {', '.join(t['sources'])}")
