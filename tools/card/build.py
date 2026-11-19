"""Build card/card.js, the card renderer the ruling-analyzer skill loads through jsDelivr.

  python3 tools/card/build.py              # writes card/card.js
  python3 tools/card/build.py --out x.js   # writes elsewhere, for a check

The style comes from the skill's assets/head.html, so the CDN card and the skill's full
inline card (render.py --inline) look the same. card.src.js mirrors render_inline() in
skills/ruling-analyzer/scripts/render.py. A change to either goes into both.

card.js is served pinned to a commit, so a card already shown never changes. After a
change, commit card/card.js and point CARD_JS in render.py at the new commit.
"""
import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
ap.add_argument("--skill", type=Path, default=ROOT / "skills" / "ruling-analyzer")
ap.add_argument("--out", type=Path, default=ROOT / "card" / "card.js")
ap.add_argument("--version", default="card-v1")
a = ap.parse_args()

head = (a.skill / "assets" / "head.html").read_text(encoding="utf-8")
css = re.search(r"<style>(.*?)</style>", head, re.S).group(1)
css = "\n".join(line.strip() for line in css.strip().splitlines() if line.strip())
src = (Path(__file__).parent / "card.src.js").read_text(encoding="utf-8")
js = src.replace("__CSS__", json.dumps(css, ensure_ascii=False)).replace("__VERSION__", json.dumps(a.version))
assert "__CSS__" not in js and "__VERSION__" not in js, "placeholder left"
a.out.parent.mkdir(parents=True, exist_ok=True)
a.out.write_text(js, encoding="utf-8")
print(f"{a.out} {len(js)} chars, css {len(css)} chars, version {a.version}")
