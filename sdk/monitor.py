import time
import uuid
import requests
import functools
from datetime import datetime
from typing import List, Dict, Any

class AIMonitor:
    def __init__(self, api_url: str = "http://localhost:8080/log"):
        self.api_url = api_url

    def log_trace(self, func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            request_id = str(uuid.uuid4())
            start_time = time.time()
            trace = [{"step_name": "Execution Started", "status": "OK", "timestamp": str(datetime.now())}]
            
            error = None
            error_type = "None"
            response_content = None
            token_usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}

            try:
                # Execute the actual AI function
                result = func(*args, **kwargs)
                response_content = str(result)
                trace.append({"step_name": f"Function {func.__name__} completed", "status": "OK", "timestamp": str(datetime.now())})
                
                # If the result has token usage (common in LangChain/OpenAI outputs)
                if isinstance(result, dict) and "usage" in result:
                    token_usage = result["usage"]
                elif hasattr(result, "response_metadata"):
                    meta = result.response_metadata
                    token_usage = meta.get("token_usage", token_usage)

                return result

            except Exception as e:
                error = str(e)
                error_type = self._classify_error(error)
                trace.append({"step_name": "Execution Failed", "status": "Error", "details": error, "timestamp": str(datetime.now())})
                raise e

            finally:
                latency = int((time.time() - start_time) * 1000)
                
                # Send telemetry payload to Debugger
                payload = {
                    "request_id": request_id,
                    "query": str(args[0]) if args else str(kwargs.get('query', 'Unknown')),
                    "response": response_content,
                    "error": error,
                    "error_type": error_type,
                    "latency_ms": latency,
                    "token_usage": token_usage,
                    "trace": trace
                }
                
                try:
                    requests.post(self.api_url, json=payload, timeout=2)
                except Exception:
                    print("Debugger Offline: Telemetry skipped.")

        return wrapper

    def _classify_error(self, error_msg: str) -> str:
        error_msg = error_msg.lower()
        if "timeout" in error_msg: return "Timeout"
        if "rate limit" in error_msg or "429" in error_msg: return "Rate Limit"
        if "context_length_exceeded" in error_msg: return "Token Limit"
        if "authentication" in error_msg or "api key" in error_msg: return "Auth Error"
        if "connection" in error_msg: return "Network Issue"
        return "Unknown Failure"

# Global instance for easy use
monitor = AIMonitor()
