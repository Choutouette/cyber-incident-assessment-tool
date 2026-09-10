from typing import Any


# Assessment readiness thresholds
STRONG_THRESHOLD = 80.0
MODERATE_THRESHOLD = 50.0


def validate_questions(questions: list[dict[str, Any]]) -> None:
    """
    Validate the structure of the assessment questions.

    Raises:
        ValueError: If the question data is invalid.
    """

    if not isinstance(questions, list):
        raise ValueError("Questions must be provided as a list.")

    if not questions:
        raise ValueError("The assessment contains no questions.")

    question_ids = set()

    for position, question in enumerate(questions, start=1):

        if not isinstance(question, dict):
            raise ValueError(
                f"Question {position} must be a dictionary."
            )

        # Question ID
        if "id" not in question:
            raise ValueError(
                f"Question {position} is missing an 'id'."
            )

        question_id = question["id"]

        if question_id in question_ids:
            raise ValueError(
                f"Duplicate question ID detected: {question_id}"
            )

        question_ids.add(question_id)

        # Options
        options = question.get("options")

        if not isinstance(options, list) or not options:
            raise ValueError(
                f"Question {question_id} must contain a non-empty "
                "'options' list."
            )

        # Correct answer
        if "correct_answer" not in question:
            raise ValueError(
                f"Question {question_id} is missing "
                "'correct_answer'."
            )

        correct_answer = question["correct_answer"]

        if not isinstance(correct_answer, int):
            raise ValueError(
                f"Question {question_id} has an invalid "
                "'correct_answer'. It must be an integer."
            )

        if not 0 <= correct_answer < len(options):
            raise ValueError(
                f"Question {question_id} has a correct answer "
                f"index outside the available options."
            )

        # Points
        points = question.get("points", 1)

        if not isinstance(points, (int, float)) or isinstance(points, bool):
            raise ValueError(
                f"Question {question_id} has an invalid points value."
            )

        if points <= 0:
            raise ValueError(
                f"Question {question_id} must have points greater than 0."
            )


def calculate_score(
    questions: list[dict[str, Any]],
    answers: dict[Any, int],
) -> dict[str, Any]:
    """
    Calculate the assessment score.

    The scoring engine independently compares each submitted answer
    against the correct answer stored in the question definition.

    Args:
        questions:
            List of assessment question dictionaries.

        answers:
            Dictionary mapping question IDs to selected option indexes.

    Returns:
        A dictionary containing the complete assessment result.
    """

    validate_questions(questions)

    if not isinstance(answers, dict):
        raise ValueError("Answers must be provided as a dictionary.")

    question_map = {
        question["id"]: question
        for question in questions
    }

    unknown_question_ids = set(answers) - set(question_map)

    if unknown_question_ids:
        raise ValueError(
            "Answers contain unknown question IDs: "
            f"{sorted(unknown_question_ids, key=str)}"
        )

    earned_points = 0.0
    maximum_points = 0.0
    correct_count = 0
    incorrect_count = 0
    unanswered_count = 0

    answer_details = []

    for question in questions:
        question_id = question["id"]
        correct_answer = question["correct_answer"]
        points = question.get("points", 1)

        maximum_points += points

        if question_id not in answers:
            unanswered_count += 1

            answer_details.append({
                "question_id": question_id,
                "selected_answer": None,
                "correct_answer": correct_answer,
                "correct": False,
                "answered": False,
                "points_earned": 0,
                "points_available": points,
            })

            continue

        selected_answer = answers[question_id]

        if not isinstance(selected_answer, int):
            raise ValueError(
                f"Answer for question {question_id} must be an integer."
            )

        options = question["options"]

        if not 0 <= selected_answer < len(options):
            raise ValueError(
                f"Answer for question {question_id} is outside "
                f"the available option range."
            )

        is_correct = selected_answer == correct_answer

        if is_correct:
            correct_count += 1
            earned_points += points
        else:
            incorrect_count += 1

        answer_details.append({
            "question_id": question_id,
            "selected_answer": selected_answer,
            "correct_answer": correct_answer,
            "correct": is_correct,
            "answered": True,
            "points_earned": points if is_correct else 0,
            "points_available": points,
        })

    total_questions = len(questions)
    answered_count = total_questions - unanswered_count

    percentage = (
        (earned_points / maximum_points) * 100
        if maximum_points > 0
        else 0.0
    )

    readiness = determine_readiness(percentage)

    return {
        "total_questions": total_questions,
        "answered": answered_count,
        "unanswered": unanswered_count,
        "correct": correct_count,
        "incorrect": incorrect_count,
        "earned_points": earned_points,
        "maximum_points": maximum_points,
        "percentage": round(percentage, 1),
        "readiness": readiness,
        "answer_details": answer_details,
    }


def determine_readiness(percentage: float) -> str:
    """
    Determine the overall cyber readiness level.
    """

    if not isinstance(percentage, (int, float)):
        raise ValueError("Percentage must be numeric.")

    if percentage < 0 or percentage > 100:
        raise ValueError("Percentage must be between 0 and 100.")

    if percentage >= STRONG_THRESHOLD:
        return "Strong Cyber Readiness"

    if percentage >= MODERATE_THRESHOLD:
        return "Moderate Cyber Readiness"

    return "Needs Improvement"