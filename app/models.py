from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class TokenUsage(BaseModel):
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0

class AIRunTrace(BaseModel):
    step_name: str
    status: str
    timestamp: datetime = Field(default_factory=datetime.now)
    details: Optional[str] = None

class AILogEntry(BaseModel):
    request_id: str
    timestamp: datetime = Field(default_factory=datetime.now)
    query: str
    response: Optional[str] = None
    error: Optional[str] = None
    error_type: Optional[str] = "None"
    latency_ms: float
    token_usage: TokenUsage
    trace: List[AIRunTrace] = []
    metadata: Dict[str, Any] = {}

class DebugSuggestion(BaseModel):
    request_id: str
    root_cause: str
    suggested_fix: str
    retry_strategy: str
    optimization_tip: str
