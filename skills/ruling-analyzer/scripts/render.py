#!/usr/bin/env python3
"""Turn a ruling card (JSON) into the widget code of ספריית ההלכות.

  python3 render.py card.json             # short widget, the card is drawn by card.js from the CDN
  python3 render.py card.json --inline    # the same widget with card.js inside (fallback)
  python3 render.py card.json -o card.html   # to a file instead of the screen

The short widget holds only the card JSON and loads card.js from cdn.jsdelivr.net, which the
Visualizer allows. The full version puts the same card.js, from ../assets, inside the widget.
Both draw the card in the page with the same script. card.js is built by tools/card/build.py
in the repo, never edited by hand. Text markup: ==marker==, **bold**, [[pin]].
Standard library only.
"""
import argparse
import html
import json
import re
import sys
from pathlib import Path

ASSETS = Path(__file__).resolve().parent.parent / "assets"
CARD_JS = "https://cdn.jsdelivr.net/gh/idob4474/rulings-index@604cb94b03d1c9e880eb4a0752b1c9b82a96b48f/card/card.js"


def esc(s):
    return html.escape("" if s is None else str(s), quote=True)


def plain(s):
    return re.sub(r"\s+", " ", re.sub(r"\[\[.+?\]\]|==|\*\*", "", str(s or ""))).strip()


def payload(c):
    """The card JSON as a script literal that cannot close its script tag."""
    data = json.dumps(c, ensure_ascii=False, separators=(",", ":"))
    return data.replace("</", "<\\/").replace("<!--", "<\\!--").replace("\u2028", "\\u2028").replace("\u2029", "\\u2029")


def title(c):
    docket = c.get("docket") or c["cite"]
    return f'<h2 class="sr-only">כרטיס ספריית הלכות ל{esc(plain(docket + " " + c["name"]))}</h2>'


def render_inline(c):
    js = (ASSETS / "card.js").read_text(encoding="utf-8").replace("</script", "<\\/script")
    return "\n".join([
        title(c),
        '<div id="hl-root"></div>',
        f"<script>window.HLData={payload(c)}</script>",
        f"<script>{js}</script>",
    ]) + "\n"


def render_widget(c):
    docket = c.get("docket") or c["cite"]
    data = payload(c)
    retry = json.dumps(f"הכרטיס של {docket} לא נטען. הצג אותו שוב בגרסה המלאה", ensure_ascii=False)
    return "\n".join([
        title(c),
        f'<div id="hl-root"><p style="color:var(--text-secondary);font-size:14px">טוען את הכרטיס של {esc(docket)}</p></div>',
        f"<script>window.HLData={data};if(window.HLCard)HLCard.render(window.HLData)</script>",
        f'<script src="{CARD_JS}"></script>',
        "<script>setTimeout(function(){if(window.HLCard)return;var r=document.getElementById(\"hl-root\");"
        "r.innerHTML='<p style=\"color:var(--text-secondary);font-size:14px\">העיצוב של הכרטיס לא נטען</p><button type=\"button\">הצגה בגרסה המלאה ↗</button>';"
        f"r.querySelector(\"button\").onclick=function(){{sendPrompt({retry})}}}},6000)</script>",
    ]) + "\n"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("card")
    ap.add_argument("--inline", action="store_true", help="put card.js inside the widget, for when the CDN is blocked")
    ap.add_argument("-o", "--out")
    a = ap.parse_args()
    card = json.loads(Path(a.card).read_text(encoding="utf-8"))
    out = render_inline(card) if a.inline else render_widget(card)
    if a.out:
        Path(a.out).write_text(out, encoding="utf-8")
    else:
        sys.stdout.write(out)


if __name__ == "__main__":
    main()
