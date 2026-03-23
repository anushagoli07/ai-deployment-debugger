import time
import random
from sdk.monitor import monitor

@monitor.log_trace
def ai_predict_loan_status(query: str):
    """
    Simulated AI function that sometimes fails or hangs.
    """
    print(f"Processing query: {query}")
    
    # Simulate random latency
    delay = random.uniform(0.5, 3.0)
    time.sleep(delay)
    
    # Simulate random failures
    outcome = random.random()
    
    if outcome < 0.2:
        raise Exception("OpenAI API Timeout Error (Simulated)")
    elif outcome < 0.4:
        raise Exception("Rate limit exceeded (429) - simulated")
    
    # Return a dummy response with usage metadata
    return {
        "status": "Approved",
        "reason": "Credit score > 750",
        "usage": {
            "prompt_tokens": random.randint(50, 200),
            "completion_tokens": random.randint(10, 50),
            "total_tokens": random.randint(60, 250)
        }
    }

if __name__ == "__main__":
    print("🚀 Starting AI Simulation...")
    queries = [
        "Should I approve user #123 with credit score 800?",
        "Status for user #999",
        "Check loan eligibility for new applicant",
        "Analyze risk for portfolio X"
    ]
    
    for q in queries:
        try:
            ai_predict_loan_status(q)
        except Exception as e:
            print(f"Captured expected failure for dashboard: {e}")
    
    print("✅ Simulation complete. Check your dashboard at http://localhost:8501")
