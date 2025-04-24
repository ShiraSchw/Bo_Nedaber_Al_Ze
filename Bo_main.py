import streamlit as st

from bo_function import registration_state, start_game, answering_state, guessing_state, results_state
from bo_utils import load_json, save_json
import random

# הגדרת נתיבים
QUESTIONS_FILE = 'bo_questions.json'
PLAYERS_FILE = 'bo_players.json'
GAME_STATE_FILE = 'bo_game_state.json'
ANSWERS_FILE = 'bo_answers.json'

# טעינת מצב קיים או יצירת חדש
questions = load_json(QUESTIONS_FILE)
players = load_json(PLAYERS_FILE)
game_state = load_json(GAME_STATE_FILE)
answers = load_json(ANSWERS_FILE)

# הגדרת שם משתמש
st.set_page_config(page_title="בוא נדבר על זה", layout="centered")
st.title("🎉 בוא נדבר על זה - משחק קבוצתי")

# כפתור לאיפוס המצב
if st.button("אפס את המשחק"):
    game_state = {"phase": "registration"}
    players.clear()
    answers.clear()
    save_json(game_state, GAME_STATE_FILE)
    save_json(players, PLAYERS_FILE)
    save_json(answers, ANSWERS_FILE)
    st.rerun()

# שלב הרשמה
if game_state.get("phase") == "registration":
    registration_state()

if len(players) >= 2:
    start_game()
    game_state["phase"] = "answering"

# שלב השאלות
if game_state.get("phase") == "answering":
    answering_state()

# שלב הניחושים
if game_state.get("phase") == "guessing":
    guessing_state()

# שלב הדירוג
if game_state.get("phase") == "rating":
    registration_state()

# תוצאות המשחק
if game_state.get("phase") == "results":
    results_state()


