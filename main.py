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
    """Create SQLite database and basic tables if they don't exist."""
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
            first_seen TEXT NOT NULL
        )
        """
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


def main():
    print("Job Tracker booting...")
    init_directories()
    init_db()

    companies = load_companies()
    print(f"Loaded {len(companies)} companies.")

    print("Environment OK. No fetching logic yet.")
    print(f"Last run: {datetime.now().isoformat()} UTC")


if __name__ == "__main__":
    main()
