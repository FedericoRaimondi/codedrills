#!/usr/bin/env python3
"""Validate CodeDrills challenge and topic JSON files.

Usage:
    python scripts/validate_json.py
"""

import json
import os
import sys

# ---------------------------------------------------------------------------
# Required keys
# ---------------------------------------------------------------------------
TOP_LEVEL_KEYS = {"language", "levels"}
LEVEL_KEYS = {"level"}
VALID_LEVELS = {"new", "beginner", "intermediate", "advanced"}

CHALLENGE_KEYS = {"id", "language", "level", "title", "description", "starterCode", "hint", "solution"}
AI_ML_CHALLENGE_KEYS = {"id", "language", "level", "title", "description", "choices", "hint", "solution"}
SOLUTION_KEYS = {"code", "steps"}
STEP_KEYS = {"title", "explanation"}
CHOICE_KEYS = {"text", "correct"}

TOPIC_KEYS = {"id", "language", "level", "title", "description", "estimatedMinutes", "lessons"}
LESSON_KEYS = {"title", "body"}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def err(path: str, msg: str) -> str:
    return f"  [{path}] {msg}"


def validate_challenge_file(path: str, data: dict) -> list[str]:
    errors: list[str] = []
    seen_ids: set[str] = set()
    top_language = data.get("language")

    for top_key in TOP_LEVEL_KEYS:
        if top_key not in data:
            errors.append(err(path, f"Missing top-level key: '{top_key}'"))

    if "levels" not in data:
        return errors  # can't proceed

    for level_idx, level_obj in enumerate(data["levels"]):
        level_prefix = f"levels[{level_idx}]"

        if "level" not in level_obj:
            errors.append(err(path, f"{level_prefix}: Missing 'level' key"))
            continue

        level_val = level_obj["level"]
        if level_val not in VALID_LEVELS:
            errors.append(err(path, f"{level_prefix}: Invalid level '{level_val}'. Must be one of {VALID_LEVELS}"))

        if "challenges" not in level_obj:
            errors.append(err(path, f"{level_prefix}: Missing 'challenges' array"))
            continue

        for ch_idx, challenge in enumerate(level_obj["challenges"]):
            ch_prefix = f"{level_prefix}.challenges[{ch_idx}]"
            required_keys = AI_ML_CHALLENGE_KEYS if top_language == "ai+ml" else CHALLENGE_KEYS

            for key in required_keys:
                if key not in challenge:
                    errors.append(err(path, f"{ch_prefix}: Missing required key '{key}'"))

            if top_language == "ai+ml" and "starterCode" in challenge:
                errors.append(err(path, f"{ch_prefix}: 'starterCode' is not valid for ai+ml challenges; use 'choices'"))

            if "language" in challenge and top_language and challenge["language"] != top_language:
                errors.append(err(path, f"{ch_prefix}: 'language' must match top-level language '{top_language}'"))

            if "level" in challenge and challenge["level"] != level_val:
                errors.append(err(path, f"{ch_prefix}: 'level' must match parent level '{level_val}'"))

            if "id" in challenge:
                cid = challenge["id"]
                if cid in seen_ids:
                    errors.append(err(path, f"{ch_prefix}: Duplicate id '{cid}'"))
                else:
                    seen_ids.add(cid)

            if top_language == "ai+ml" and "choices" in challenge:
                choices = challenge["choices"]
                if not isinstance(choices, list):
                    errors.append(err(path, f"{ch_prefix}.choices: Must be an array"))
                else:
                    if len(choices) != 4:
                        errors.append(err(path, f"{ch_prefix}.choices: Must contain exactly 4 answers"))

                    correct_count = 0
                    for choice_idx, choice in enumerate(choices):
                        choice_prefix = f"{ch_prefix}.choices[{choice_idx}]"
                        if not isinstance(choice, dict):
                            errors.append(err(path, f"{choice_prefix}: Must be an object"))
                            continue
                        for ck in CHOICE_KEYS:
                            if ck not in choice:
                                errors.append(err(path, f"{choice_prefix}: Missing key '{ck}'"))
                        if choice.get("correct") is True:
                            correct_count += 1

                    if correct_count != 1:
                        errors.append(err(path, f"{ch_prefix}.choices: Must contain exactly one correct answer"))

            if "solution" in challenge:
                sol = challenge["solution"]
                for sk in SOLUTION_KEYS:
                    if sk not in sol:
                        errors.append(err(path, f"{ch_prefix}.solution: Missing key '{sk}'"))
                if "steps" in sol:
                    for st_idx, step in enumerate(sol["steps"]):
                        for stk in STEP_KEYS:
                            if stk not in step:
                                errors.append(err(path, f"{ch_prefix}.solution.steps[{st_idx}]: Missing key '{stk}'"))

    return errors


def validate_topic_file(path: str, data: dict) -> list[str]:
    errors: list[str] = []
    seen_ids: set[str] = set()
    top_language = data.get("language")

    for top_key in TOP_LEVEL_KEYS:
        if top_key not in data:
            errors.append(err(path, f"Missing top-level key: '{top_key}'"))

    if "levels" not in data:
        return errors

    for level_idx, level_obj in enumerate(data["levels"]):
        level_prefix = f"levels[{level_idx}]"

        if "level" not in level_obj:
            errors.append(err(path, f"{level_prefix}: Missing 'level' key"))
            continue

        level_val = level_obj["level"]
        if level_val not in VALID_LEVELS:
            errors.append(err(path, f"{level_prefix}: Invalid level '{level_val}'. Must be one of {VALID_LEVELS}"))

        if "topics" not in level_obj:
            errors.append(err(path, f"{level_prefix}: Missing 'topics' array"))
            continue

        for tp_idx, topic in enumerate(level_obj["topics"]):
            tp_prefix = f"{level_prefix}.topics[{tp_idx}]"

            for key in TOPIC_KEYS:
                if key not in topic:
                    errors.append(err(path, f"{tp_prefix}: Missing required key '{key}'"))

            if "language" in topic and top_language and topic["language"] != top_language:
                errors.append(err(path, f"{tp_prefix}: 'language' must match top-level language '{top_language}'"))

            if "level" in topic and topic["level"] != level_val:
                errors.append(err(path, f"{tp_prefix}: 'level' must match parent level '{level_val}'"))

            if "id" in topic:
                tid = topic["id"]
                if tid in seen_ids:
                    errors.append(err(path, f"{tp_prefix}: Duplicate id '{tid}'"))
                else:
                    seen_ids.add(tid)

            if "lessons" in topic:
                for ls_idx, lesson in enumerate(topic["lessons"]):
                    lesson_prefix = f"{tp_prefix}.lessons[{ls_idx}]"
                    for lk in LESSON_KEYS:
                        if lk not in lesson:
                            errors.append(err(path, f"{lesson_prefix}: Missing key '{lk}'"))

                    if "image" in lesson and not isinstance(lesson["image"], str):
                        errors.append(err(path, f"{lesson_prefix}.image: Must be a string path"))

                    if top_language == "ai+ml" and "code" in lesson and lesson.get("runnable") is not False:
                        errors.append(err(path, f"{lesson_prefix}: ai+ml lessons with 'code' must set 'runnable' to false"))

    return errors


def collect_json_files(root: str) -> list[tuple[str, str]]:
    """Return (path, kind) pairs for all JSON files under challenges/ and topics/."""
    results: list[tuple[str, str]] = []
    for kind in ("challenges", "topics"):
        base = os.path.join(root, kind)
        if not os.path.isdir(base):
            continue
        for dirpath, _, filenames in os.walk(base):
            for fname in filenames:
                if fname.endswith(".json"):
                    results.append((os.path.join(dirpath, fname), kind.rstrip("s")))  # "challenge" / "topic"
    return results


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    files = collect_json_files(root)

    if not files:
        print("No JSON content files found under challenges/ or topics/.")
        return 0

    all_errors: list[str] = []

    for path, kind in files:
        rel = os.path.relpath(path, root)
        try:
            with open(path, encoding="utf-8") as fh:
                data = json.load(fh)
        except json.JSONDecodeError as exc:
            all_errors.append(err(rel, f"Invalid JSON: {exc}"))
            continue

        if kind == "challenge":
            file_errors = validate_challenge_file(rel, data)
        else:
            file_errors = validate_topic_file(rel, data)

        all_errors.extend(file_errors)

    if all_errors:
        print(f"Validation FAILED — {len(all_errors)} error(s) found:\n")
        for e in all_errors:
            print(e)
        return 1

    print(f"Validation PASSED — {len(files)} file(s) checked, no errors.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
