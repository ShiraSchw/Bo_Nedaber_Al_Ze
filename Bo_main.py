import streamlit as st
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
    st.experimental_rerun()

# שלב הרשמה
if game_state.get("phase") == "registration":
    st.subheader("הרשמה למשחק")
    name = st.text_input("הכניסו שם משתמש כדי להצטרף למשחק")
    if st.button("הצטרף"):
        if name and name not in players:
            players.append(name)
            save_json(players, PLAYERS_FILE)
            st.success(f"{name}, הצטרפת למשחק!")
        elif name in players:
            st.warning("השם הזה כבר קיים. בחר/י שם אחר.")

    if len(players) > 1:
        if st.button("התחל משחק"):
            game_state["phase"] = "answering"
            game_state["current_question_index"] = 0
            game_state["scores"] = {player: 0 for player in players}
            game_state["ratings"] = {player: [] for player in players}
            save_json(game_state, GAME_STATE_FILE)
            st.experimental_rerun()

# שלב השאלות
elif game_state.get("phase") == "answering":
    st.subheader("שלב השאלות - כתבו את תשובתכם!")
    current_index = game_state.get("current_question_index", 0)

    if current_index < len(questions):
        question = questions[current_index]
        st.write(f"שאלה {current_index + 1} מתוך {len(questions)}:")
        st.markdown(f"### {question}")

        player_name = st.text_input("שם משתמש שלך:")
        answer = st.text_area("כתוב/כתבי את התשובה שלך (או השאר/י ריק בכוונה)")

        if st.button("שמור תשובה"):
            if player_name not in players:
                st.warning("השם שהזנת אינו מופיע ברשימת המשתתפים.")
            else:
                if question not in answers:
                    answers[question] = {}
                answers[question][player_name] = answer
                save_json(answers, ANSWERS_FILE)
                st.success("התשובה נשמרה!")

        if question in answers and len(answers[question]) == len(players):
            if st.button("עבור לשאלה הבאה"):
                game_state["current_question_index"] += 1
                save_json(game_state, GAME_STATE_FILE)
                st.experimental_rerun()
    else:
        st.success("סיימנו את שלב התשובות! המשחק האמיתי מתחיל עכשיו...")
        game_state["phase"] = "guessing"
        game_state["guess_index"] = 0
        game_state["guesses"] = {}
        save_json(game_state, GAME_STATE_FILE)
        st.experimental_rerun()

# שלב הניחושים
elif game_state.get("phase") == "guessing":
    st.subheader("שלב הניחושים - מי ענה את זה?")
    guess_index = game_state.get("guess_index", 0)
    if guess_index < len(questions):
        question = questions[guess_index]
        if question not in answers:
            st.warning("לא נמצאו תשובות לשאלה זו.")
        else:
            answer_mapping = answers[question]
            players_shuffled = list(answer_mapping.keys())
            random.shuffle(players_shuffled)

            selected_player = random.choice(players_shuffled)
            selected_answer = answer_mapping[selected_player]

            st.markdown(f"**שאלה:** {question}")
            st.markdown(f"**תשובה:** {selected_answer}")

            guesser_name = st.selectbox("בחר את שמך:", players)
            guess = st.radio("מי לדעתך ענה את התשובה?", players_shuffled)

            if st.button("שלח ניחוש"):
                if question not in game_state["guesses"]:
                    game_state["guesses"][question] = []

                game_state["guesses"][question].append({
                    "guesser": guesser_name,
                    "guess": guess,
                    "correct": guess == selected_player,
                    "answered_by": selected_player
                })
                save_json(game_state, GAME_STATE_FILE)
                st.success("הניחוש נשלח!")

            if st.button("עבור לניחוש הבא"):
                game_state["guess_index"] += 1
                save_json(game_state, GAME_STATE_FILE)
                st.experimental_rerun()
    else:
        st.success("סיימנו את שלב הניחושים! עכשיו נדרג את התשובות...")
        game_state["phase"] = "rating"
        game_state["rating_index"] = 0
        save_json(game_state, GAME_STATE_FILE)
        st.experimental_rerun()

# שלב הדירוג
elif game_state.get("phase") == "rating":
    st.subheader("שלב הדירוג - דרגו את התשובות!")
    rating_index = game_state.get("rating_index", 0)
    if rating_index < len(questions):
        question = questions[rating_index]
        if question not in answers:
            st.warning("אין תשובות לשאלה זו.")
        else:
            for player, answer in answers[question].items():
                st.markdown(f"**{player} ענה:** {answer}")
                rater = st.selectbox(f"מי אתה? (לדרוג תשובתו של {player})", players, key=f"rater_{player}")
                rating = st.slider("כמה אהבת את התשובה הזו?", 1, 10, key=f"rating_{player}")

                if st.button(f"שלח דירוג עבור {player}", key=f"btn_{player}"):
                    game_state["ratings"][player].append(rating)
                    save_json(game_state, GAME_STATE_FILE)
                    st.success("הדירוג נשמר!")

            if st.button("עבור לשאלה הבאה לדירוג"):
                game_state["rating_index"] += 1
                save_json(game_state, GAME_STATE_FILE)
                st.experimental_rerun()
    else:
        st.success("שלב הדירוג הסתיים! מחשבים את התוצאות...")
        game_state["phase"] = "results"
        save_json(game_state, GAME_STATE_FILE)
        st.experimental_rerun()

# תוצאות המשחק
elif game_state.get("phase") == "results":
    st.subheader("🎉 תוצאות המשחק 🎉")
    st.markdown("### ניחושים נכונים:")
    guess_scores = {player: 0 for player in players}
    for guesses in game_state.get("guesses", {}).values():
        for g in guesses:
            if g["correct"]:
                guess_scores[g["guesser"]] += 1
    for player, score in guess_scores.items():
        st.markdown(f"{player}: {score} ניחושים נכונים")

    st.markdown("### דירוגים ממוצעים:")
    avg_ratings = {player: (sum(r) / len(r)) if r else 0 for player, r in game_state["ratings"].items()}
    for player, avg in avg_ratings.items():
        st.markdown(f"{player}: {avg:.2f} דירוג ממוצע")

    winner_guess = max(guess_scores, key=guess_scores.get)
    winner_rating = max(avg_ratings, key=avg_ratings.get)

    st.success(f"🏆 המנצח בניחושים: {winner_guess}")
    st.success(f"🏆 המנצח בתשובות: {winner_rating}")
