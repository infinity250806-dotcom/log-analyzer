import streamlit as st
from pymongo import MongoClient
import pandas as pd
import os

# ---------------- CONFIG ----------------
st.set_page_config(
    page_title="Log Analyzer",
    page_icon="📊",
    layout="wide"
)

# ---------------- CUSTOM CSS ----------------
st.markdown("""
<style>
.metric-card {
    background-color: #161b22;
    padding: 20px;
    border-radius: 10px;
    text-align: center;
}

.badge-error {
    color: white;
    background-color: #ff4b4b;
    padding: 5px 10px;
    border-radius: 8px;
}

.badge-info {
    color: white;
    background-color: #3b82f6;
    padding: 5px 10px;
    border-radius: 8px;
}

.badge-warning {
    color: black;
    background-color: #facc15;
    padding: 5px 10px;
    border-radius: 8px;
}
</style>
""", unsafe_allow_html=True)

# ---------------- DB CONNECTION ----------------
MONGO_URI = os.getenv("MONGO_URI")

client = MongoClient(MONGO_URI)

db = client["logdb"]
collection = db["logs"]

# ---------------- TITLE ----------------
st.markdown("<h1 style='text-align:center;'>📊 Big Data Log Analyzer</h1>", unsafe_allow_html=True)
st.markdown("---")

# ---------------- SIDEBAR ----------------
st.sidebar.header("⚙️ Controls")

mode = st.sidebar.selectbox(
    "Data Mode",
    ["Recent Logs (Fast)", "Full Data (Slow)"]
)

limit = st.sidebar.slider("Logs to Display", 100, 2000, 500)

levels = st.sidebar.multiselect(
    "Filter Levels",
    ["INFO", "WARNING", "ERROR"],
    default=["INFO", "WARNING", "ERROR"]
)

search = st.sidebar.text_input("Search logs")

# ---------------- LOAD DATA ----------------
if mode == "Full Data (Slow)":
    logs = list(collection.find())
else:
    logs = list(
        collection.find()
        .sort("timestamp", -1)
        .limit(limit)
    )

if not logs:
    st.warning("No logs found.")
    st.stop()

df = pd.DataFrame(logs)
df.drop(columns=["_id"], inplace=True)
df["timestamp"] = pd.to_datetime(df["timestamp"])

# ---------------- FILTER ----------------
filtered_df = df[df["level"].isin(levels)]

if search:
    filtered_df = filtered_df[
        filtered_df["message"].str.contains(search, case=False)
    ]

# ---------------- METRICS ----------------
st.subheader("📌 Overview")

total_logs = collection.count_documents({})
errors = total_logs and collection.count_documents({"level": "ERROR"})
warnings = total_logs and collection.count_documents({"level": "WARNING"})

col1, col2, col3 = st.columns(3)

col1.markdown(f"<div class='metric-card'><h2>{total_logs}</h2><p>Total Logs</p></div>", unsafe_allow_html=True)
col2.markdown(f"<div class='metric-card'><h2>{errors}</h2><p style='color:#ff4b4b;'>Errors</p></div>", unsafe_allow_html=True)
col3.markdown(f"<div class='metric-card'><h2>{warnings}</h2><p style='color:#facc15;'>Warnings</p></div>", unsafe_allow_html=True)

st.markdown("---")

# ---------------- CHART ----------------
st.subheader("📊 Log Distribution")

chart_data = filtered_df["level"].value_counts()
st.bar_chart(chart_data)

# ---------------- BADGE FUNCTION ----------------
def get_badge(level):
    if level == "ERROR":
        return "<span class='badge-error'>🚨 ERROR</span>"
    elif level == "WARNING":
        return "<span class='badge-warning'>⚠ WARNING</span>"
    else:
        return "<span class='badge-info'>INFO</span>"

# ---------------- LOG DISPLAY ----------------
st.subheader("📄 Logs")

for _, row in filtered_df.iterrows():
    badge = get_badge(row["level"])

    st.markdown(f"""
    <div style='background-color:#161b22; padding:15px; border-radius:10px; margin-bottom:10px;'>
        <b>{row['timestamp']}</b> {badge}  
        <br>{row['message']}
    </div>
    """, unsafe_allow_html=True)

# ---------------- TIME ANALYSIS ----------------
st.subheader("⏱ Activity Over Time")

time_df = filtered_df.copy()
time_df["hour"] = time_df["timestamp"].dt.hour

time_chart = time_df.groupby("hour").size()
st.line_chart(time_chart)

# ---------------- DOWNLOAD ----------------
st.markdown("---")

csv = filtered_df.to_csv(index=False)

st.download_button(
    label="📥 Download Logs as CSV",
    data=csv,
    file_name="logs.csv",
    mime="text/csv"
)

# ---------------- FOOTER ----------------
st.markdown("---")
st.markdown("<p style='text-align:center; color:gray;'>Big Data Log Analyzer • Streamlit + MongoDB</p>", unsafe_allow_html=True)