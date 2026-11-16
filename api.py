"""FastAPI service for SecTriage.

POST /triage   triage one alert (mode: agent | rag | baseline)
GET  /health   liveness check

Optional protection for a public deployment (both read from the environment, never hard-coded):
  TRIAGE_API_TOKEN      if set, requests must send it in the X-API-Key header
  RATE_LIMIT_PER_MIN    max /triage calls per client IP per minute (default 10)
  DAILY_TRIAGE_LIMIT    max /triage calls per UTC day across all clients (default 300)
"""
import hmac
import os
import threading
import time
from collections import defaultdict, deque
from pathlib import Path
from typing import Literal

import anthropic
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Header, HTTPException, Request
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from agent import triage_alert_agent
from triage import MODEL, Triage, load_alerts, triage_alert

load_dotenv()

app = FastAPI(title="SecTriage", version="0.1.0",
              description="AI security-alert triage with retrieval over a knowledge base.")


class AlertIn(BaseModel):
    timestamp: str = Field(max_length=64, examples=["2026-11-11T14:05:00Z"])
    source: str = Field(max_length=100, examples=["Windows Security"])
    host: str = Field(max_length=200)
    user: str = Field(max_length=200)
    title: str = Field(min_length=1, max_length=300)
    details: str = Field(min_length=1, max_length=4000)


class TriageRequest(BaseModel):
    alert: AlertIn
    mode: Literal["agent", "rag", "baseline"] = "agent"


class Search(BaseModel):
    query: str | None
    sources: list[str]


class TriageResponse(BaseModel):
    triage: Triage
    mode: str
    model: str
    searches: list[Search] = []
    retrieved_sources: list[str] = []


# ---- optional auth and rate limiting -------------------------------------------------

def require_token(x_api_key: str | None = Header(default=None)):
    token = os.getenv("TRIAGE_API_TOKEN")
    if token and not hmac.compare_digest(x_api_key or "", token):
        raise HTTPException(status_code=401, detail="Missing or invalid API key")


_hits: dict[str, deque] = defaultdict(deque)
_hits_lock = threading.Lock()


def rate_limit(request: Request):
    limit = int(os.getenv("RATE_LIMIT_PER_MIN", "10"))
    ip = request.client.host if request.client else "unknown"
    now = time.monotonic()
    with _hits_lock:
        q = _hits[ip]
        while q and now - q[0] > 60:
            q.popleft()
        if len(q) >= limit:
            raise HTTPException(status_code=429, detail="Rate limit exceeded; try again in a minute")
        q.append(now)


_daily = {"day": None, "count": 0}


def daily_cap():
    """Global ceiling on /triage calls per UTC day so a public deployment cannot run up a bill."""
    limit = int(os.getenv("DAILY_TRIAGE_LIMIT", "300"))
    today = time.strftime("%Y-%m-%d", time.gmtime())
    with _hits_lock:
        if _daily["day"] != today:
            _daily.update(day=today, count=0)
        if _daily["count"] >= limit:
            raise HTTPException(status_code=429, detail="Daily demo limit reached; try again tomorrow")
        _daily["count"] += 1


# ---- routes -----------------------------------------------------------------------

UI_FILE = Path(__file__).parent / "ui" / "index.html"
SAMPLE_SETS = {"hard": "data/alerts_hard.json", "original": "data/alerts.json"}


@app.get("/", include_in_schema=False)
def index():
    return FileResponse(UI_FILE)


@app.get("/health")
def health():
    return {"status": "ok", "model": MODEL, "auth_required": bool(os.getenv("TRIAGE_API_TOKEN"))}


@app.get("/samples")
def samples():
    """Demo alerts with their reference labels (the labels are never sent to the model)."""
    out = []
    for set_name, path in SAMPLE_SETS.items():
        for r in load_alerts(Path(__file__).parent / path):
            out.append({"id": r["id"], "set": set_name, "alert": r["alert"], "label": r["label"]})
    return out


@app.post("/triage", response_model=TriageResponse, dependencies=[Depends(require_token), Depends(rate_limit), Depends(daily_cap)])
def triage(req: TriageRequest):
    alert = req.alert.model_dump()
    try:
        if req.mode == "agent":
            result, trace = triage_alert_agent(alert)
            return TriageResponse(triage=result, mode=req.mode, model=MODEL, searches=trace,
                                  retrieved_sources=sorted({s for t in trace for s in t["sources"]}))
        result, chunks = triage_alert(alert, use_rag=req.mode == "rag")
        return TriageResponse(triage=result, mode=req.mode, model=MODEL,
                              retrieved_sources=sorted({c["source"] for c in chunks}))
    except anthropic.AuthenticationError:
        raise HTTPException(status_code=500, detail="Server is missing a valid Anthropic API key")
    except anthropic.RateLimitError:
        raise HTTPException(status_code=503, detail="Upstream model is rate limited; retry shortly")
    except anthropic.APIError:
        raise HTTPException(status_code=502, detail="Upstream model error")
    except RuntimeError as e:  # model never produced a valid decision
        raise HTTPException(status_code=502, detail=str(e)[:200])
