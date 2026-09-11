from pathlib import Path

from src.report import generate_report


def create_questions():
    return [
        {
            "id": 1,
            "question": "What should you do?",
            "options": [
                "Ignore it",
                "Verify independently",
                "Click the link",
                "Share the password",
            ],
            "correct_answer": 1,
            "feedback": "Always verify suspicious payment requests independently.",
            "points": 1,
        },
        {
            "id": 2,
            "question": "What is the safest action?",
            "options": [
                "Open the attachment",
                "Forward it",
                "Verify the sender",
                "Delete all emails",
            ],
            "correct_answer": 2,
            "feedback": "Verify unexpected attachments using a trusted contact method.",
            "points": 1,
        },
        {
            "id": 3,
            "question": "What should be investigated?",
            "options": [
                "The suspicious login",
                "Nothing",
                "The customer's identity only",
                "The weather",
            ],
            "correct_answer": 0,
            "feedback": "Unexpected login activity should be investigated.",
            "points": 1,
        },
    ]


def create_result():
    return {
        "total_questions": 3,
        "answered": 3,
        "unanswered": 0,
        "correct": 2,
        "incorrect": 1,
        "earned_points": 2,
        "maximum_points": 3,
        "percentage": 66.7,
        "readiness": "Moderate Cyber Readiness",
        "answer_details": [
            {
                "question_id": 1,
                "selected_answer": 1,
                "correct_answer": 1,
                "correct": True,
                "answered": True,
                "points_earned": 1,
                "points_available": 1,
            },
            {
                "question_id": 2,
                "selected_answer": 0,
                "correct_answer": 2,
                "correct": False,
                "answered": True,
                "points_earned": 0,
                "points_available": 1,
            },
            {
                "question_id": 3,
                "selected_answer": 0,
                "correct_answer": 0,
                "correct": True,
                "answered": True,
                "points_earned": 1,
                "points_available": 1,
            },
        ],
    }


def test_report_is_created(tmp_path):
    questions = create_questions()
    result = create_result()

    output_file = tmp_path / "assessment_report.pdf"

    generate_report(
        scenario_title="Test Cyber Incident",
        scoring_result=result,
        questions=questions,
        output_path=output_file,
    )

    assert output_file.exists()
    assert output_file.stat().st_size > 0


def test_report_has_pdf_format(tmp_path):
    questions = create_questions()
    result = create_result()

    output_file = tmp_path / "assessment_report.pdf"

    generate_report(
        scenario_title="Test Cyber Incident",
        scoring_result=result,
        questions=questions,
        output_path=output_file,
    )

    with open(output_file, "rb") as file:
        header = file.read(4)

    assert header == b"%PDF"


def test_report_contains_expected_content(tmp_path):
    questions = create_questions()
    result = create_result()

    output_file = tmp_path / "assessment_report.pdf"

    generate_report(
        scenario_title="Test Cyber Incident",
        scoring_result=result,
        questions=questions,
        output_path=output_file,
    )

    assert output_file.exists()