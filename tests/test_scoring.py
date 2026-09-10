import pytest
from src.scoring import calculate_score


def create_questions(number=15):
    """Create a simple 15-question test assessment."""

    return [
        {
            "id": i,
            "story": f"Test incident update {i}",
            "question": f"Test question {i}?",
            "options": [
                "Option A",
                "Option B",
                "Option C",
                "Option D",
            ],
            "correct_answer": 0,
            "points": 1,
        }
        for i in range(1, number + 1)
    ]


def test_all_answers_correct():
    questions = create_questions()

    answers = {
        question["id"]: 0
        for question in questions
    }

    result = calculate_score(questions, answers)

    assert result["correct"] == 15
    assert result["incorrect"] == 0
    assert result["unanswered"] == 0
    assert result["earned_points"] == 15
    assert result["maximum_points"] == 15
    assert result["percentage"] == 100.0
    assert result["readiness"] == "Strong Cyber Readiness"


def test_all_answers_wrong():
    questions = create_questions()

    answers = {
        question["id"]: 1
        for question in questions
    }

    result = calculate_score(questions, answers)

    assert result["correct"] == 0
    assert result["incorrect"] == 15
    assert result["unanswered"] == 0
    assert result["earned_points"] == 0
    assert result["percentage"] == 0.0
    assert result["readiness"] == "Needs Improvement"


def test_eighty_percent():
    questions = create_questions()

    answers = {
        question["id"]: (0 if question["id"] <= 12 else 1)
        for question in questions
    }

    result = calculate_score(questions, answers)

    assert result["correct"] == 12
    assert result["incorrect"] == 3
    assert result["percentage"] == 80.0
    assert result["readiness"] == "Strong Cyber Readiness"


def test_unanswered_questions():
    questions = create_questions()

    answers = {
        question["id"]: 0
        for question in questions[:10]
    }

    result = calculate_score(questions, answers)

    assert result["correct"] == 10
    assert result["incorrect"] == 0
    assert result["unanswered"] == 5
    assert result["answered"] == 10
    assert result["earned_points"] == 10
    assert result["percentage"] == 66.7
    assert result["readiness"] == "Moderate Cyber Readiness"


    import pytest
from src.scoring import calculate_score


def test_rejects_duplicate_question_ids():
    questions = create_questions()

    questions[1]["id"] = questions[0]["id"]

    with pytest.raises(ValueError, match="Duplicate question ID"):
        calculate_score(questions, {})


def test_rejects_invalid_correct_answer():
    questions = create_questions()

    questions[0]["correct_answer"] = 10

    with pytest.raises(ValueError, match="correct answer index"):
        calculate_score(questions, {})


def test_rejects_unknown_question_id():
    questions = create_questions()

    answers = {
        999: 0
    }

    with pytest.raises(ValueError, match="unknown question IDs"):
        calculate_score(questions, answers)


def test_rejects_invalid_selected_answer():
    questions = create_questions()

    answers = {
        1: 10
    }

    with pytest.raises(ValueError, match="outside the available option range"):
        calculate_score(questions, answers)


def test_rejects_invalid_points():
    questions = create_questions()

    questions[0]["points"] = 0

    with pytest.raises(ValueError, match="points greater than 0"):
        calculate_score(questions, {})


def test_rejects_missing_options():
    questions = create_questions()

    questions[0]["options"] = []

    with pytest.raises(ValueError, match="non-empty"):
        calculate_score(questions, {})


def test_rejects_missing_question_id():
    questions = create_questions()

    del questions[0]["id"]

    with pytest.raises(ValueError, match="missing an 'id'"):
        calculate_score(questions, {})


def test_moderate_readiness_boundary():
    questions = create_questions()

    # 7 correct out of 15 = 46.7%, should be Needs Improvement
    answers = {
        question["id"]: (0 if question["id"] <= 7 else 1)
        for question in questions
    }

    result = calculate_score(questions, answers)

    assert result["percentage"] == 46.7
    assert result["readiness"] == "Needs Improvement"


def test_fifty_percent_boundary():
    questions = create_questions(10)

    # 5/10 = exactly 50%
    answers = {
        question["id"]: (0 if question["id"] <= 5 else 1)
        for question in questions
    }

    result = calculate_score(questions, answers)

    assert result["percentage"] == 50.0
    assert result["readiness"] == "Moderate Cyber Readiness"


def test_strong_readiness_boundary():
    questions = create_questions(10)

    # 8/10 = exactly 80%
    answers = {
        question["id"]: (0 if question["id"] <= 8 else 1)
        for question in questions
    }

    result = calculate_score(questions, answers)

    assert result["percentage"] == 80.0
    assert result["readiness"] == "Strong Cyber Readiness"


def test_weighted_questions():
    questions = create_questions(3)

    questions[0]["points"] = 2
    questions[1]["points"] = 3
    questions[2]["points"] = 5

    answers = {
        1: 0,
        2: 0,
        3: 1
    }

    result = calculate_score(questions, answers)

    assert result["maximum_points"] == 10
    assert result["earned_points"] == 5
    assert result["percentage"] == 50.0
    assert result["correct"] == 2
    assert result["incorrect"] == 1