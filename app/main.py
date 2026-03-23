import os
import json
import uuid
from typing import List, Dict
from fastapi import FastAPI, HTTPException, Body
from app.models import AILogEntry, DebugSuggestion
from app.debugger import AIDebugger
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="AI Deployment Debugger API")

# Simple in-memory storage (upgrade to SQLite if needed)
LOGS_FILE = "database/logs.json"
os.makedirs("database", exist_ok=True)
if not os.path.exists(LOGS_FILE):
    with open(LOGS_FILE, "w") as f:
        json.dump([], f)

def save_log(entry: AILogEntry):
    with open(LOGS_FILE, "r") as f:
        data = json.load(f)
    data.append(entry.dict())
    # Keep only last 1000 logs for demo performance
    if len(data) > 1000:
        data = data[-1000:]
    with open(LOGS_FILE, "w") as f:
        json.dump(data, f, default=str)

@app.post("/log")
async def log_request(entry: AILogEntry):
    """
    Ingest a new AI request log with trace and token usage.
    """
    save_log(entry)
    return {"status": "logged", "request_id": entry.request_id}

@app.get("/logs", response_model=List[AILogEntry])
async def get_logs():
    with open(LOGS_FILE, "r") as f:
        return json.load(f)

@app.get("/metrics")
async def get_metrics():
    with open(LOGS_FILE, "r") as f:
        logs = json.load(f)
    
    if not logs:
        return {"avg_latency_ms": 0, "total_cost_tokens": 0, "total_cost_usd": 0, "failure_rate": 0, "total_requests": 0}

    total_latency = sum(l['latency_ms'] for l in logs)
    total_tokens = sum(l['token_usage']['total_tokens'] for l in logs)
    failures = sum(1 for l in logs if l['error'])
    
    return {
        "avg_latency_ms": int(total_latency / len(logs)),
        "total_cost_tokens": total_tokens,
        "total_cost_usd": total_tokens * 0.000002, # Estimated for gpt-4o-mini
        "failure_rate": round(failures / len(logs), 2),
        "total_requests": len(logs)
    }

@app.get("/debug/{request_id}", response_model=DebugSuggestion)
async def debug_failure(request_id: str):
    with open(LOGS_FILE, "r") as f:
        logs = json.load(f)
    
    entry = next((l for l in logs if l['request_id'] == request_id), None)
    if not entry:
        raise HTTPException(status_code=404, detail="Log entry not found")
    
    debugger = AIDebugger()
    suggestion = await debugger.analyze_failure(entry)
    return suggestion

@app.get("/health")
async def health():
    return {"status": "debugger-online"}
