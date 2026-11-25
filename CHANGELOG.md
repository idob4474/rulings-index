# Changelog

All three skills and the marketplace share one version, the one in `.claude-plugin/marketplace.json`.

## 1.3.0, November 2026

- `lookup.py` no longer picks a ruling automatically when no candidate carries the names in the query.
- `lecture-summarizer` defines where ruling-analyzer is, validates the card, and says what to do with unknown fields and missing pins.
- `exam-simulator` has one order of precedence for question type, never names an unverified ruling, and handles hints and skipped feedback.
- The shared version now matches the one in `skills/ruling-analyzer/README.md`.

## 1.1.0, November 2026

- Added `lecture-summarizer` and `exam-simulator`.
- `.claude-plugin/marketplace.json` has a plugin per skill and the `law-student-pack` bundle.
- Lecture cards are validated by `validate.py` and rendered by the same card renderer as rulings.
- Name, description and heading are uniform across the skills, and CI enforces it.

## 1.0.0, November 2026

- First release with `ruling-analyzer`.
