# Contributing to CodeDrills

Thank you for helping make CodeDrills better! This guide explains how to add new **challenges** or **topics/lessons** to the content library.

---

## Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [What you can contribute](#what-you-can-contribute)
3. [Getting started](#getting-started)
4. [File structure](#file-structure)
5. [Challenge format](#challenge-format)
6. [Topic format](#topic-format)
7. [Naming conventions](#naming-conventions)
8. [Submitting a pull request](#submitting-a-pull-request)
9. [Validation](#validation)

---

## Code of Conduct

Be kind, constructive, and inclusive. Harassment or discrimination of any kind will not be tolerated.

---

## What you can contribute

| Type        | Description |
|-------------|-------------|
| **Challenge** | A focused coding exercise with starter code, a hint, and a step-by-step solution |
| **Topic**     | A short lesson with explanations and optional code snippets |

Both types support four levels: `new`, `beginner`, `intermediate`, `advanced`.

Supported languages: **Python**, **SQL**, **JavaScript**, **Rust**.

---

## Getting started

1. **Fork** this repository.
2. **Clone** your fork locally.
3. Create a new branch: `git checkout -b add/<language>-<level>-<short-name>`
4. Add or edit the relevant JSON file(s).
5. Run the local validator (see [Validation](#validation)).
6. Open a pull request against `main`.

---

## File structure

```
challenges/
  <language>/
    <language>_challenges.json
topics/
  <language>/
    <language>_topics.json
```

Each file covers **all four levels** in one JSON document.

---

## Challenge format

Full annotated example: [`examples/challenge_example.json`](examples/challenge_example.json)

Required top-level keys: `language`, `levels`  
Each level object: `level`, `challenges`  
Each challenge object:

| Key           | Type   | Description |
|---------------|--------|-------------|
| `id`          | string | Unique, e.g. `py-new-1` |
| `language`    | string | Matches the file's top-level `language` |
| `level`       | string | `new` / `beginner` / `intermediate` / `advanced` |
| `title`       | string | Short human-readable title |
| `description` | string | Full task description |
| `starterCode` | string | Pre-filled code shown to the user |
| `hint`        | string | One-line nudge |
| `solution`    | object | `{ "code": "...", "steps": [...] }` |

Each solution step: `{ "title": "...", "explanation": "...", "code"?: "..." }`

---

## Topic format

Full annotated example: [`examples/lesson_example.json`](examples/lesson_example.json)

Required top-level keys: `language`, `levels`  
Each level object: `level`, `topics`  
Each topic object:

| Key                | Type    | Description |
|--------------------|---------|-------------|
| `id`               | string  | Unique, e.g. `py-new-datatypes` |
| `language`         | string  | Matches the file's top-level `language` |
| `level`            | string  | `new` / `beginner` / `intermediate` / `advanced` |
| `title`            | string  | Short human-readable title |
| `description`      | string  | One-sentence summary |
| `estimatedMinutes` | integer | Reading/practice time in minutes |
| `lessons`          | array   | Array of lesson objects |

Each lesson: `{ "title": "...", "body": "...", "code"?: "..." }`

---

## Naming conventions

- **IDs** — `<lang-abbr>-<level>-<slug>`, e.g. `js-beginner-arrays`
- **File IDs** are lowercase with hyphens; no spaces.
- **Language abbreviations**: `py`, `sql`, `js`, `rs`

---

## Submitting a pull request

1. Make sure `scripts/validate_json.py` passes with no errors.
2. Fill in the pull request template completely.
3. Link any related issues.
4. One PR per language/level addition is preferred.

A maintainer will review within a few days. Feedback will be left as review comments.

---

## Validation

Run the bundled validation script before opening a PR:

```bash
python scripts/validate_json.py
```

It checks:
- All JSON files are valid JSON.
- Top-level keys (`language`, `levels`) are present.
- Each level entry has a valid `level` value and the correct content key (`challenges` or `topics`).
- Each challenge/topic has all required keys.
- IDs are unique within their file.

Fix any errors reported before submitting.
