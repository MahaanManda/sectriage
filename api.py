"""FastAPI service for SecTriage.

POST /triage   triage one alert (mode: agent | rag | baseline)
GET  /health   liveness check

Optional protection for a public deployment (both read from the environment, never hard-coded):
  TRIAGE_API_TOKEN      if set, requests must send it in the X-API-Key header
  RATE_LIMIT_PER_MIN    max /triage calls per client IP per minute (default 10)
"""
import hmac
import os
import threading
import time
from collections import defaultdict, deque
from typing import Literal

import anthropic
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Header, HTTPException, Request
from pydantic import BaseModel, Field

from agent import triage_alert_agent
from triage import MODEL, Triage, triage_alert

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


# ---- routes -----------------------------------------------------------------------

@app.get("/health")
def health():
    return {"status": "ok", "model": MODEL}


@app.post("/triage", response_model=TriageResponse, dependencies=[Depends(require_token), Depends(rate_limit)])
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
