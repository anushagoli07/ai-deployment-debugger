import streamlit as st
import requests
import pandas as pd
import time
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="AI Deployment Debugger", layout="wide")

st.title("🛡️ AI Deployment Debugger")
st.markdown("Monitor, Detect, and Fix production AI failures in real-time.")

BASE_URL = "http://localhost:8080"

# --- Metrics Section ---
def load_metrics():
    try:
        response = requests.get(f"{BASE_URL}/metrics")
        return response.json()
    except:
        return None

metrics = load_metrics()

if metrics:
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Requests", metrics.get('total_requests', 0))
    m2.metric("Avg Latency", f"{metrics.get('avg_latency_ms', 0)}ms")
    m3.metric("Total Cost (Est)", f"${metrics.get('total_cost_usd', 0):.4f}")
    m4.metric("Failure Rate", f"{metrics.get('failure_rate', 0)*100}%", delta_color="inverse")

# --- Logs View ---
st.divider()
st.subheader("📋 Request Logs & Traces")

def load_logs():
    try:
        return requests.get(f"{BASE_URL}/logs").json()
    except:
        return []

logs = load_logs()

if logs:
    df = pd.DataFrame(logs)
    # Highlight failures
    def highlight_errors(val):
        color = 'red' if val and val != "None" else 'green'
        return f'background-color: {color}; color: white'

    st.dataframe(df[['timestamp', 'request_id', 'query', 'error_type', 'latency_ms']], use_container_width=True)

    # --- Debugger Detail View ---
    st.divider()
    selected_id = st.selectbox("Select a Request to Debug / Analyze Trace", [l['request_id'] for l in logs])
    
    if selected_id:
        log = next(l for l in logs if l['request_id'] == selected_id)
        
        c1, c2 = st.columns(2)
        with c1:
            st.info("**Request Metadata**")
            st.json(log)
        
        with c2:
            st.warning("**Trace View**")
            for step in log['trace']:
                status_icon = "✅" if step['status'] == "OK" else "❌"
                st.write(f"{status_icon} **{step['step_name']}** at {step['timestamp']}")
                if step.get('details'):
                    st.code(step['details'])

        # --- AI Fix Implementation ---
        if log['error']:
            if st.button("🧠 Generate AI Fix Strategy"):
                with st.spinner("Analyzing Root Cause..."):
                    res = requests.get(f"{BASE_URL}/debug/{selected_id}")
                    if res.status_code == 200:
                        fix = res.json()
                        st.success("### AI Analysis Ready")
                        st.write(f"**Root Cause:** {fix['root_cause']}")
                        st.write(f"**Suggested Fix:** {fix['suggested_fix']}")
                        st.write(f"**Retry Strategy:** {fix['retry_strategy']}")
                        st.write(f"**Optimization:** {fix['optimization_tip']}")
                    else:
                        st.error("Failed to generate analysis.")
else:
    st.write("No logs found. Start your AI apps with the @monitor decorator!")

if st.button("🔄 Refresh Data"):
    st.rerun()
