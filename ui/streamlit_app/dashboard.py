import sqlite3
from pathlib import Path
import pandas as pd
import streamlit as st

# Paths
BASE_DIR = Path(__file__).resolve().parents[2]
DB_PATH = BASE_DIR / "data" / "job_cache.db"

# Page Config
st.set_page_config(
    page_title="Job Tracker Dashboard",
    layout="wide"
)

st.title("Job Tracker Dashboard")

# DB Helpers 
def get_connection():
    return sqlite3.connect(DB_PATH)

def load_jobs():
    conn = get_connection()
    df = pd.read_sql_query(
        """
        SELECT
            company,
            title,
            location,
            url,
            date_posted,
            first_seen
        FROM jobs
        ORDER BY first_seen DESC
        """,
        conn
    )
    conn.close()
    return df
def load_run_stats():
    conn = get_connection()
    df = pd.read_sql_query(
        """
        SELECT
            run_timestamp,
            total_fetched,
            total_matched,
            total_rejected,
            total_inserted
        FROM runs
        ORDER BY run_timestamp DESC
        LIMIT 1
        """,
        conn
    )
    conn.close()
    return df

# UI 
st.subheader("Latest Run Summary")

try:
    stats_df = load_run_stats()

    if stats_df.empty:
        st.info("No run statistics available yet.")
    else:
        stats = stats_df.iloc[0]

        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Fetched", int(stats["total_fetched"]))
        col2.metric("Matched", int(stats["total_matched"]))
        col3.metric("Rejected", int(stats["total_rejected"]))
        col4.metric("Inserted", int(stats["total_inserted"]))

except Exception as e:
    st.error("Failed to load run statistics.")
    st.exception(e)


if not DB_PATH.exists():
    st.error("Database not found. Run main.py first.")
    st.stop()

st.subheader("All Tracked Jobs")

try:
    jobs_df = load_jobs()

    if jobs_df.empty:
        st.info("No jobs found yet. Run the job fetcher.")
    else:
        st.dataframe(
            jobs_df,
            use_container_width=True,
            hide_index=True
        )

except Exception as e:
    st.error("Failed to load jobs from database.")
    st.exception(e)

# Footer 
st.caption("Job Tracker • Local Dashboard")
