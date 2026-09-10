import json
import streamlit as st


# -----------------------------
# Load scenario data
# -----------------------------
def load_scenario(scenario_id):
    scenario_path = f"data/scenarios/{scenario_id}/attack.json"

    with open(scenario_path, "r", encoding="utf-8") as file:
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
# Scenario options
# -----------------------------
SCENARIOS = {
    "Fake Customer Alert": "fake_customer_alert",
    "Malicious Invoice": "malicious_invoice",
    "Social Media Takeover": "social_medi_takeover"
}


# -----------------------------
# Session state
# -----------------------------
if "selected_scenario" not in st.session_state:
    st.session_state.selected_scenario = None

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
if not st.session_state.started:

    st.subheader("Choose an Incident Scenario")

    selected_name = st.selectbox(
        "Select a scenario category:",
        list(SCENARIOS.keys())
    )

    selected_id = SCENARIOS[selected_name]

    scenario = load_scenario(selected_id)

    st.session_state.selected_scenario = selected_id

    st.subheader(selected_name)

    st.write(
        "You will work through a simulated cyber incident "
        "and make decisions based on the information provided."
    )

    if st.button("Start Assessment", type="primary"):
        st.session_state.question_number = 0
        st.session_state.score = 0
        st.session_state.answers = []
        st.session_state.started = True
        st.rerun()



# -----------------------------
# Assessment
# -----------------------------
else:

    scenario = load_scenario(
        st.session_state.selected_scenario
    )

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