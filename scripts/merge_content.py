#!/usr/bin/env python3
"""Merge all CodeDrills challenge and topic JSON files into single output files.

Each language-specific file is read, deduplicated by entry ``id``, and written
to ``output/challenges.json`` and/or ``output/lessons.json`` at the repository
root.

Deduplication rule: if an output file already exists, its entries are loaded
first and take priority.  New entries whose ``id`` already appears in the
existing output are silently skipped.

Usage:
    # Merge both challenges and lessons (default)
    python scripts/merge_content.py

    # Merge challenges only
    python scripts/merge_content.py --challenges

    # Merge lessons only
    python scripts/merge_content.py --lessons
"""

import argparse
import json
import os
import sys

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

OUTPUT_DIR = "output"
CHALLENGES_OUTPUT = "challenges.json"
LESSONS_OUTPUT = "lessons.json"
LEVELS = ["new", "beginner", "intermediate", "advanced"]

# ---------------------------------------------------------------------------
# JSON helpers
# ---------------------------------------------------------------------------


def load_json_or_exit(path: str) -> dict:
    """Load a JSON file and return its contents as a dict.

    Exits with an error message on invalid JSON.
    """
    with open(path, encoding="utf-8") as fh:
        try:
            return json.load(fh)
        except json.JSONDecodeError as exc:
            print(f"ERROR: Invalid JSON in '{path}': {exc}", file=sys.stderr)
            sys.exit(1)


def write_json(path: str, data: dict) -> None:
    """Create parent directories if needed, then write *data* as pretty-printed UTF-8 JSON."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)
        fh.write("\n")


# ---------------------------------------------------------------------------
# Collection helpers
# ---------------------------------------------------------------------------


def _iter_json_files(base_dir: str) -> list[str]:
    """Return sorted paths of all *.json files under *base_dir*."""
    paths: list[str] = []
    if not os.path.isdir(base_dir):
        return paths
    for dirpath, _, filenames in os.walk(base_dir):
        for fname in sorted(filenames):
            if fname.endswith(".json"):
                paths.append(os.path.join(dirpath, fname))
    return sorted(paths)


# ---------------------------------------------------------------------------
# Challenges
# ---------------------------------------------------------------------------


def merge_challenges(root: str, output_path: str) -> None:
    """Collect all challenges from ``challenges/`` and write *output_path*.

    Output is grouped by language and level:
    ``{"languages": [{"language": "...", "levels": [{"level": "...", "challenges": [...]}]}]}``

    If *output_path* already exists its entries are loaded first and take
    priority over the freshly read source files.
    """
    # existing_ids tracks all IDs seen so far for deduplication.
    existing_ids: set[str] = set()
    # lang_level_map: language -> level -> list[dict]
    lang_level_map: dict[str, dict[str, list[dict]]] = {}

    # Seed with existing output so existing IDs take priority.
    if os.path.isfile(output_path):
        existing = load_json_or_exit(output_path)
        count = 0
        for lang_obj in existing.get("languages", []):
            lang = lang_obj.get("language", "")
            if lang not in lang_level_map:
                lang_level_map[lang] = {lv: [] for lv in LEVELS}
            for level_obj in lang_obj.get("levels", []):
                lv = level_obj.get("level", "")
                for ch in level_obj.get("challenges", []):
                    cid = ch.get("id")
                    if cid and cid not in existing_ids:
                        lang_level_map[lang].setdefault(lv, []).append(ch)
                        existing_ids.add(cid)
                        count += 1
        print(f"  Loaded {count} existing challenge(s) from '{output_path}'.")

    added = 0
    skipped = 0
    challenges_dir = os.path.join(root, "challenges")
    for path in _iter_json_files(challenges_dir):
        data = load_json_or_exit(path)
        lang = data.get("language", "")
        if not lang:
            continue
        if lang not in lang_level_map:
            lang_level_map[lang] = {lv: [] for lv in LEVELS}
        for level_obj in data.get("levels", []):
            lv = level_obj.get("level", "")
            for ch in level_obj.get("challenges", []):
                cid = ch.get("id")
                if not cid:
                    continue
                if cid in existing_ids:
                    skipped += 1
                else:
                    lang_level_map[lang].setdefault(lv, []).append(ch)
                    existing_ids.add(cid)
                    added += 1

    # Build output structure.
    languages_list: list[dict] = []
    for lang in sorted(lang_level_map):
        levels_list: list[dict] = []
        for lv in LEVELS:
            levels_list.append(
                {
                    "level": lv,
                    "challenges": lang_level_map[lang].get(lv, []),
                }
            )
        languages_list.append({"language": lang, "levels": levels_list})

    output = {"languages": languages_list}
    write_json(output_path, output)
    total = sum(len(v) for m in lang_level_map.values() for v in m.values())
    print(
        f"  Challenges: {added} added, {skipped} duplicate(s) skipped. "
        f"Total: {total}. Saved to '{output_path}'."
    )


# ---------------------------------------------------------------------------
# Lessons (topics)
# ---------------------------------------------------------------------------


def merge_lessons(root: str, output_path: str) -> None:
    """Collect all topics from ``topics/`` and write *output_path*.

    Output is grouped by language and level:
    ``{"languages": [{"language": "...", "levels": [{"level": "...", "topics": [...]}]}]}``

    If *output_path* already exists its entries are loaded first and take
    priority over the freshly read source files.
    """
    existing_ids: set[str] = set()
    # lang_level_map: language -> level -> list[dict]
    lang_level_map: dict[str, dict[str, list[dict]]] = {}

    if os.path.isfile(output_path):
        existing = load_json_or_exit(output_path)
        count = 0
        for lang_obj in existing.get("languages", []):
            lang = lang_obj.get("language", "")
            if lang not in lang_level_map:
                lang_level_map[lang] = {lv: [] for lv in LEVELS}
            for level_obj in lang_obj.get("levels", []):
                lv = level_obj.get("level", "")
                for topic in level_obj.get("topics", []):
                    tid = topic.get("id")
                    if tid and tid not in existing_ids:
                        lang_level_map[lang].setdefault(lv, []).append(topic)
                        existing_ids.add(tid)
                        count += 1
        print(f"  Loaded {count} existing topic(s) from '{output_path}'.")

    added = 0
    skipped = 0
    topics_dir = os.path.join(root, "topics")
    for path in _iter_json_files(topics_dir):
        data = load_json_or_exit(path)
        lang = data.get("language", "")
        if not lang:
            continue
        if lang not in lang_level_map:
            lang_level_map[lang] = {lv: [] for lv in LEVELS}
        for level_obj in data.get("levels", []):
            lv = level_obj.get("level", "")
            for topic in level_obj.get("topics", []):
                tid = topic.get("id")
                if not tid:
                    continue
                if tid in existing_ids:
                    skipped += 1
                else:
                    lang_level_map[lang].setdefault(lv, []).append(topic)
                    existing_ids.add(tid)
                    added += 1

    # Build output structure.
    languages_list: list[dict] = []
    for lang in sorted(lang_level_map):
        levels_list: list[dict] = []
        for lv in LEVELS:
            levels_list.append(
                {
                    "level": lv,
                    "topics": lang_level_map[lang].get(lv, []),
                }
            )
        languages_list.append({"language": lang, "levels": levels_list})

    output = {"languages": languages_list}
    write_json(output_path, output)
    total = sum(len(v) for m in lang_level_map.values() for v in m.values())
    print(
        f"  Lessons: {added} added, {skipped} duplicate(s) skipped. "
        f"Total: {total}. Saved to '{output_path}'."
    )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Merge all CodeDrills challenge and/or topic JSON files into "
            "single deduplicated output files under the output/ directory."
        )
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--challenges",
        action="store_true",
        help="Merge challenge files only.",
    )
    group.add_argument(
        "--lessons",
        action="store_true",
        help="Merge lesson/topic files only.",
    )
    args = parser.parse_args()

    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_dir = os.path.join(root, OUTPUT_DIR)

    run_challenges = args.challenges or (not args.challenges and not args.lessons)
    run_lessons = args.lessons or (not args.challenges and not args.lessons)

    if run_challenges:
        print("Merging challenges...")
        merge_challenges(root, os.path.join(output_dir, CHALLENGES_OUTPUT))

    if run_lessons:
        print("Merging lessons...")
        merge_lessons(root, os.path.join(output_dir, LESSONS_OUTPUT))

    return 0


if __name__ == "__main__":
    sys.exit(main())
