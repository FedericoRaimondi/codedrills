# GitHub Copilot Instructions — CodeDrills

CodeDrills is a **content-only repository**: no application code, no build system. All contributions are JSON data files for a mobile coding-practice app. There are no npm/pip dependencies to install beyond the stdlib-only validator.

## Repository Structure

```
challenges/<language>/<language>_challenges.json   # coding exercises
topics/<language>/<language>_topics.json           # lessons/theory
examples/challenge_example.json                    # canonical challenge schema
examples/lesson_example.json                       # canonical topic/lesson schema
scripts/validate_json.py                           # sole CI script (stdlib only)
```

Supported languages: `python`, `javascript`, `sql`, `rust`. Each JSON file covers all four levels in one document.

## JSON Schemas

### Challenge (`challenges/<lang>/<lang>_challenges.json`)
```json
{
  "language": "python",
  "levels": [{
    "level": "new",
    "challenges": [{
      "id": "py-new-1",
      "language": "python",
      "level": "new",
      "title": "...",
      "description": "...",
      "starterCode": "# Write your code below\n",
      "hint": "...",
      "solution": {
        "code": "...",
        "steps": [{ "title": "...", "explanation": "...", "code": "..." }]
      }
    }]
  }]
}
```
`code` on a step is optional; all rest are required.

### Topic (`topics/<lang>/<lang>_topics.json`)
```json
{
  "language": "python",
  "levels": [{
    "level": "new",
    "topics": [{
      "id": "py-new-datatypes",
      "language": "python",
      "level": "new",
      "title": "...",
      "description": "...",
      "estimatedMinutes": 8,
      "lessons": [{ "title": "...", "body": "...", "code": "...", "runnable": true or false}]
    }]
  }]
}
```
`code` on a lesson is optional; all rest are required.
`runnable` on a lesson is required if `code` is present; it indicates whether the code can executed based on topics/runnable-code-in-topics.md.

## ID Conventions

- Format: `<lang-abbr>-<level>-<slug>` — e.g. `py-new-1`, `js-beginner-arrays`, `rs-intermediate-ownership`
- Abbreviations: `py`, `js`, `sql`, `rs`
- Slugs: lowercase, hyphens only, no spaces
- IDs must be **unique within their file** (validator enforces this)

## Validation (run before every PR)

```bash
python scripts/validate_json.py
```

Checks: valid JSON, required top-level keys, valid `level` values (`new`/`beginner`/`intermediate`/`advanced`), all required keys per entry, and ID uniqueness. The script auto-discovers all files under `challenges/` and `topics/`. CI runs this automatically on PRs touching those paths.

## Key Conventions

- Both `challenge["language"]` and `topic["language"]` must match the file's top-level `"language"` value.
- Both `challenge["level"]` and `topic["level"]` must match the parent `level` object's `"level"` value.
- `starterCode` uses `\n` for newlines within the JSON string (not actual newlines).
- Solution `steps` should walk through reasoning, not just repeat the code — typically 2–4 steps.
- `estimatedMinutes` for topics should reflect realistic reading + practice time (e.g. 5–15 min).

## Branch & PR Workflow

- Branch naming: `add/<language>-<level>-<short-name>`
- One PR per language/level addition is preferred
- PR template at `.github/PULL_REQUEST_TEMPLATE.md` must be filled in completely
- Issue templates for new content live in `.github/ISSUE_TEMPLATE/`
