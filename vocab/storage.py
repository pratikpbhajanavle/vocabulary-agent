import json
from pathlib import Path
from datetime import datetime, timedelta

DATA_DIR = Path(__file__).parent.parent / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
PROGRESS_FILE = DATA_DIR / "user_progress.json"

DEFAULT = {"user": {"name": "Learner", "points": 0, "streak": 0}, "words": {}}

def load_progress():
    if not PROGRESS_FILE.exists():
        save_progress(DEFAULT)
        return DEFAULT
    try:
        with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        save_progress(DEFAULT)
        return DEFAULT

def save_progress(data):
    with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def mark_seen(word, known=False):
    data = load_progress()
    w = data["words"].setdefault(word, {"seen":0, "correct":0, "incorrect":0, "interval":0, "next_review":None})
    w["seen"] = w.get("seen",0) + 1
    if known:
        w["correct"] = w.get("correct",0) + 1
        # simple spaced repetition: double interval
        w["interval"] = max(1, w.get("interval",0) * 2 or 1)
    else:
        w["incorrect"] = w.get("incorrect",0) + 1
        w["interval"] = 1

    # set next review date
    next_review = datetime.utcnow() + timedelta(days=w["interval"])
    w["next_review"] = next_review.isoformat()

    # user points and streak
    if known:
        data["user"]["points"] = data["user"].get("points",0) + 10
        data["user"]["streak"] = data["user"].get("streak",0) + 1
    else:
        data["user"]["streak"] = 0

    save_progress(data)
    return data

def get_due_words():
    data = load_progress()
    due = []
    now = datetime.utcnow()
    for w, info in data.get("words", {}).items():
        nr = info.get("next_review")
        if not nr:
            due.append(w)
        else:
            try:
                t = datetime.fromisoformat(nr)
                if t <= now:
                    due.append(w)
            except Exception:
                due.append(w)
    return due
