# SecTriage

An LLM agent that triages security alerts. It decides whether an alert is a true positive or benign, assigns a category and severity, and recommends next steps. It does this by searching a knowledge base of attack-technique notes, response playbooks, and an organization's own policies, then citing what it used. Includes an evaluation harness that compares the agent against a no-retrieval baseline, a FastAPI service, and a small web UI.

**Live demo:** https://sectriage.onrender.com (free hosting, so the first load after idle can take up to a minute)

> **Status:** works end to end locally. The numbers below come from small synthetic test sets, so read them as directional, not as a benchmark. See [Limitations](#limitations).

## What it does

```
alert ──> agent (Claude) ──search_knowledge_base──> Chroma index ──> passages + source files
              │  (up to 6 turns, may search several times)
              └──submit_triage──> validated JSON: verdict, category, severity,
                                  confidence, reasoning, actions, cited sources
```

Three modes, so the value of retrieval can be measured instead of assumed:

| Mode | How it works |
|---|---|
| `baseline` | The model sees only the alert. |
| `rag` | The top 5 knowledge-base passages for the alert are retrieved up front and added to the prompt. |
| `agent` | The model has a `search_knowledge_base` tool and decides what to look up, as many times as it wants (hard cap of 6 turns, the last one forces a verdict). |

Output is forced through a typed schema (Pydantic), so every result has a fixed verdict, category and severity, a confidence between 0 and 1, and the source files it cited.

**Knowledge base** (24 markdown files, 114 chunks, one chunk per section):
- 13 technique notes in the style of MITRE ATT&CK (brute force, credential dumping, scheduled tasks, and so on)
- 7 response playbooks, including one on common false positives in managed environments
- 4 policy documents for a fictional company, Harbor Logistics: approved tools, maintenance windows with a change register, service-account behavior, and asset tiers with a severity policy

## Evaluation

Two labeled test sets, each run once per mode. Labels are never shown to the model. Metrics are exact-match accuracy against the label, plus counts of false alarms (benign called malicious) and missed threats (malicious called benign).

### Hard set: 26 alerts whose answer depends on the organization's policies

Examples: an `adm_` account logging on from a workstation instead of the jump host, a look-alike S3 bucket, a ticket number that is not in the change register, a security tool binary running from the wrong folder. 12 benign, 14 true positive. Labels were written from the policy documents before any model was run.

| mode | verdict | category | severity | severity within 1 level | false alarms | missed threats | retrieval recall |
|---|---|---|---|---|---|---|---|
| baseline | 21/26 (81%) | 20/26 (77%) | 14/26 (54%) | 77% | 1 | 4 | n/a |
| RAG | 23/26 (88%) | 21/26 (81%) | 18/26 (69%) | 88% | 1 | 2 | 55% |
| agent | 24/26 (92%) | 24/26 (92%) | 19/26 (73%) | 96% | 0 | 2 | 59% |

### Original set: 40 alerts, mostly self-contained

| mode | verdict | category | severity | false alarms | missed threats | retrieval recall |
|---|---|---|---|---|---|---|
| baseline | 39/40 (98%) | 35/40 (88%) | 37/40 (93%) | 0 | 1 | n/a |
| RAG | 40/40 (100%) | 37/40 (93%) | 39/40 (98%) | 0 | 0 | 77% |
| agent | 40/40 (100%) | 35/40 (88%) | 39/40 (98%) | 0 | 0 | 81% |

### What the results show
- **On alerts that depend on organization-specific facts, retrieval helps.** Verdict accuracy went from 81% (baseline) to 88% (RAG) and 92% (agent), and the agent made no false alarms. The baseline can't know that `harbor-backup-stage` is not an approved bucket, so it called that transfer benign.
- **On the original alerts it barely matters.** Most of them carry their own context (for example "approved change ticket CHG-1042"), and the baseline already got 39 of 40 verdicts right. The early finding that RAG made almost no difference there is what motivated building the hard set.
- **Severity is the weakest metric in every mode.** Models tend to say High where the policy says Medium or Critical. I did not tune prompts to fix this.
- **Retrieval is the bottleneck.** Retrieval recall is only 55 to 59% on the hard set. The agent's remaining misses are cases where it never retrieved the document that held the answer, for example the Dropbox upload (the approved-tools section was not retrieved) and the unregistered ticket CHG-2060 (the change register was not retrieved).
- **RAG vs agent:** on the hard set the agent is ahead by one alert on verdict and three on category. With 26 alerts and one run each, that gap is within what run-to-run variation could produce.

Per-alert results are in `eval_results/`. Re-running the agent costs roughly 3 to 6 model calls per alert.

### Label changes
Labels are changed only when they contradict the source of truth, and each change is logged. One has been made: **A038** was relabeled from benign to true positive because it was written before the policy documents existed and contradicted them. The relabel moves RAG and the agent up by one alert, because only they have the policy. Details, reason and before/after numbers: [data/LABEL_CHANGES.md](data/LABEL_CHANGES.md).

## Limitations

Please read these before trusting any number above.

- **The data is synthetic and written with Claude's help.** The 40 original alerts, the 26 hard alerts and the Harbor Logistics policies are all invented. The model that is being tested also helped write them, so they may be easier for it to read than real telemetry. Nothing here was tested on real alerts.
- **Small samples, single runs.** 26 and 40 alerts, each mode run once. Model output varies between runs, and I did not repeat runs or compute confidence intervals. Differences of one or two alerts should not be taken as real.
- **The hard set was designed to need the knowledge base.** It shows that retrieval works when the answer lives in the documents. It does not show how much retrieval would help on real alert streams.
- **Category and severity labels have some ambiguity.** For example, an Office macro that arrives by email can reasonably be labeled either "phishing" or "scripting". Several category misses in every mode are of this kind.
- **Policy lookups are not guaranteed.** The agent can miss the document that contains the answer, as the retrieval recall numbers show. It should assist an analyst, not replace one.
- **No authentication, rate-limit or cost testing beyond unit tests.** See [DEPLOY.md](DEPLOY.md).

## Run it

Requires Python 3.14 and an Anthropic API key. The key goes in `.env` (git-ignored); copy `.env.example` and fill it in.

```bash
python -m venv .venv
.venv\Scripts\activate            # Windows; use `source .venv/bin/activate` elsewhere
pip install -r requirements.txt
python ingest.py                  # build the vector index from knowledge_base/
```

```bash
python triage.py A005             # one alert, retrieval up front
python triage.py A005 --no-rag    # one alert, no retrieval
python agent.py H013              # one alert, agent searches itself
python eval.py --data data/alerts_hard.json --out eval_results/hard   # full evaluation
python eval.py --rescore          # re-score saved predictions after a label change, no API calls
```

```bash
uvicorn api:app --port 8000       # then open http://localhost:8000
pytest                            # 21 tests, all with a mocked model client (no API calls)
```

### API
- `POST /triage` with `{"alert": {...}, "mode": "agent" | "rag" | "baseline"}`
- `GET /health`, `GET /samples`, `GET /` (the web UI)

Optional environment settings for a public deployment: `TRIAGE_API_TOKEN`, `RATE_LIMIT_PER_MIN`, `DAILY_TRIAGE_LIMIT`. A Dockerfile is included, but it has not been built or deployed yet.

## Project layout

```
triage.py      single-shot triage (baseline and RAG), schema, prompts
agent.py       tool-use loop with knowledge-base search
eval.py        evaluation harness
api.py         FastAPI service
ui/            single-page web UI
ingest.py      builds the Chroma index
knowledge_base/  24 markdown documents
data/          alerts.json (40), alerts_hard.json (26), LABEL_CHANGES.md
eval_results/  per-alert predictions and summaries
tests/         unit tests with a scripted fake Anthropic client
```

## License
See [LICENSE](LICENSE).
