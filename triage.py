"""Triage one security alert with Claude, optionally grounded in the knowledge base (RAG)."""
import json
import sys
from typing import Literal

import anthropic
import chromadb
from dotenv import load_dotenv
from pydantic import BaseModel, Field

load_dotenv()

MODEL = "claude-sonnet-5-5"
ALERTS_PATH = "data/alerts.json"

Category = Literal[
    "brute_force", "phishing", "valid_accounts", "scripting", "credential_dumping",
    "ransomware", "scheduled_task", "autostart", "impair_defenses", "tool_transfer",
    "remote_services", "network_discovery", "indicator_removal", "data_exfiltration",
    "malware", "benign",
]


class Triage(BaseModel):
    verdict: Literal["true_positive", "benign"] = Field(
        description="true_positive if the alert reflects malicious or unauthorized activity, benign if it is legitimate activity."
    )
    category: Category = Field(description="Best-fitting category. Use 'benign' when the verdict is benign.")
    severity: Literal["informational", "low", "medium", "high", "critical"] = Field(
        description="Use 'informational' for benign alerts."
    )
    confidence: float = Field(ge=0, le=1, description="Confidence in the verdict from 0 to 1.")
    reasoning: str = Field(description="2-4 sentences explaining the decision using evidence from the alert.")
    recommended_actions: list[str] = Field(description="Concrete next steps for an analyst, most important first.")
    cited_sources: list[str] = Field(description="Knowledge base file names that informed the decision. Empty if none were provided.")


SYSTEM_PROMPT = """You are a security analyst assistant that triages alerts for an IT team.
For each alert, decide whether it is a true positive or benign, assign a category and severity,
and recommend next steps. Consider that many alerts are legitimate administration or tool behavior:
do not flag activity as malicious without evidence in the alert. Be calibrated about confidence.
If reference material is provided, base your reasoning on it and cite the source file names.
Always respond by calling the submit_triage tool."""

TOOL = {
    "name": "submit_triage",
    "description": "Submit the triage decision for the alert.",
    "input_schema": Triage.model_json_schema(),
}


def load_alerts(path=ALERTS_PATH):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


_collection = None


def get_collection():
    """One shared Chroma client; creating several for the same path is not thread-safe."""
    global _collection
    if _collection is None:
        _collection = chromadb.PersistentClient(path="chroma_db").get_collection("security_kb")
    return _collection


def retrieve(alert, n_results=5):
    """Find the most relevant knowledge base chunks for an alert."""
    collection = get_collection()
    query = f"{alert['title']}. {alert['details']}"
    res = collection.query(query_texts=[query], n_results=n_results)
    return [
        {"source": m["source"], "section": m["section"], "text": d}
        for d, m in zip(res["documents"][0], res["metadatas"][0])
    ]


def triage_alert(alert, use_rag=True, client=None):
    """Return (Triage, retrieved_chunks). `alert` is only the alert fields, never the label."""
    client = client or anthropic.Anthropic()
    chunks = retrieve(alert) if use_rag else []

    parts = []
    if chunks:
        parts.append("Reference material from the knowledge base:\n")
        for c in chunks:
            parts.append(f"[{c['source']} > {c['section']}]\n{c['text']}\n")
    parts.append("Alert to triage:\n" + json.dumps(alert, indent=2))

    message = client.messages.create(
        model=MODEL,
        max_tokens=1500,
        system=SYSTEM_PROMPT,
        tools=[TOOL],
        messages=[{"role": "user", "content": "\n".join(parts)}],
    )
    tool_use = next((b for b in message.content if b.type == "tool_use"), None)
    if tool_use is None:
        raise RuntimeError(f"Model did not call submit_triage. Response: {message.content}")
    return Triage.model_validate(tool_use.input), chunks


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("Usage: python triage.py A005 [--no-rag]")
    alert_id = sys.argv[1]
    use_rag = "--no-rag" not in sys.argv

    record = next((r for r in load_alerts() if r["id"] == alert_id), None)
    if record is None:
        sys.exit(f"No alert with id {alert_id}")

    result, chunks = triage_alert(record["alert"], use_rag=use_rag)

    print(f"=== {alert_id}: {record['alert']['title']}  (RAG {'on' if use_rag else 'off'}) ===")
    print(result.model_dump_json(indent=2))
    print("\nExpected:", record["label"]["verdict"], "/", record["label"]["category"], "/", record["label"]["severity"])
    if chunks:
        print("Retrieved:", ", ".join(sorted({c["source"] for c in chunks})))
