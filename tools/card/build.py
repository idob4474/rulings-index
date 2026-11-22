"""Build the card renderer of the ruling-analyzer skill.

  python3 tools/card/build.py              # writes card/card.js and the skill's assets/card.js
  python3 tools/card/build.py --out x.js   # writes one file elsewhere, for a check

card.src.js is the one renderer of the card, and card.css its style. The build puts the style
inside the script. card/card.js is what the skill loads through jsDelivr, pinned to a commit
so a card already shown never changes. The skill keeps an identical copy in assets/card.js,
which render.py --inline puts inside the widget when the CDN is blocked.

After a change, commit both files and point CARD_JS in render.py at the new commit.
"""
import argparse
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]

ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
ap.add_argument("--out", type=Path, help="write one file here instead of the two usual places")
ap.add_argument("--version", default="card-v3")
a = ap.parse_args()

css = (HERE / "card.css").read_text(encoding="utf-8")
css = "\n".join(line.strip() for line in css.strip().splitlines() if line.strip())
src = (HERE / "card.src.js").read_text(encoding="utf-8")
js = src.replace("__CSS__", json.dumps(css, ensure_ascii=False)).replace("__VERSION__", json.dumps(a.version))
assert "__CSS__" not in js and "__VERSION__" not in js, "placeholder left"
outs = [a.out] if a.out else [ROOT / "card" / "card.js", ROOT / "skills" / "ruling-analyzer" / "assets" / "card.js"]
for out in outs:
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(js, encoding="utf-8")
    print(f"{out} {len(js)} chars, css {len(css)} chars, version {a.version}")
