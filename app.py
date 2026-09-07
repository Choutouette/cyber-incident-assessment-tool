import json
import streamlit as st


# -----------------------------
# Load scenario data
# -----------------------------
def load_scenario():
    with open("data/scenarios/phishing.json", "r", encoding="utf-8") as file:
        return json.load(file)


# -----------------------------
# Page configuration
# -----------------------------
st.set_page_config(
    page_title="Cyber Incident Assessment Tool",
    page_icon="🛡️",
    layout="centered"
)


# -----------------------------
# Load data
# -----------------------------
scenario = load_scenario()


# -----------------------------
# Session state
# -----------------------------
if "question_number" not in st.session_state:
    st.session_state.question_number = 0

if "score" not in st.session_state:
    st.session_state.score = 0

if "answers" not in st.session_state:
    st.session_state.answers = []

if "started" not in st.session_state:
    st.session_state.started = False


# -----------------------------
# Home page
# -----------------------------
st.title("🛡️ Cyber Incident Assessment & Forensic Readiness Tool")

st.write(
    "A scenario-based training and assessment tool that helps "
    "small-scale online businesses understand cyber incidents, "
    "response and digital forensics."
)

st.info(
    "This tool uses simulated cyber incidents for training. "
    "Do not enter real passwords, PINs, OTPs or confidential information."
)


# # -----------------------------
# # Scenario selection
# # -----------------------------
# scenario_id = st.selectbox(
#     "Choose an incident scenario",
#     list(scenario.keys())
# )

# scenario = scenario[scenario_id]


if not st.session_state.started:

    st.subheader(scenario["title"])

    st.write(scenario["description"])

    if st.button("Start Assessment", type="primary"):
        st.session_state.started = True
        st.rerun()


# -----------------------------
# Assessment
# -----------------------------
else:

    questions = scenario["questions"]
    current = st.session_state.question_number

    # Assessment completed
    if current >= len(questions):

        st.success("Assessment completed!")

        st.subheader("Your Result")

        st.metric(
            "Total Score",
            f"{st.session_state.score} / {len(questions)}"
        )

        percentage = (
            st.session_state.score / len(questions)
        ) * 100

        st.write(f"Score: **{percentage:.1f}%**")

        if percentage >= 80:
            st.success("Strong Cyber Readiness")
        elif percentage >= 50:
            st.warning("Moderate Cyber Readiness")
        else:
            st.error("Needs Improvement")

        if st.button("Restart Assessment"):
            st.session_state.question_number = 0
            st.session_state.score = 0
            st.session_state.answers = []
            st.session_state.started = False
            st.rerun()

    else:

        question = questions[current]

        # Progress
        st.progress(
            (current + 1) / len(questions)
        )

        st.caption(
            f"Question {current + 1} of {len(questions)}"
        )

        # Stage
        st.markdown(
            f"**Assessment Area:** {question['category']}"
        )

        # Incident story
        st.subheader("Incident Update")

        st.write(question["story"])

        # Show simulated evidence when available
        if "evidence" in question:

            st.subheader("🔎 Simulated Evidence")

            for item in question["evidence"]:
                st.code(item)

        # Question
        st.subheader(question["question"])

        answer = st.radio(
            "Select your answer:",
            question["options"],
            key=f"question_{question['id']}"
        )

        if st.button("Submit Answer", type="primary"):

            selected_answer = question["options"].index(answer)

            correct = (
                selected_answer == question["correct_answer"]
            )

            if correct:
                st.session_state.score += question.get(
                    "points", 1
                )
                st.success("Correct!")

            else:
                st.error("Not quite.")

            st.info(question["feedback"])

            st.session_state.answers.append({
                "question_id": question["id"],
                "selected_answer": selected_answer,
                "correct": correct
            })

            st.session_state.question_number += 1

            st.button("Continue")
            st.rerun()