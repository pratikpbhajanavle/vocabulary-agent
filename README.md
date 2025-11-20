# Vocabulary Agent (Streamlit + Multi-Agent)

Local vocabulary learning app combining lightweight multi-agent modules with a Streamlit UI.

Features
- Generate sets of words on demand (5 words default)
- Rich content per word: definitions (from DictionaryAPI), examples, heuristics-based mnemonics
- Study, Quiz, and Review modes
- Progress tracking, simple spaced-review, gamification (points, streaks, badges)
- Offline fallback using a built-in local word database

Quick start

1. Create and activate a virtual environment (Windows PowerShell):

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

2. Optional: set environment variables in a `.env` file (e.g., `OPENAI_API_KEY`) if you plan to enable AI enhancements.

Notes
- The app uses the free Dictionary API at `https://api.dictionaryapi.dev/` to fetch definitions. If the API is unavailable, the app falls back to `vocab/local_words.json`.
- Multi-agent logic is implemented locally in `vocab/agents.py` to simulate generator, educator, quiz, and recommendation agents.

Files of interest
- `app.py` — Streamlit UI entry point
- `vocab/api.py` — fetches word data with offline fallback
- `vocab/agents.py` — content generation and quiz logic
- `vocab/storage.py` — user progress persistence
- `vocab/local_words.json` — offline word database

License
This project is provided as-is for educational use.
