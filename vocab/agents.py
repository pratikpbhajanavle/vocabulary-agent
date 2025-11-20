from . import api
from .storage import load_progress
import random
from datetime import datetime

def generate_word_set(count=5, level="medium"):
    """Generator agent: select words (prefers due words)."""
    # prefer due words from progress
    progress = load_progress()
    due = []
    for w, info in progress.get("words", {}).items():
        nr = info.get("next_review")
        if not nr or datetime.fromisoformat(nr) <= datetime.utcnow():
            due.append(w)

    words = []
    for w in due:
        if len(words) >= count:
            break
        words.append(w)

    if len(words) < count:
        needed = count - len(words)
        suggestions = api.suggest_words(count=needed, level=level)
        # avoid duplicates
        for s in suggestions:
            if s not in words:
                words.append(s)

    # fetch full info
    info_list = []
    for w in words:
        info = api.fetch_definition(w)
        # educator agent will enrich
        info_list.append(enrich_word(info))
    return info_list

def enrich_word(info):
    """Educator agent: produce mnemonic and simplified examples if missing."""
    word = info.get("word")
    if not info.get("definitions"):
        info["definitions"] = ["(definition not available offline)"]

    if not info.get("example"):
        # create simple example using word in a sentence
        info["example"] = f"I used the word '{word}' in a sentence to demonstrate its meaning."

    if not info.get("mnemonic"):
        info["mnemonic"] = heuristic_mnemonic(word)

    return info

def heuristic_mnemonic(word):
    # simple heuristics: split into chunks or associations
    w = word.lower()
    if len(w) <= 5:
        return f"Think of '{w}' and a short phrase that reminds you of it."
    parts = [w[:len(w)//2], w[len(w)//2:]]
    return f"Split: {'-'.join(parts)} — build an image bridging the two."

def generate_quiz(items, num_questions=5):
    """Quiz agent: create multiple choice questions from items.
    items: list of word info dicts
    """
    questions = []
    pool_defs = {it["word"]: (it.get("definitions") or [""])[0] for it in items}
    words = [it["word"] for it in items]
    for i, it in enumerate(items[:num_questions]):
        correct = (it.get("definitions") or [""])[0]
        # distractors: sample other definitions or use variants
        distractors = []
        other_defs = [d for w,d in pool_defs.items() if w != it["word"]]
        random.shuffle(other_defs)
        for d in other_defs[:3]:
            distractors.append(d)

        # if not enough distractors, fabricate slight variants
        while len(distractors) < 3:
            distractors.append(f"Not quite: related idea for {it['word']}")

        options = [correct] + distractors
        random.shuffle(options)
        q = {
            "word": it["word"],
            "question": f"Which definition best fits '{it['word']}'?",
            "options": options,
            "answer": correct
        }
        questions.append(q)
    return questions

def recommend_next(progress, recent_words):
    """Recommendation agent: returns level and suggested count based on performance."""
    user = progress.get("user", {})
    points = user.get("points", 0)
    streak = user.get("streak", 0)
    # naive adaptation: increase difficulty as points increase
    if points < 100:
        level = "easy"
        count = 5
    elif points < 500:
        level = "medium"
        count = 6
    else:
        level = "hard"
        count = 8
    # reduce new words if many are due
    due_count = len([w for w in recent_words if progress.get("words", {}).get(w)])
    if due_count > 0:
        count = max(3, count - due_count)
    return {"level": level, "count": count}
