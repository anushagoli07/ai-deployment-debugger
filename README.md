# 🛡️ AI Deployment Debugger

A "Datadog for AI" monitoring system that detects failures, classifies errors, and suggests LLM-powered fixes in real-time.

## 🏗️ Architecture Diagram
```mermaid
graph TD
    A[RAG App / AI Service] -->|@monitor.log_trace| B[Debugger API]
    B -->|Logs| C[JSON/SQLite DB]
    B -->|Failures| D[LLM Debugging Engine]
    D -->|RCA & Fixes| B
    E[Streamlit Dashboard] -->|Metrics & Trends| B
```

## 🚀 Key Features
- **One-Line Decorator**: Integrate in seconds using the `@monitor.log_trace` decorator.
- **Error Classification**: Automatically identifies `Timeout`, `Rate Limit`, `Hallucination`, and `Token Limit` errors.
- **AI-Powered RCA**: Uses GPT-4o to analyze failures and provide **Root Cause Analysis**, **Prompts Engineering Tips**, and **Retry Strategies**.
- **Interactive Trends**: Plotly-powered charts for monitoring Latency and Token usage trends.
- **Trace Dashboard**: Detailed step-by-step trace of every AI execution.

## 🛠️ Tech Stack
- **Backend**: FastAPI
- **Intelligence**: OpenAI API (GPS-4o-mini)
- **Frontend**: Streamlit + Plotly
- **SDK**: Python Functools / Requests

## 📦 Quick Start
1. Clone the repo:
   ```bash
   git clone https://github.com/anushagoli07/ai-deployment-debugger.git
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up `.env` with your `OPENAI_API_KEY`.

## 🏃 How to Run
1. **Start the API Server**:
   ```bash
   uvicorn app.main:app --port 8080
   ```
2. **Start the Dashboard**:
   ```bash
   streamlit run dashboard/app.py --server.port 8502
   ```

## 🧪 Simulation
You can test the debugger immediately without a real AI project by running:
```bash
python tests/simulate_ai_calls.py
```
This will seed the dashboard with a mix of successful and failed AI requests.
