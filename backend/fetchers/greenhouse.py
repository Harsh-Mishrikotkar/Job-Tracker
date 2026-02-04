import requests
from datetime import datetime
from typing import List, Dict


GREENHOUSE_API = "https://boards-api.greenhouse.io/v1/boards/{board_token}/jobs"


def fetch_greenhouse_jobs(company: Dict) -> List[Dict]:
    """
    Fetch jobs from a Greenhouse job board.

    Required company fields:
    - name
    - board_token
    """
    board_token = company.get("board_token")
    company_name = company.get("name")

    if not board_token:
        raise ValueError(f"Missing board_token for {company_name}")

    url = GREENHOUSE_API.format(board_token=board_token)

    response = requests.get(url, timeout=15)
    response.raise_for_status()

    data = response.json()
    jobs = []

    for job in data.get("jobs", []):
        jobs.append(
            {
                "company": company_name,
                "job_id": str(job["id"]),
                "title": job["title"],
                "location": job["location"]["name"]
                if job.get("location")
                else None,
                "url": job["absolute_url"],
                "date_posted": job.get("updated_at"),
                "first_seen": datetime.utcnow().isoformat(),
            }
        )

    return jobs
