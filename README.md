# CodeDrills

> Replace mindless scrolling with something actually useful — practice and learn coding, one drill at a time.

CodeDrills is a mobile app that delivers bite-sized coding challenges and lessons so you can turn idle moments into real learning. Pick a language, pick a level, and drill.

---

## 📚 Content Structure

Community-contributed content lives under two top-level directories:

```
challenges/
  <language>/
    <language>_challenges.json
topics/
  <language>/
    <language>_topics.json
```

### Supported Languages

| Language   | Directory         |
|------------|-------------------|
| Python     | `python/`         |
| SQL        | `sql/`            |
| JavaScript | `javascript/`     |
| Rust       | `rust/`           |

### Levels

Each file covers four levels:

| Level        | Description                              |
|--------------|------------------------------------------|
| `new`        | No prior experience assumed              |
| `beginner`   | Basic syntax and concepts                |
| `intermediate` | Real-world patterns and problem-solving |
| `advanced`   | Performance, idioms, deeper internals    |

---

## 🗂️ JSON Schemas

See the [`examples/`](examples/) folder for annotated reference files:

- [`examples/challenge_example.json`](examples/challenge_example.json) — challenge format
- [`examples/lesson_example.json`](examples/lesson_example.json) — topic/lesson format

### Challenge keys

```json
{
  "language": "python",
  "levels": [
    {
      "level": "new",
      "challenges": [
        {
          "id": "py-new-1",
          "language": "python",
          "level": "new",
          "title": "...",
          "description": "...",
          "starterCode": "...",
          "hint": "...",
          "solution": {
            "code": "...",
            "steps": [
              { "title": "...", "explanation": "..." }
            ]
          }
        }
      ]
    }
  ]
}
```

### Topic keys

```json
{
  "language": "python",
  "levels": [
    {
      "level": "new",
      "topics": [
        {
          "id": "py-new-datatypes",
          "language": "python",
          "level": "new",
          "title": "...",
          "description": "...",
          "estimatedMinutes": 8,
          "lessons": [
            { "title": "...", "body": "...", "code": "..." }
          ]
        }
      ]
    }
  ]
}
```

---

## 🤝 Contributing

We welcome challenge and topic contributions! Read [CONTRIBUTING.md](CONTRIBUTING.md) for step-by-step instructions, naming conventions, and the review process.

---

## 🔒 Privacy

See [privacy-policy.md](privacy-policy.md).

---

## 📄 License

[MIT](LICENSE) © Federico Raimondi
