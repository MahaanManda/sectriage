"""Evaluate triage modes on data/alerts.json. Labels are never shown to the model.

Usage: python eval.py [--data data/alerts.json] [--out eval_results/easy] [--modes baseline,rag,agent] [--limit N] [--workers 4]
Writes per-alert results to <out>/<mode>.json and prints a comparison table.
"""
import argparse
import json
import os
from concurrent.futures import ThreadPoolExecutor

import anthropic

from agent import triage_alert_agent
from triage import get_collection, load_alerts, triage_alert

SEV = ["informational", "low", "medium", "high", "critical"]


def run_one(mode, record, client):
    alert = record["alert"]  # label and relevant_docs deliberately excluded
    try:
        if mode == "baseline":
            res, _ = triage_alert(alert, use_rag=False, client=client)
            retrieved = []
        elif mode == "rag":
            res, chunks = triage_alert(alert, use_rag=True, client=client)
            retrieved = sorted({c["source"] for c in chunks})
        else:
            res, trace = triage_alert_agent(alert, client=client)
            retrieved = sorted({s for t in trace for s in t["sources"]})

        return {"id": record["id"], "prediction": res.model_dump(), "retrieved": retrieved, "error": None}
    except Exception as e:  # keep going; failures are reported, not hidden
        return {"id": record["id"], "prediction": None, "retrieved": [], "error": f"{type(e).__name__}: {e}"}


def score(mode, records, results):
    by_id = {r["id"]: r for r in records}
    n = len(results)
    ok = [r for r in results if r["prediction"]]
    m = {"mode": mode, "n": n, "errors": n - len(ok)}
    v = c = s = s1 = tp_hit = tp_n = fp = fn = 0
    recall, covered = [], []
    misses = []
    for r in ok:
        lab, p = by_id[r["id"]]["label"], r["prediction"]
        v += p["verdict"] == lab["verdict"]
        c += p["category"] == lab["category"]
        s += p["severity"] == lab["severity"]
        s1 += abs(SEV.index(p["severity"]) - SEV.index(lab["severity"])) <= 1
        fp += p["verdict"] == "true_positive" and lab["verdict"] == "benign"   # false alarm
        fn += p["verdict"] == "benign" and lab["verdict"] == "true_positive"   # missed threat
        if p["verdict"] != lab["verdict"] or p["category"] != lab["category"]:
            misses.append((r["id"], f"{lab['verdict']}/{lab['category']}", f"{p['verdict']}/{p['category']}"))
        if r["retrieved"]:
            rel = set(by_id[r["id"]].get("relevant_docs", []))
            if rel:
                recall.append(len(rel & set(r["retrieved"])) / len(rel))
        cited = set(p["cited_sources"])
        rel = set(by_id[r["id"]].get("relevant_docs", []))
        if cited and rel:
            covered.append(len(rel & cited) / len(rel))
    k = max(len(ok), 1)
    m.update(
        verdict=v / k, category=c / k, severity=s / k, severity_within1=s1 / k,
        false_alarms=fp, missed_threats=fn,
        retrieval_recall=sum(recall) / len(recall) if recall else None,
        citation_recall=sum(covered) / len(covered) if covered else None,
    )
    return m, misses


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="data/alerts.json")
    ap.add_argument("--out", default="eval_results/easy")
    ap.add_argument("--modes", default="baseline,rag,agent")
    ap.add_argument("--limit", type=int)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--rescore", action="store_true", help="re-score saved predictions against current labels; no API calls")
    args = ap.parse_args()

    records = load_alerts(args.data)[: args.limit]
    os.makedirs(args.out, exist_ok=True)
    client = None if args.rescore else anthropic.Anthropic()
    if not args.rescore:
        get_collection()  # initialise before worker threads start
    summaries = []

    for mode in args.modes.split(","):
        if args.rescore:
            print(f"Re-scoring saved {mode} predictions...", flush=True)
            with open(f"{args.out}/{mode}.json", encoding="utf-8") as f:
                results = json.load(f)[: args.limit]
        else:
            print(f"Running {mode} on {len(records)} alerts...", flush=True)
            with ThreadPoolExecutor(args.workers) as ex:
                results = list(ex.map(lambda r: run_one(mode, r, client), records))
            with open(f"{args.out}/{mode}.json", "w", encoding="utf-8") as f:
                json.dump(results, f, indent=2)
        summary, misses = score(mode, records, results)
        summaries.append(summary)
        print(f"  {mode}: verdict {summary['verdict']:.0%}, category {summary['category']:.0%}, errors {summary['errors']}")
        for mid, exp, got in misses:
            print(f"    miss {mid}: expected {exp}, got {got}")

    with open(f"{args.out}/summary.json", "w", encoding="utf-8") as f:
        json.dump(summaries, f, indent=2)

    pct = lambda x: "  n/a" if x is None else f"{x:5.0%}"
    print("\n| mode | verdict | category | severity | sev ±1 | false alarms | missed threats | retrieval recall | citation recall | errors |")
    print("|---|---|---|---|---|---|---|---|---|---|")
    for s in summaries:
        print(f"| {s['mode']} | {pct(s['verdict'])} | {pct(s['category'])} | {pct(s['severity'])} | {pct(s['severity_within1'])} "
              f"| {s['false_alarms']} | {s['missed_threats']} | {pct(s['retrieval_recall'])} | {pct(s['citation_recall'])} | {s['errors']} |")


if __name__ == "__main__":
    main()
