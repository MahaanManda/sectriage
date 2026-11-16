# Deploying SecTriage

Nothing here has been deployed yet. The container has **not been built or run** on the machine that prepared it (Docker is not installed there), so do a local build first.

## Local container check
```bash
docker build -t sectriage .
docker run --rm -p 8000:8000 -e ANTHROPIC_API_KEY=... -e TRIAGE_API_TOKEN=choose-a-long-random-string sectriage
```
Open http://localhost:8000. If `TRIAGE_API_TOKEN` is set the page shows an API key box.

## Runtime settings (environment variables, set in the host's secret store, never in the repo)
| Variable | Purpose | Default |
|---|---|---|
| `ANTHROPIC_API_KEY` | Required. Calls the model. | none |
| `TRIAGE_API_TOKEN` | If set, `/triage` needs an `X-API-Key` header with this value. | off |
| `RATE_LIMIT_PER_MIN` | Per-IP calls to `/triage` per minute. | 10 |
| `DAILY_TRIAGE_LIMIT` | Total `/triage` calls per UTC day, all clients. Caps spend. | 300 |
| `PORT` | Listen port; most hosts set this. | 8000 |

## Cost and exposure
- Every agent-mode request makes 2 to 6 model calls. With the default daily cap of 300 requests the worst case is bounded, but it is still your money. Lower `DAILY_TRIAGE_LIMIT` for a public demo.
- Anyone with the URL can use the demo unless you set `TRIAGE_API_TOKEN`. For a portfolio link, either leave it open with a low daily cap, or share the key only in applications.
- Also set a monthly spend limit on the API key in the Anthropic console.
- Counters are in memory, so they reset on restart and are per instance. Run one instance.

## Hosting options (any container host works)
- **Render / Railway / Fly.io:** create a service from the GitHub repo, pick "Docker", add the variables above as secrets. Free tiers sleep when idle, so the first request after a pause is slow.
- **Google Cloud Run:** `gcloud run deploy --source .` with the variables as secrets, max instances 1.
