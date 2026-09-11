import json
from pathlib import Path

BASE_DIR = Path("data/scenarios")

SCENARIOS = {
    "fake_customer_alert": {
        "output": "fake_customer_alert.json",
        "attack_file": "fake_customer_alert/attack.json",
        "prevention_file": "fake_customer_alert/prevention.json",
        "forensics_file": "fake_customer_alert/forensics.json",
    },
    "malicious_invoice": {
        "output": "malicious_invoice.json",
        "attack_file": "malicious_invoice/attack.json",
        "prevention_file": "malicious_invoice/prevention.json",
        "forensics_file": "malicious_invoice/forensics.json",
    },
    "social_media_takeover": {
        "output": "social_media_takeover.json",
        "attack_file": "social_medi_takeover/attack.json",
        "prevention_file": "social_medi_takeover/prevention.json",
        "forensics_file": "social_medi_takeover/forensics.json",
    },
}


def load_json(path):
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def get_attack_questions(data):
    scenarios = data.get("scenarios", [])

    if not scenarios:
        raise ValueError("Attack file contains no scenarios.")

    questions = scenarios[0].get("questions", [])

    if len(questions) != 3:
        raise ValueError(
            f"Expected 3 attack questions, found {len(questions)}."
        )

    return questions


def get_prevention_questions(data):
    scenarios = data.get("scenarios", [])

    if not scenarios:
        raise ValueError("Prevention file contains no scenarios.")

    questions = scenarios[0].get("questions", [])

    if len(questions) != 4:
        raise ValueError(
            f"Expected 4 prevention questions, found {len(questions)}."
        )

    return questions


def get_forensic_questions(data):
    questions = data.get("questions", [])

    if len(questions) != 4:
        raise ValueError(
            f"Expected 4 forensic questions, found {len(questions)}."
        )

    return questions


def clean_question(question, stage_prefix):
    return {
        "id": f"{stage_prefix}_{question['id']}",
        "story": question["story"],
        "question": question["question"],
        "options": question["options"],
        "correct_answer": question["correct_answer"],
        "feedback": question["feedback"],
        "points": question.get("points", 1),
    }


def build_scenario(config):
    attack_data = load_json(BASE_DIR / config["attack_file"])
    prevention_data = load_json(BASE_DIR / config["prevention_file"])
    forensic_data = load_json(BASE_DIR / config["forensics_file"])

    attack_questions = get_attack_questions(attack_data)
    prevention_questions = get_prevention_questions(prevention_data)
    forensic_questions = get_forensic_questions(forensic_data)

    combined_questions = (
        [clean_question(q, "attack") for q in attack_questions]
        + [clean_question(q, "blue") for q in prevention_questions]
        + [clean_question(q, "forensics") for q in forensic_questions]
    )

    if len(combined_questions) != 11:
        raise ValueError(
            f"Combined scenario should contain 11 questions, "
            f"found {len(combined_questions)}."
        )

    question_ids = [q["id"] for q in combined_questions]

    if len(question_ids) != len(set(question_ids)):
        raise ValueError("Duplicate question IDs detected.")

    attack_scenario = attack_data["scenarios"][0]

    return {
        "id": attack_scenario["id"],
        "title": attack_scenario["title"],
        "attacker_objective": attack_scenario["attacker_objective"],
        "questions": combined_questions,
    }


def main():
    for scenario_name, config in SCENARIOS.items():
        output = build_scenario(config)

        output_path = BASE_DIR / config["output"]

        with open(output_path, "w", encoding="utf-8") as file:
            json.dump(output, file, indent=2, ensure_ascii=False)

        print(
            f"Created {output_path} "
            f"with {len(output['questions'])} questions."
        )


if __name__ == "__main__":
    main()