# Halachot skills

Claude skills for Israeli law students, and the open index of Supreme Court rulings they read from.

כלים ל-Claude לסטודנטים למשפטים. [מדריך התקנה בעברית](skills/ruling-analyzer/README.md)

## Skills

| Skill | What it does | Download |
| --- | --- | --- |
| [ruling-analyzer](skills/ruling-analyzer) | מנתח פסק דין ישראלי לכרטיס לימוד בעיצוב ספריית ההלכות. לכל טענה יש מראה מקום, וכל טענה נבדקת מול הנוסח המלא, בסקריפט ובבודק ספקן, לפני שהכרטיס מוצג | [ruling-analyzer.zip](https://github.com/idob4474/rulings-index/releases/download/skills/ruling-analyzer.zip) |

Every skill lives in `skills/` as a plain folder, exactly as Claude loads it, with its `SKILL.md`, scripts and assets. The ZIPs are built from these folders on every change and published on the [skills release](https://github.com/idob4474/rulings-index/releases/tag/skills), so the download links never change.

## Install

**Claude on the web or desktop**

1. In Settings, then Capabilities, turn on Create and edit files.
2. Download the skill's ZIP from the table above. Do not unzip it.
3. In Customize, then Skills, click +, then Create skill, then Upload a skill, and pick the ZIP.

**Claude Code**

```
/plugin marketplace add idob4474/rulings-index
/plugin install ruling-analyzer@halachot-skills
```

Or copy `skills/ruling-analyzer` into `~/.claude/skills/`.

## Repository layout

| Path | What it is |
| --- | --- |
| `skills/` | One folder per skill, raw, as Claude loads it |
| `card/card.js` | The card renderer that ruling-analyzer loads through jsDelivr, pinned to a commit |
| `tools/card/` | Source and build script of `card.js` |
| `scripts/` | `build_index.py` builds the rulings index, `lookup.py` finds a ruling in it. The skill carries the same `lookup.py` |
| `.claude-plugin/marketplace.json` | The Claude Code plugin marketplace |
| `.github/workflows/skills.yml` | Checks the skills and publishes their ZIPs on the release `skills` |
| `.github/workflows/rulings-index.yml` | Builds the rulings index and publishes it on the release `rulings-2022` |

## Rulings index

Find an Israeli Supreme Court ruling by case number or by the parties' names, and get its exact full text.

```bash
curl -fsSL https://raw.githubusercontent.com/idob4474/rulings-index/main/scripts/lookup.py -o lookup.py
python3 lookup.py 'ע"א 8146/13'
python3 lookup.py "ג'ושה אלדג'אני"
```

The texts live in the `rulings-2022` release, built by the workflow in this repo. About 97,000 documents, of which about 82,000 are judgments. Lower courts, rulings after 2022 and many rulings from before the late 1990s are not included.

## Source and credit

The data comes from the dataset [LevMuchnik/SupremeCourtOfIsrael](https://huggingface.co/datasets/LevMuchnik/SupremeCourtOfIsrael), a 2022 snapshot of the Supreme Court website, curated by Prof. Lev Muchnik (Hebrew University of Jerusalem) and Dr. Inbal Yahav Shenberger (Tel Aviv University) and published under the OpenRAIL license. Court rulings themselves are not protected by copyright under section 6 of the Israeli Copyright Act.
