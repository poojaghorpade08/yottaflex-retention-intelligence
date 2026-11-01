from pathlib import Path
import sys
import pandas as pd
import streamlit as st
import plotly.express as px

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
st.set_page_config(page_title="YottaFlex Retention Intelligence", layout="wide")
st.title("YottaFlex | Retention Intelligence")
st.caption("Synthetic data • Supportive signals only • Human review required")

@st.cache_data
def load(name):
    path = RAW / name
    return pd.read_csv(path) if path.exists() else pd.DataFrame()

employees = load("employees.csv")
surveys = load("engagement_surveys.csv")
workload = load("workload_snapshots.csv")
outcomes = load("attrition_outcomes.csv")
interventions = load("interventions.csv")

if employees.empty:
    st.error("No data found. Run: python scripts/generate_data.py")
    st.stop()

attrition_rate = outcomes["voluntary_attrition"].mean() * 100 if not outcomes.empty else 0
c1,c2,c3,c4 = st.columns(4)
c1.metric("Synthetic employees", f"{len(employees):,}")
c2.metric("Survey responses", f"{len(surveys):,}")
c3.metric("Synthetic attrition rate", f"{attrition_rate:.1f}%")
c4.metric("Supportive interventions", f"{len(interventions):,}")

st.subheader("Engagement distribution")
if not surveys.empty:
    fig = px.histogram(surveys, x="engagement_score", nbins=20, title="Survey score distribution (0–100)")
    st.plotly_chart(fig, use_container_width=True)

st.subheader("Workload trend")
if not workload.empty:
    trend = workload.groupby("snapshot_date", as_index=False)["weekly_hours"].mean()
    fig = px.line(trend, x="snapshot_date", y="weekly_hours", markers=True, title="Average synthetic weekly hours")
    st.plotly_chart(fig, use_container_width=True)

st.subheader("Supportive follow-up queue")
if not interventions.empty:
    st.info("These are synthetic conversation prompts, not employee risk verdicts. A human must review context before any outreach.")
    st.dataframe(interventions.head(100), use_container_width=True)
else:
    st.write("No supportive follow-up events were generated.")

st.subheader("Data notes")
st.markdown("""
- Missing surveys are absent records and are not interpreted as negative engagement.
- Attrition labels are kept in a separate outcome table.
- Future outcome fields must never enter the feature set.
- No automated employment action is recommended.
""")
