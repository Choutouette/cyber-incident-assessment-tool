from datetime import datetime
from pathlib import Path

from fpdf import FPDF


class AssessmentReport(FPDF):
    """PDF document used for Cyber Incident Assessment Reports."""

    def __init__(self):
        super().__init__()

        self.set_auto_page_break(
            auto=True,
            margin=15
        )

        self.set_margins(
            left=15,
            top=15,
            right=15
        )

    def header(self):
        """Add a simple report header."""

        if self.page_no() > 1:
            self.set_font("Helvetica", "I", 8)
            self.cell(
                0,
                6,
                "Cyber Incident Assessment Report",
                align="R",
                new_x="LMARGIN",
                new_y="NEXT",
            )

            self.ln(2)

    def footer(self):
        """Add page numbering."""

        self.set_y(-12)

        self.set_font("Helvetica", "I", 8)

        self.cell(
            0,
            6,
            f"Page {self.page_no()}",
            align="C",
        )


def _safe_text(value):
    """
    Convert a value to safe printable text.
    """

    if value is None:
        return ""

    return str(value).replace("\r\n", "\n").replace("\r", "\n")


def _write_wrapped(pdf, text, size=10, height=5):
    """
    Write text safely using a wrapped multi-cell.
    """

    text = _safe_text(text)

    if not text:
        return

    pdf.set_font("Helvetica", "", size)

    pdf.multi_cell(
        0,
        height,
        text,
        new_x="LMARGIN",
        new_y="NEXT",
    )


def _write_heading(pdf, text, size=12):
    """Write a section heading."""

    pdf.set_font("Helvetica", "B", size)

    pdf.multi_cell(
        0,
        7,
        _safe_text(text),
        new_x="LMARGIN",
        new_y="NEXT",
    )

    pdf.ln(2)


def generate_report(
    scenario_title,
    scoring_result,
    questions,
    output_path,
):
    """
    Generate a Cyber Incident Assessment Report.

    The scoring engine remains responsible for calculating
    assessment results. This function only formats those
    results into a PDF.
    """

    if not isinstance(scoring_result, dict):
        raise ValueError(
            "scoring_result must be a dictionary."
        )

    if not isinstance(questions, list):
        raise ValueError(
            "questions must be provided as a list."
        )

    output_path = Path(output_path)

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    pdf = AssessmentReport()

    pdf.add_page()

    # =========================================================
    # TITLE
    # =========================================================

    pdf.set_font("Helvetica", "B", 18)

    pdf.multi_cell(
        0,
        10,
        "CYBER INCIDENT ASSESSMENT REPORT",
        align="C",
        new_x="LMARGIN",
        new_y="NEXT",
    )

    pdf.ln(5)

    # =========================================================
    # ASSESSMENT INFORMATION
    # =========================================================

    _write_heading(
        pdf,
        "Assessment Information",
    )

    assessment_date = datetime.now().strftime(
        "%d %B %Y, %H:%M"
    )

    pdf.set_font("Helvetica", "", 10)

    pdf.cell(
        0,
        6,
        f"Scenario: {_safe_text(scenario_title)}",
        new_x="LMARGIN",
        new_y="NEXT",
    )

    pdf.cell(
        0,
        6,
        f"Assessment Date: {assessment_date}",
        new_x="LMARGIN",
        new_y="NEXT",
    )

    pdf.ln(5)

    # =========================================================
    # SECTION 1 — ASSESSMENT RESULTS
    # =========================================================

    _write_heading(
        pdf,
        "1. Assessment Results",
    )

    total_questions = scoring_result.get(
        "total_questions",
        0
    )

    answered = scoring_result.get(
        "answered",
        0
    )

    unanswered = scoring_result.get(
        "unanswered",
        0
    )

    correct = scoring_result.get(
        "correct",
        0
    )

    incorrect = scoring_result.get(
        "incorrect",
        0
    )

    earned_points = scoring_result.get(
        "earned_points",
        0
    )

    maximum_points = scoring_result.get(
        "maximum_points",
        0
    )

    percentage = scoring_result.get(
        "percentage",
        0
    )

    readiness = scoring_result.get(
        "readiness",
        "Not available"
    )

    pdf.set_font("Helvetica", "", 10)

    result_lines = [
        f"Overall Score: {earned_points:g} / {maximum_points:g}",
        f"Percentage: {percentage:.1f}%",
        f"Readiness Level: {_safe_text(readiness)}",
        f"Questions Answered: {answered} / {total_questions}",
        f"Correct Answers: {correct}",
        f"Incorrect Answers: {incorrect}",
        f"Unanswered Questions: {unanswered}",
    ]

    for line in result_lines:
        pdf.cell(
            0,
            6,
            line,
            new_x="LMARGIN",
            new_y="NEXT",
        )

    pdf.ln(4)

    # =========================================================
    # OVERALL INTERPRETATION
    # =========================================================

    _write_heading(
        pdf,
        "Overall Interpretation",
        size=11,
    )

    if readiness == "Strong Cyber Readiness":

        interpretation = (
            "The assessment indicates a strong level of "
            "cyber readiness based on the responses provided."
        )

    elif readiness == "Moderate Cyber Readiness":

        interpretation = (
            "The assessment indicates a moderate level of "
            "cyber readiness. Some areas may require "
            "improvement."
        )

    else:

        interpretation = (
            "The assessment indicates that improvements "
            "are needed in the participant's handling of "
            "the simulated incident."
        )

    _write_wrapped(
        pdf,
        interpretation,
        size=10,
        height=6,
    )

    pdf.ln(5)

    # =========================================================
    # SECTION 2 — DETAILED FINDINGS
    # =========================================================

    _write_heading(
        pdf,
        "2. Detailed Findings",
    )

    answer_details = scoring_result.get(
        "answer_details",
        []
    )

    question_map = {
        question["id"]: question
        for question in questions
        if "id" in question
    }

    for number, detail in enumerate(
        answer_details,
        start=1,
    ):

        question_id = detail.get(
            "question_id"
        )

        question = question_map.get(
            question_id
        )

        if question is None:
            continue

        pdf.set_font(
            "Helvetica",
            "B",
            10,
        )

        _write_wrapped(
            pdf,
            f"Question {number}: "
            f"{question.get('question', '')}",
            size=10,
            height=5,
        )

        selected = detail.get(
            "selected_answer"
        )

        correct_answer = detail.get(
            "correct_answer"
        )

        options = question.get(
            "options",
            []
        )

        if selected is None:

            selected_text = "Not answered"

        elif 0 <= selected < len(options):

            selected_text = (
                f"{selected + 1}. "
                f"{options[selected]}"
            )

        else:

            selected_text = (
                "Invalid recorded answer"
            )

        if (
            isinstance(correct_answer, int)
            and 0 <= correct_answer < len(options)
        ):

            correct_text = (
                f"{correct_answer + 1}. "
                f"{options[correct_answer]}"
            )

        else:

            correct_text = (
                "Invalid correct-answer definition"
            )

        result_text = (
            "Correct"
            if detail.get("correct", False)
            else "Incorrect"
        )

        _write_wrapped(
            pdf,
            f"Selected Answer: {selected_text}",
            size=9,
            height=5,
        )

        _write_wrapped(
            pdf,
            f"Correct Answer: {correct_text}",
            size=9,
            height=5,
        )

        _write_wrapped(
            pdf,
            f"Result: {result_text}",
            size=9,
            height=5,
        )

        _write_wrapped(
            pdf,
            f"Points: "
            f"{detail.get('points_earned', 0)} / "
            f"{detail.get('points_available', 0)}",
            size=9,
            height=5,
        )

        feedback = question.get(
            "feedback"
        )

        if feedback:

            _write_wrapped(
                pdf,
                f"Feedback: {feedback}",
                size=9,
                height=5,
            )

        pdf.ln(4)

    # =========================================================
    # SECTION 3 — RECOMMENDATIONS
    # =========================================================

    _write_heading(
        pdf,
        "3. Recommended Improvements",
    )

    incorrect_questions = [
        detail
        for detail in answer_details
        if not detail.get("correct", False)
    ]

    if not incorrect_questions:

        _write_wrapped(
            pdf,
            "No incorrect responses were recorded. "
            "Continue maintaining the controls and "
            "practices demonstrated during the assessment.",
            size=10,
            height=6,
        )

    else:

        for detail in incorrect_questions:

            question_id = detail.get(
                "question_id"
            )

            question = question_map.get(
                question_id
            )

            if question is None:
                continue

            feedback = question.get(
                "feedback",
                "Review the area covered by this question.",
            )

            recommendation = (
                f"Question {question_id}: {feedback}"
            )

            _write_wrapped(
                pdf,
                f"- {recommendation}",
                size=9,
                height=5,
            )

    pdf.ln(6)

    # =========================================================
    # DISCLAIMER
    # =========================================================

    pdf.set_font(
        "Helvetica",
        "I",
        8,
    )

    pdf.multi_cell(
        0,
        5,
        (
            "This report is based on responses to a "
            "simulated cyber incident assessment. It "
            "should be interpreted as an assessment of "
            "the responses provided and not as confirmation "
            "of an actual security incident."
        ),
        new_x="LMARGIN",
        new_y="NEXT",
    )

    # =========================================================
    # SAVE
    # =========================================================

    pdf.output(str(output_path))