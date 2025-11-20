import streamlit as st
from vocab import agents, api
from vocab.storage import load_progress, mark_seen, get_due_words
from datetime import datetime

st.set_page_config(page_title="Vocabulary Agent", layout="wide")

def header():
    st.title("Vocabulary Agent — Learn Smarter")
    st.markdown("A small multi-agent vocabulary trainer with offline fallback and progress tracking.")

def sidebar_controls():
    st.sidebar.header("Settings & Profile")
    name = st.sidebar.text_input("Your name", value=load_progress().get("user", {}).get("name", "Learner"))
    if st.sidebar.button("Save profile"):
        p = load_progress(); p["user"]["name"] = name; __import__("vocab.storage").storage.save_progress(p)
    st.sidebar.markdown("---")
    mode = st.sidebar.selectbox("Mode", ["Study", "Quiz", "Review", "Dashboard"])    
    return mode

def study_mode():
    st.header("Study Mode")
    progress = load_progress()
    rec = agents.recommend_next(progress, [])
    cnt = st.number_input("Words per session", min_value=1, max_value=20, value=5)
    if st.button("Generate Words"):
        words = agents.generate_word_set(count=cnt, level=rec["level"])
        st.session_state["current_set"] = words

    words = st.session_state.get("current_set", [])
    if not words:
        st.info("Generate a set of words to start studying.")
        return

    idx = st.session_state.get("study_idx", 0)
    col1, col2 = st.columns([2,1])
    w = words[idx]
    with col1:
        st.subheader(w.get("word"))
        st.write("**Definition:**")
        for d in w.get("definitions", []):
            st.write(f"- {d}")
        st.write("**Example:**")
        st.write(w.get("example"))
        st.write("**Mnemonic:**")
        st.write(w.get("mnemonic"))
        if st.button("Mark Known"):
            mark_seen(w.get("word"), known=True)
            st.success("Marked as known — +10 points")
        if st.button("Mark Unknown"):
            mark_seen(w.get("word"), known=False)
            st.info("Marked for review")
    with col2:
        st.write("Session Progress")
        st.progress((idx+1)/len(words))
        if st.button("Prev"):
            st.session_state["study_idx"] = max(0, idx-1)
        if st.button("Next"):
            st.session_state["study_idx"] = min(len(words)-1, idx+1)

def quiz_mode():
    st.header("Quiz Mode")
    cnt = st.number_input("Questions", min_value=1, max_value=20, value=5)
    if st.button("Start Quiz"):
        words = agents.generate_word_set(count=cnt)
        st.session_state["quiz_questions"] = agents.generate_quiz(words, num_questions=cnt)
        st.session_state["quiz_idx"] = 0
        st.session_state["score"] = 0

    qs = st.session_state.get("quiz_questions", [])
    if not qs:
        st.info("Start a quiz to test yourself.")
        return

    idx = st.session_state.get("quiz_idx", 0)
    q = qs[idx]
    st.subheader(f"Q{idx+1}: {q['question']}")
    choice = st.radio("Options", q["options"])
    if st.button("Submit"):
        correct = choice == q["answer"]
        if correct:
            st.session_state["score"] += 1
            st.success("Correct!")
            mark_seen(q["word"], known=True)
        else:
            st.error(f"Incorrect — correct: {q['answer']}")
            mark_seen(q["word"], known=False)

        # advance
        st.session_state["quiz_idx"] = idx+1

    if st.session_state.get("quiz_idx",0) >= len(qs):
        st.info(f"Quiz complete — score: {st.session_state.get('score',0)}/{len(qs)}")
        st.session_state["quiz_questions"] = []

def review_mode():
    st.header("Review Mode")
    due = get_due_words()
    if not due:
        st.success("No words are due for review — great work!")
        return
    st.write(f"{len(due)} words due for review")
    for w in due:
        info = api.fetch_definition(w)
        st.subheader(w)
        for d in info.get("definitions", []):
            st.write(f"- {d}")
        st.write(info.get("example"))
        if st.button(f"Mark {w} Known"):
            mark_seen(w, known=True)

def dashboard_mode():
    st.header("Dashboard")
    p = load_progress()
    user = p.get("user", {})
    st.metric("Points", user.get("points",0))
    st.metric("Streak", user.get("streak",0))
    words = p.get("words", {})
    st.write(f"Tracked words: {len(words)}")
    if st.button("Show detailed progress"):
        st.json(p)

def main():
    header()
    mode = sidebar_controls()
    if mode == "Study":
        study_mode()
    elif mode == "Quiz":
        quiz_mode()
    elif mode == "Review":
        review_mode()
    elif mode == "Dashboard":
        dashboard_mode()

if __name__ == "__main__":
    main()
