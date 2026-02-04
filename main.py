import json
import sqlite3
from pathlib import Path
from datetime import datetime


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
CONFIG_DIR = BASE_DIR / "config"

DB_PATH = DATA_DIR / "job_cache.db"
COMPANIES_FILE = CONFIG_DIR / "companies.json"


def init_directories():
    """Ensure required directories exist."""
    DATA_DIR.mkdir(exist_ok=True)
    (DATA_DIR / "logs").mkdir(exist_ok=True)


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company TEXT NOT NULL,
            job_id TEXT NOT NULL,
            title TEXT NOT NULL,
            location TEXT,
            url TEXT,
            date_posted TEXT,
            first_seen TEXT NOT NULL,
            UNIQUE(company, job_id)
        )
        """
    )
    cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS runs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        run_timestamp TEXT NOT NULL,
        total_fetched INTEGER NOT NULL,
        total_matched INTEGER NOT NULL,
        total_rejected INTEGER NOT NULL,
        total_inserted INTEGER NOT NULL
    )
    """
)


    conn.commit()
    conn.close()

def record_run_stats(
    total_fetched: int,
    total_matched: int,
    total_rejected: int,
    total_inserted: int,
):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO runs (
            run_timestamp,
            total_fetched,
            total_matched,
            total_rejected,
            total_inserted
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            datetime.utcnow().isoformat(),
            total_fetched,
            total_matched,
            total_rejected,
            total_inserted,
        ),
    )

    conn.commit()
    conn.close()


def load_companies():
    """Load companies config."""
    if not COMPANIES_FILE.exists():
        raise FileNotFoundError(
            "companies.json not found. Create config/companies.json first."
        )

    with open(COMPANIES_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def insert_jobs(jobs):
    """
    Insert jobs into DB, ignoring duplicates.
    Returns number of new jobs inserted.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    inserted = 0

    for job in jobs:
        try:
            cursor.execute(
                """
                INSERT INTO jobs (
                    company, job_id, title, location, url, date_posted, first_seen
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    job["company"],
                    job["job_id"],
                    job["title"],
                    job["location"],
                    job["url"],
                    job["date_posted"],
                    job["first_seen"],
                ),
            )
            inserted += 1
        except sqlite3.IntegrityError:
            # Duplicate (company, job_id)
            continue

    conn.commit()
    conn.close()
    return inserted

from backend.fetchers.greenhouse import fetch_greenhouse_jobs
from backend.utils.job_filter import is_relevant_job


def main():
    print("Job Tracker starting...")
    init_directories()
    init_db()

    companies = load_companies()
    print(f"Loaded {len(companies)} companies.")

    total_new = 0

    total_fetched = 0
    total_matched = 0
    total_inserted = 0

    for company in companies:
        if company.get("ats") != "greenhouse":
            continue

        print(f"Fetching jobs for {company['name']} (Greenhouse)...")

        try:
            jobs = fetch_greenhouse_jobs(company)
            total_fetched += len(jobs)

            filtered_jobs = [job for job in jobs if is_relevant_job(job)]
            total_matched += len(filtered_jobs)

            inserted = insert_jobs(filtered_jobs)
            total_inserted += inserted

            print(
                f"  → {len(jobs)} fetched, "
                f"{len(filtered_jobs)} matched, "
                f"{inserted} new"
            )

        except Exception as e:
            print(f"  ❌ Failed for {company['name']}: {e}")

    total_rejected = total_fetched - total_matched

    record_run_stats(
        total_fetched=total_fetched,
        total_matched=total_matched,
        total_rejected=total_rejected,
        total_inserted=total_inserted,
    )

    print("\n📊 Run stats recorded")




if __name__ == "__main__":
    main()
