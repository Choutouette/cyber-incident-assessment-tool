import json
from datetime import datetime
from pathlib import Path

import streamlit as st

from src.scoring import calculate_score
from src.report import generate_report


# ---------------------------------------------------------
# PAGE CONFIGURATION
# ---------------------------------------------------------

st.set_page_config(
    page_title="Cyber Incident Assessment Tool",
    page_icon="🛡️",
    layout="centered",
)


# ---------------------------------------------------------
# SCENARIO FILES
# ---------------------------------------------------------

BASE_DIR = Path("data/scenarios")

SCENARIOS = {
    "Fake Customer Payment": "fake_customer_alert.json",
    "Malicious Invoice": "malicious_invoice.json",
    "Business Social Media Account Takeover": "social_media_takeover.json",
}


# ---------------------------------------------------------
# LOAD SCENARIO
# ---------------------------------------------------------

@st.cache_data
def load_scenario(filename):
    scenario_path = BASE_DIR / filename

    if not scenario_path.exists():
        raise FileNotFoundError(
            f"Scenario file not found: {scenario_path}"
        )

    with open(scenario_path, "r", encoding="utf-8") as file:
        return json.load(file)


# ---------------------------------------------------------
# SESSION STATE
# ---------------------------------------------------------

defaults = {
    "selected_scenario": None,
    "question_number": 0,
    "answers": {},
    "started": False,
    "assessment_started_at": None,
    "result": None,
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ---------------------------------------------------------
# RESET ASSESSMENT
# ---------------------------------------------------------

def reset_assessment():
    st.session_state.selected_scenario = None
    st.session_state.question_number = 0
    st.session_state.answers = {}
    st.session_state.started = False
    st.session_state.assessment_started_at = None
    st.session_state.result = None


# =========================================================
# START SCREEN
# =========================================================

if not st.session_state.started:

    st.title("🛡️ Cyber Incident Assessment Tool")

    st.write(
        "Work through a simulated cyber incident and make decisions "
        "based on the information provided."
    )

    st.subheader("Choose an Incident Scenario")

    selected_name = st.selectbox(
        "Select a scenario:",
        list(SCENARIOS.keys()),
    )

    scenario = load_scenario(
        SCENARIOS[selected_name]
    )

    st.subheader(
        scenario["title"]
    )

    st.write(
        "The assessment follows the incident as it develops. "
        "Read each incident update carefully and select the "
        "most appropriate answer."
    )

    if st.button(
        "Start Assessment",
        type="primary",
    ):

        st.session_state.selected_scenario = selected_name
        st.session_state.question_number = 0
        st.session_state.answers = {}
        st.session_state.result = None

        st.session_state.assessment_started_at = (
            datetime.now().isoformat(
                timespec="seconds"
            )
        )

        st.session_state.started = True

        st.rerun()


# =========================================================
# ASSESSMENT
# =========================================================

else:

    scenario = load_scenario(
        SCENARIOS[
            st.session_state.selected_scenario
        ]
    )

    questions = scenario["questions"]

    current = st.session_state.question_number


    # =====================================================
    # RESULTS PAGE
    # =====================================================

    if current >= len(questions):

        # -------------------------------------------------
        # CALCULATE SCORE
        # -------------------------------------------------

        if st.session_state.result is None:

            st.session_state.result = calculate_score(
                questions,
                st.session_state.answers,
            )

        result = st.session_state.result


        # -------------------------------------------------
        # TITLE
        # -------------------------------------------------

        st.title("Assessment Results")

        st.caption(
            scenario["title"]
        )


        # -------------------------------------------------
        # SCORE
        # -------------------------------------------------

        col1, col2 = st.columns(2)

        with col1:

            st.metric(
                "Overall Score",
                f"{result['earned_points']:.0f} / "
                f"{result['maximum_points']:.0f}",
            )

        with col2:

            st.metric(
                "Percentage",
                f"{result['percentage']:.1f}%",
            )


        # -------------------------------------------------
        # READINESS
        # -------------------------------------------------

        readiness = result["readiness"]

        if readiness == "Strong Cyber Readiness":

            st.success(
                f"### {readiness}\n\n"
                "The assessment indicates strong performance "
                "across the simulated incident."
            )

        elif readiness == "Moderate Cyber Readiness":

            st.warning(
                f"### {readiness}\n\n"
                "The assessment indicates moderate cyber readiness. "
                "Some areas may benefit from additional attention."
            )

        else:

            st.error(
                f"### {readiness}\n\n"
                "The assessment indicates areas requiring improvement. "
                "Review the findings and recommendations below."
            )


        # -------------------------------------------------
        # PERFORMANCE SUMMARY
        # -------------------------------------------------

        st.subheader(
            "Performance Summary"
        )

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "Questions",
                result["total_questions"],
            )

        with col2:
            st.metric(
                "Correct",
                result["correct"],
            )

        with col3:
            st.metric(
                "Incorrect",
                result["incorrect"],
            )

        with col4:
            st.metric(
                "Unanswered",
                result["unanswered"],
            )


        # -------------------------------------------------
        # PDF REPORT
        # -------------------------------------------------

        st.subheader("Assessment Report")

        try:

            report_dir = Path("outputs/reports")

            report_dir.mkdir(
                parents=True,
                exist_ok=True,
            )

            report_path = (
                report_dir
                / f"assessment_report_"
                f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            )

            generate_report(
                scenario["title"],
                result,
                questions,
                str(report_path),
            )

            # Read the generated PDF into memory
            with open(report_path, "rb") as pdf_file:
                pdf_data = pdf_file.read()

            st.download_button(
                label="📄 Download Assessment Report",
                data=pdf_data,
                file_name=report_path.name,
                mime="application/pdf",
                type="primary",
            )

        except Exception as error:

            st.error(
                f"Unable to generate the PDF report: {error}"
            )

        # -------------------------------------------------
        # FINDINGS & RECOMMENDATIONS
        # -------------------------------------------------

        st.subheader(
            "Findings & Recommendations"
        )

        st.caption(
            "Expand each question to review your answer "
            "and the assessment feedback."
        )

        for number, detail in enumerate(
            result["answer_details"],
            start=1,
        ):

            question_id = detail["question_id"]

            question = next(
                q
                for q in questions
                if q["id"] == question_id
            )


            # Determine status

            if detail["answered"]:

                if detail["correct"]:
                    status = "✓ Correct"
                else:
                    status = "✗ Incorrect"

            else:

                status = "— Unanswered"


            # Collapsible question

            with st.expander(
                f"Question {number} — {status}"
            ):

                st.write(
                    question["question"]
                )


                if detail["answered"]:

                    selected_text = question["options"][
                        detail["selected_answer"]
                    ]

                    correct_text = question["options"][
                        detail["correct_answer"]
                    ]

                    st.markdown(
                        f"**Your answer:** {selected_text}"
                    )

                    st.markdown(
                        f"**Correct answer:** {correct_text}"
                    )


                    if detail["correct"]:

                        st.success(
                            f"Correct — "
                            f"{detail['points_earned']} "
                            f"point earned."
                        )

                    else:

                        st.error(
                            "Incorrect."
                        )

                else:

                    st.warning(
                        "This question was not answered."
                    )


                st.info(
                    question["feedback"]
                )


        # -------------------------------------------------
        # START NEW ASSESSMENT
        # -------------------------------------------------

        st.divider()

        if st.button(
            "Start New Assessment",
            type="primary",
        ):

            reset_assessment()

            st.rerun()


    # =====================================================
    # QUESTION PAGE
    # =====================================================

    else:

        question = questions[current]


        # -------------------------------------------------
        # PROGRESS
        # -------------------------------------------------

        st.progress(
            (current + 1) / len(questions)
        )

        st.caption(
            f"Question {current + 1} of {len(questions)}"
        )


        # -------------------------------------------------
        # INCIDENT UPDATE
        # -------------------------------------------------

        st.subheader(
            "Incident Update"
        )

        st.write(
            question["story"]
        )


        # -------------------------------------------------
        # QUESTION
        # -------------------------------------------------

        st.subheader(
            question["question"]
        )

        answer = st.radio(
            "Select your answer:",
            question["options"],
            key=f"answer_{question['id']}",
        )


        # -------------------------------------------------
        # SUBMIT ANSWER
        # -------------------------------------------------

        if st.button(
            "Submit Answer",
            type="primary",
        ):

            selected_answer = (
                question["options"].index(answer)
            )

            st.session_state.answers[
                question["id"]
            ] = selected_answer

            st.session_state.question_number += 1

            st.rerun()