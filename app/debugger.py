import os
from openai import OpenAI
from app.models import AILogEntry, DebugSuggestion
from dotenv import load_dotenv

load_dotenv()

class AIDebugger:
    def __init__(self):
        self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

    async def analyze_failure(self, entry_dict: dict):
        """
        Uses LLM to analyze the root cause of a failure and suggest remediation.
        """
        query = entry_dict.get("query")
        response = entry_dict.get("response")
        error = entry_dict.get("error")
        error_type = entry_dict.get("error_type", "Unknown")
        latency = entry_dict.get("latency_ms")

        prompt = f"""
        You are an Expert AI Debugging Assistant. 
        Analyze the following failure in an AI-powered production system:

        [FAILURE DETAILS]
        Error Type: {error_type}
        Reported Error: {error}
        Original Query: {query}
        Raw Response: {response}
        Latency: {latency} ms

        [REQUIRED RESPONSE FORMAT]
        Provide your analysis in EXACTLY the following structure:
        Root Cause: <One sentence explanation>
        Suggested Fix: <Step by step action to fix>
        Retry Strategy: <How the system should retry this specific error>
        Optimization Tip: <How to prevent this in the future long-term>
        """

        try:
            completion = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1
            )
            analysis_text = completion.choices[0].message.content
            
            # Simple parsing of the structured response
            lines = analysis_text.split("\n")
            result = {
                "request_id": entry_dict["request_id"],
                "root_cause": self._extract_value(lines, "Root Cause:"),
                "suggested_fix": self._extract_value(lines, "Suggested Fix:"),
                "retry_strategy": self._extract_value(lines, "Retry Strategy:"),
                "optimization_tip": self._extract_value(lines, "Optimization Tip:")
            }
            return DebugSuggestion(**result)

        except Exception as e:
            return DebugSuggestion(
                request_id=entry_dict["request_id"],
                root_cause=f"Debugger failed to analyze: {str(e)}",
                suggested_fix="Check your OpenAI API connectivity.",
                retry_strategy="None",
                optimization_tip="N/A"
            )

    def _extract_value(self, lines, prefix):
        for line in lines:
            if line.startswith(prefix):
                return line.replace(prefix, "").strip()
        return "Not analyzed."
