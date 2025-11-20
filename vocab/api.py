import requests
import json
import os
from pathlib import Path

LOCAL = Path(__file__).parent / "local_words.json"

DICT_API = "https://api.dictionaryapi.dev/api/v2/entries/en/{}"

def load_local_words():
    try:
        with open(LOCAL, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("words", [])
    except Exception:
        return []

def fetch_definition(word, timeout=5):
    """Fetch definition and example from DictionaryAPI; fall back to local."""
    try:
        r = requests.get(DICT_API.format(word), timeout=timeout)
        if r.status_code == 200:
            j = r.json()
            # structure: [ { meanings: [ { definitions: [ { definition, example } ] } ] } ]
            meanings = j[0].get("meanings", [])
            defs = []
            example = None
            for m in meanings:
                for d in m.get("definitions", []):
                    defs.append(d.get("definition"))
                    if not example and d.get("example"):
                        example = d.get("example")
            return {"word": word, "definitions": defs, "example": example}
    except Exception:
        pass

    # fallback: search local
    for w in load_local_words():
        if w.get("word", "").lower() == word.lower():
            return {"word": w["word"], "definitions": w.get("definitions", []), "example": w.get("example")}

    return {"word": word, "definitions": [], "example": None}

def suggest_words(count=5, level="medium"):
    """Return a list of candidate words. Tries to use local DB first then random picks.
    level can be used to vary difficulty (simple heuristic)."""
    local = load_local_words()
    if not local:
        return []

    # simple difficulty mapping: easy -> first N, medium -> middle, hard -> last
    words = [w["word"] for w in local]
    if level == "easy":
        pool = words[: max(5, len(words)//3)]
    elif level == "hard":
        pool = words[-max(5, len(words)//3):]
    else:
        pool = words

    import random
    return random.sample(pool, min(count, len(pool)))
