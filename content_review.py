"""Local Streamlit editor for CodeDrills lesson and challenge source JSON."""

from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import streamlit as st

ROOT = Path(__file__).parent
STATE_PATH = ROOT / ".content-review-state.json"
LEVELS = ("new", "beginner", "intermediate", "advanced")
CODE_LANGUAGES = {
    "ai+ml": "python",
    "javascript": "javascript",
    "python": "python",
    "rust": "rust",
    "sql": "sql",
}


def field_label(label: str) -> str:
    return label.replace("_", " ").replace("-", " ").title()


def inject_styles() -> None:
    palette = {
        "canvas": "#121914",
        "surface": "#1c2820",
        "control": "#26352c",
        "ink": "#eff7f0",
        "muted": "#bdcbbf",
        "line": "#3a4c40",
        "mint": "#1c5138",
        "green": "#84e0ae",
        "sun": "#5c4b16",
        "warning": "#ffdf75",
        "code": "#0d130f",
        "active-ink": "#0b2013",
    }
    st.markdown(
        """
        <style>
        :root {
            --canvas: __CANVAS__;
            --surface: __SURFACE__;
            --control: __CONTROL__;
            --ink: __INK__;
            --muted: __MUTED__;
            --line: __LINE__;
            --mint: __MINT__;
            --green: __GREEN__;
            --sun: __SUN__;
            --warning: __WARNING__;
            --code: __CODE__;
            --active-ink: __ACTIVE_INK__;
        }
        .stApp { background: var(--canvas); color: var(--ink); }
        .block-container { max-width: 1440px; padding-top: 2rem; padding-bottom: 3rem; }
        h1, h2, h3 { color: var(--ink); letter-spacing: 0 !important; }
        h1 { font-size: 2rem !important; margin-bottom: 0.15rem !important; }
        p, label, [data-testid="stMarkdownContainer"] { color: var(--ink); }
        [data-testid="stCaptionContainer"], [data-testid="stMetricLabel"] { color: var(--muted) !important; }
        [data-testid="stSidebar"] { background: var(--surface); border-right: 1px solid var(--line); }
        [data-testid="stSidebar"] > div:first-child { padding-top: 1.5rem; }
        [data-testid="stMetric"] { background: var(--control); border: 1px solid var(--line); border-radius: 6px; padding: 0.8rem 1rem; }
        [data-testid="stMetricValue"] { color: var(--ink); }
        [data-testid="stSelectbox"] > div > div,
        [data-testid="stTextArea"] textarea,
        [data-testid="stNumberInput"] input { background: var(--control); color: var(--ink); border-color: var(--line); }
        [data-testid="stSelectbox"] [role="combobox"], [data-testid="stSelectbox"] [role="combobox"] * { color: var(--ink) !important; opacity: 1 !important; }
        [data-testid="stTextArea"] textarea::placeholder { color: var(--muted); }
        [data-baseweb="select"] > div { background: var(--control); border-color: var(--line); color: var(--ink); }
        [data-baseweb="select"] *, [data-baseweb="select"] svg { color: var(--ink) !important; fill: var(--ink) !important; }
        [role="radiogroup"] button[role="radio"] { background: var(--control); border: 1px solid var(--line); color: var(--ink) !important; }
        [role="radiogroup"] button[role="radio"] * { color: var(--ink) !important; }
        [role="radiogroup"] button[role="radio"][aria-checked="true"] { background: var(--green); border-color: var(--green); }
        [role="radiogroup"] button[role="radio"][aria-checked="true"] * { color: var(--active-ink) !important; }
        .review-kicker { color: var(--green); font-size: 0.8rem; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase; }
        .review-meta { color: var(--muted); font-size: 0.9rem; }
        .status-pill { display: inline-block; background: var(--mint); color: var(--green); border-radius: 999px; font-size: 0.78rem; font-weight: 700; padding: 0.28rem 0.65rem; }
        .status-pill.pending { background: var(--sun); color: var(--warning); }
        [data-testid="stExpander"] { border: 1px solid var(--line); border-radius: 6px; background: var(--surface); }
        [data-testid="stTabs"] button { font-weight: 650; }
        [data-testid="stTabs"] button[aria-selected="true"] { color: var(--green); }
        [data-testid="stCodeBlock"] { border: 1px solid var(--line); border-radius: 6px; }
        [data-testid="stCodeBlock"] pre { background: var(--code); }
        .stButton > button { border-radius: 5px; font-weight: 650; min-height: 2.5rem; }
        button[data-testid="stBaseButton-secondary"] { background: var(--control); border-color: var(--line); color: var(--ink) !important; }
        button[data-testid="stBaseButton-secondary"] * { color: var(--ink) !important; }
        button[data-testid="stBaseButton-primary"] { background: var(--green); border-color: var(--green); color: var(--active-ink) !important; }
        button[data-testid="stBaseButton-primary"] * { color: var(--active-ink) !important; }
        textarea { line-height: 1.5 !important; }
        </style>
        """.replace("__CANVAS__", palette["canvas"])
        .replace("__SURFACE__", palette["surface"])
        .replace("__CONTROL__", palette["control"])
        .replace("__INK__", palette["ink"])
        .replace("__MUTED__", palette["muted"])
        .replace("__LINE__", palette["line"])
        .replace("__MINT__", palette["mint"])
        .replace("__GREEN__", palette["green"])
        .replace("__SUN__", palette["sun"])
        .replace("__WARNING__", palette["warning"])
        .replace("__CODE__", palette["code"])
        .replace("__ACTIVE_INK__", palette["active-ink"]),
        unsafe_allow_html=True,
    )


def load_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as source:
        return json.load(source)


def write_json(path: Path, data: dict[str, Any]) -> None:
    temporary_path = path.with_suffix(".tmp")
    with temporary_path.open("w", encoding="utf-8") as target:
        json.dump(data, target, ensure_ascii=False, indent=2)
        target.write("\n")
    temporary_path.replace(path)


def load_review_state() -> dict[str, set[str]]:
    if not STATE_PATH.exists():
        return {"lessons": set(), "challenges": set()}
    try:
        data = load_json(STATE_PATH)
    except json.JSONDecodeError:
        return {"lessons": set(), "challenges": set()}
    return {
        "lessons": set(data.get("lessons", [])),
        "challenges": set(data.get("challenges", [])),
    }


def write_review_state(state: dict[str, set[str]]) -> None:
    write_json(STATE_PATH, {kind: sorted(ids) for kind, ids in state.items()})


def content_files(kind: str) -> list[Path]:
    directory = ROOT / ("topics" if kind == "lessons" else "challenges")
    return sorted(directory.rglob("*.json"))


def collect_entries(kind: str) -> list[dict[str, Any]]:
    collection_key = "topics" if kind == "lessons" else "challenges"
    entries: list[dict[str, Any]] = []
    for source_path in content_files(kind):
        document = load_json(source_path)
        language = document.get("language", source_path.parent.name)
        for level_data in document.get("levels", []):
            for entry in level_data.get(collection_key, []):
                entries.append(
                    {
                        "id": entry.get("id", ""),
                        "title": entry.get("title", "Untitled"),
                        "level": level_data.get("level", ""),
                        "language": language,
                        "path": source_path,
                        "entry": entry,
                    }
                )
    return entries


def replace_entry(
    kind: str, selected: dict[str, Any], replacement: dict[str, Any]
) -> None:
    document = load_json(selected["path"])
    collection_key = "topics" if kind == "lessons" else "challenges"
    for level_data in document["levels"]:
        for index, entry in enumerate(level_data.get(collection_key, [])):
            if entry.get("id") == selected["id"]:
                level_data[collection_key][index] = replacement
                write_json(selected["path"], document)
                return
    raise ValueError(f"Could not find {selected['id']} in {selected['path']}")


def validate_source() -> tuple[bool, str]:
    result = subprocess.run(
        [sys.executable, "scripts/validate_json.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    return result.returncode == 0, result.stdout + result.stderr


def editor(value: Any, label: str, key_prefix: str, language: str) -> Any:
    """Render editable JSON values while preserving their original types."""
    if isinstance(value, str):
        height = 180 if label in {"body", "description", "code"} else 90
        edited = st.text_area(
            field_label(label), value=value, key=f"{key_prefix}-{label}", height=height
        )
        if label == "image" and edited:
            image_path = ROOT / edited
            if image_path.is_file():
                st.image(str(image_path), caption=edited)
            else:
                st.caption(f"Image path: {edited} (file not found)")
        if label == "code":
            st.code(edited, language=CODE_LANGUAGES.get(language, "text"))
        return edited
    if isinstance(value, bool):
        return st.checkbox(field_label(label), value=value, key=f"{key_prefix}-{label}")
    if isinstance(value, int | float):
        return st.number_input(
            field_label(label), value=value, key=f"{key_prefix}-{label}"
        )
    if isinstance(value, list):
        edited_items = []
        for index, item in enumerate(value):
            with st.expander(f"{label} {index + 1}", expanded=True):
                edited_items.append(
                    editor(
                        item, f"{label} {index + 1}", f"{key_prefix}-{index}", language
                    )
                )
        return edited_items
    if isinstance(value, dict):
        edited_values: dict[str, Any] = {}
        if "code" in value:
            status = "Runnable" if value.get("runnable") else "Not runnable"
            st.caption(f"Snippet status: {status}")
        for field, item in value.items():
            if isinstance(item, (dict, list)):
                with st.expander(field.replace("_", " ").title(), expanded=True):
                    edited_values[field] = editor(
                        item, field, f"{key_prefix}-{field}", language
                    )
            else:
                edited_values[field] = editor(
                    item, field, f"{key_prefix}-{field}", language
                )
        return edited_values
    return value


def filtered_entries(
    entries: list[dict[str, Any]],
    reviewed_ids: set[str],
    language: str,
    level: str,
    topic: str,
    section: str,
) -> list[dict[str, Any]]:
    results = []
    for item in entries:
        if language != "All" and item["language"] != language:
            continue
        if level != "All" and item["level"] != level:
            continue
        if topic != "All" and item["title"] != topic:
            continue
        is_reviewed = item["id"] in reviewed_ids
        if section == "To review" and is_reviewed:
            continue
        if section == "Reviewed" and not is_reviewed:
            continue
        results.append(item)
    return results


def main() -> None:
    st.set_page_config(page_title="CodeDrills Content Review", layout="wide")
    inject_styles()
    st.title("CodeDrills Content Review")
    st.caption("A focused workspace for reviewing and improving app content.")

    st.sidebar.markdown("### Review queue")
    kind = st.sidebar.radio("Content", ("lessons", "challenges"), format_func=str.title)
    state = load_review_state()
    all_entries = collect_entries(kind)
    languages = sorted({item["language"] for item in all_entries})
    selected_language = st.sidebar.selectbox("Language", ["All", *languages])
    selected_level = st.sidebar.selectbox("Level", ["All", *LEVELS])
    available_topics = sorted(
        item["title"]
        for item in all_entries
        if (selected_language == "All" or item["language"] == selected_language)
        and (selected_level == "All" or item["level"] == selected_level)
    )
    selected_topic = st.sidebar.selectbox("Topic", ["All", *available_topics])
    section = st.sidebar.segmented_control(
        "Queue", ("To review", "Reviewed", "All"), default="To review"
    )

    entries = filtered_entries(
        all_entries,
        state[kind],
        selected_language,
        selected_level,
        selected_topic,
        section,
    )
    st.sidebar.divider()
    st.sidebar.metric("Items in queue", len(entries))
    st.sidebar.caption(f"{len(state[kind])} {kind} marked reviewed locally")
    if not entries:
        st.info("No content matches these filters.")
        return

    labels = {
        f"{item['language']} / {item['level']} / {item['title']}": item
        for item in entries
    }
    selected_label = st.selectbox("Choose an item", labels)
    selected = labels[selected_label]
    is_reviewed = selected["id"] in state[kind]

    left, right = st.columns((4, 1))
    with left:
        st.markdown(
            f"<div class='review-kicker'>{kind[:-1]} review</div>",
            unsafe_allow_html=True,
        )
        st.header(selected["title"])
        st.markdown(
            f"<div class='review-meta'>{selected['id']} &nbsp;|&nbsp; "
            f"{selected['path'].relative_to(ROOT)}</div>",
            unsafe_allow_html=True,
        )
    with right:
        status_class = "" if is_reviewed else " pending"
        status_text = "Reviewed" if is_reviewed else "To review"
        st.markdown(
            f"<div class='status-pill{status_class}'>{status_text}</div>",
            unsafe_allow_html=True,
        )

    preview_tab, edit_tab, source_tab = st.tabs(("Review", "Edit", "JSON"))
    with preview_tab:
        st.caption("Review the current content before editing.")
        st.json(selected["entry"], expanded=2)
    with edit_tab:
        st.caption("Changes are saved directly to the source JSON file.")
        updated_entry = editor(
            copy.deepcopy(selected["entry"]),
            "content",
            selected["id"],
            selected["language"],
        )
    with source_tab:
        st.caption("Use the copy button in the snippet to copy the full entry.")
        st.code(
            json.dumps(selected["entry"], ensure_ascii=False, indent=2), language="json"
        )

    st.divider()
    st.subheader("Review decision")
    st.caption("Saving validates all content files before confirming the result.")
    actions = st.columns((1.25, 1.5, 1))
    if actions[0].button("Save changes", type="primary"):
        replace_entry(kind, selected, updated_entry)
        valid, output = validate_source()
        if valid:
            st.success("Saved and validated source JSON.")
        else:
            st.error(
                "Saved, but validation failed. Correct the source before merging content."
            )
            st.code(output)
    if actions[1].button("Save and mark reviewed"):
        replace_entry(kind, selected, updated_entry)
        state[kind].add(selected["id"])
        write_review_state(state)
        valid, output = validate_source()
        if valid:
            st.success("Saved, validated, and marked reviewed.")
        else:
            st.error("Saved and marked reviewed, but validation failed.")
            st.code(output)
    if actions[2].button("Mark reviewed"):
        state[kind].add(selected["id"])
        write_review_state(state)
        st.success("Marked reviewed without changing source JSON.")


if __name__ == "__main__":
    main()
