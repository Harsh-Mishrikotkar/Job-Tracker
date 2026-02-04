import re
from typing import Dict

# --- Positive role keywords ---
ROLE_KEYWORDS = [
    "analyst",
    "financial analyst",
    "finance analyst",
    "data analyst",
    "quant",
    "statistic",
    "statistics",
    "economics",
    "risk analyst",
]

# --- Entry-level / junior indicators ---
ENTRY_LEVEL_KEYWORDS = [
    "entry",
    "junior",
    "jr",
    "associate",
    "level i",
    "level 1",
    "new grad",
    "early career",
    "graduate",
]

# --- Strong exclusion keywords ---
EXCLUDE_KEYWORDS = [
    "senior",
    "sr",
    "lead",
    "principal",
    "manager",
    "director",
    "head",
    "staff",
    "vp",
    "vice president",
]

def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower().strip())

def is_relevant_job(job: Dict) -> bool:
    """
    Decide whether a job fits target criteria.
    Uses conservative filtering to avoid false positives.
    """
    title = normalize(job.get("title", ""))

    # Must contain at least one role keyword
    if not any(keyword in title for keyword in ROLE_KEYWORDS):
        return False

    # Must NOT contain senior/excluded terms
    if any(keyword in title for keyword in EXCLUDE_KEYWORDS):
        return False

    # Must indicate entry-level OR be neutral analyst role
    entry_signal = any(keyword in title for keyword in ENTRY_LEVEL_KEYWORDS)

    # Allow generic "Analyst" roles without senior signals
    if "analyst" in title and not entry_signal:
        return True

    return entry_signal
