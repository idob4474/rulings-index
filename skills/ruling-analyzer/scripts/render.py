#!/usr/bin/env python3
"""Turn a ruling card (JSON) into the widget code of ספריית ההלכות.

  python3 render.py card.json             # short widget, the card is drawn by card.js from the CDN
  python3 render.py card.json --inline    # full HTML with the style and script inside (fallback)
  python3 render.py card.json -o card.html

The short widget holds only the card JSON and loads the design from cdn.jsdelivr.net, which
the Visualizer allows. The full HTML takes the style and script from ../assets. Both draw the
same card. card.js is a mirror of render_inline() below, keep the two in step.
Text markup: ==marker==, **bold**, [[pin]]. Standard library only.
"""
import argparse
import html
import json
import re
import sys
from pathlib import Path

ASSETS = Path(__file__).resolve().parent.parent / "assets"
HEB = re.compile(r"[א-ת]")
DOCKET_LEAD = re.compile(r"^\s*([^\s.]{1,8}\s+\d{1,6}/\d{2,4})\.\s*")
CARD_JS = "https://cdn.jsdelivr.net/gh/idob4474/rulings-index@604cb94b03d1c9e880eb4a0752b1c9b82a96b48f/card/card.js"


def esc(s):
    return html.escape("" if s is None else str(s), quote=True)


def rich(s):
    out = esc(s)
    out = re.sub(r"==(.+?)==", r"<mark>\1</mark>", out)
    out = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", out)
    return re.sub(r"\[\[(.+?)\]\]", r'<span class="pin">\1</span>', out)


def js_str(s):
    """A string literal for an inline onclick handler, safe inside a double-quoted attribute."""
    lit = "'" + str(s).replace("\\", "\\\\").replace("'", "\\'") + "'"
    return html.escape(lit, quote=False).replace('"', "&quot;")


def icon(name):
    return f'<i class="ti ti-{name}" aria-hidden="true"></i>'


def section(title, ic, body, count=None):
    cnt = f'<span class="cnt">{count}</span>' if count is not None else ""
    return (f'<details class="sec" open><summary><span class="ic">{icon(ic)}</span><span>{esc(title)}</span>{cnt}'
            f'<i class="ti ti-chevron-down chev" aria-hidden="true"></i></summary><div class="body">\n{body}\n</div></details>')


def seal(docket, letter):
    return (f'<svg class="seal" id="hl-seal" data-id="{esc(docket)}" viewBox="-50 -50 100 100" aria-hidden="true">'
            '<circle class="disc" r="47"></circle><path class="sg p1" stroke-width="0.7" opacity="0.9"></path>'
            '<path class="sg p2" stroke-width="0.55" opacity="0.65"></path><circle class="sg" r="47" stroke-width="1.4"></circle>'
            '<circle class="sg" r="22" stroke-width="0.8" opacity="0.6"></circle><circle r="20" fill="var(--card)"></circle>'
            f'<text class="ltr" x="0" y="1" text-anchor="middle" dominant-baseline="central" font-size="24">{esc(letter)}</text></svg>')


def plain(s):
    return re.sub(r"\s+", " ", re.sub(r"\[\[.+?\]\]|==|\*\*", "", str(s or ""))).strip()


def render_inline(c):
    vol = "torts" if c.get("course") == "torts" else "corp"
    docket = c.get("docket") or c["cite"]
    seal_id = (re.search(r"\d+/\d+|\d+-\d+-\d+", docket) or re.search(".+", docket)).group(0)
    letter = (HEB.search(c["short"]) or HEB.search(c["name"]) or re.search(".", "?")).group(0)
    holdings = c["holdings"]
    keys = c.get("keys") or [0, 1, 2]
    parts = []

    crumbs = [f'<span><i class="dot"></i>{esc(c.get("courseName") or "")}</span>'] if c.get("courseName") else []
    if c.get("chapter"):
        crumbs.append(f'<span>{esc(c["chapter"])}</span>')
    parts.append(f'<div class="hl" data-vol="{vol}">')
    if crumbs:
        parts.append(f'<div class="crumbs">{"".join(crumbs)}</div>')

    facts = "".join(f'<div class="fact"><dt>{esc(k)}</dt><dd>{rich(v)}</dd></div>' for k, v in c["meta"])
    if c.get("draft"):
        trust = f'<span class="trust draft">{icon("alert-triangle")}טיוטה, לא נבדק מול הנוסח</span>'
    else:
        trust = f'<span class="trust">{icon("shield-check")}{esc(c["status"])}</span>'
    parts.append(
        '<header class="case-h">\n'
        f'<div class="row"><div><p class="sub">{esc(c["eyebrow"])}</p><h1>{esc(c["short"])}</h1></div>{seal(seal_id, letter)}</div>\n'
        f'<p class="aka">{rich(c["aka"])}</p>\n'
        f'<dl class="facts">{facts}</dl>\n'
        f'<p class="cite">{esc(c["cite"])}</p>\n'
        f'<div class="statusrow">{trust}<button type="button" class="switch" role="switch" aria-checked="true" id="hl-pins">'
        '<i aria-hidden="true"></i>מראי מקום</button></div>\n</header>')

    key_items = "\n".join(
        f'<li>{icon("circle-check")}<span><b>{esc(holdings[k][0])}</b><span class="txt">{rich(holdings[k][1])}</span></span></li>'
        for k in keys if 0 <= k < len(holdings))
    report = js_str(f"מצאתי טעות בכרטיס של {docket}. בוא נבדוק אותו שוב מול הנוסח")
    parts.append(
        '<section class="brief" aria-label="בקצרה">\n'
        f'<div><h3>ההלכה בשורה אחת</h3><p class="lead">{rich(c["oneLine"])}</p></div>\n'
        f'<div><h3>שלוש הלכות לזכור</h3><ul class="keys">\n{key_items}\n</ul></div>\n'
        '<div class="write"><div class="head"><h3>מה לכתוב במבחן</h3><button type="button" class="btn ghost" id="hl-copy">'
        f'{icon("copy")}<span>העתקה</span></button></div><p id="hl-write">{rich(c["exam"]["write"])}</p></div>\n'
        f'<div class="actions"><button type="button" class="btn" onclick="window.print()">{icon("printer")}הדפסה</button>'
        f'<button type="button" class="btn ghost" onclick="sendPrompt({report})">{icon("flag")}דיווח על טעות ↗</button></div>\n'
        '</section>')

    secs = []
    body = "\n".join(f"<p>{rich(p)}</p>" for p in c["background"])
    if c.get("questions"):
        body += '\n<h4>השאלות המשפטיות</h4><ul class="plain">' + "".join(f"<li>{rich(q)}</li>" for q in c["questions"]) + "</ul>"
    secs.append(section("רקע והשאלות", "book", body))
    secs.append(section("ההכרעה", "gavel", f'<p>{rich(c["decision"])}</p>'))

    body = '<ul class="holdings">\n' + "\n".join(f"<li><b>{esc(t)}</b>{rich(x)}</li>" for t, x in holdings) + "\n</ul>"
    cl = c.get("clause")
    if cl:
        body += (f'\n<div class="clause"><p class="lbl">{esc(cl["label"])}</p><ol>'
                 + "".join(f"<li>{rich(x)}</li>" for x in cl["items"]) + "</ol>"
                 + (f'<p>{rich(cl["after"])}</p>' if cl.get("after") else "") + "</div>")
    secs.append(section("כל ההלכות", "list", body, len(holdings)))

    js = c.get("justices") or []
    if js:
        cards = "\n".join(
            f'<div class="justice"><header><h5>{esc(j["name"])}</h5><span class="tag{" solo" if j.get("solo") else ""}">{esc(j["tag"])}</span></header>'
            f'<p class="theory">{esc(j["theory"])}</p><p>{rich(j["text"])}</p></div>' for j in js)
        body = f'<div class="justices">\n{cards}\n</div>'
        if c.get("common"):
            body += f'\n<p>{rich(c["common"])}</p>'
        q = c.get("quote")
        if q:
            body += f'\n<p class="quote">{rich(q["text"])}</p>\n<p class="quote-src">{rich(q["src"])}</p>'
        secs.append(section(c.get("justicesTitle") or "מי אמר מה", "users", body, len(js)))

    ly = c.get("layer")
    if ly and (ly.get("reading") or ly.get("note")):
        inner = (f'<p class="lbl">{esc(ly.get("title") or "")}</p>' if ly.get("title") else "")
        inner += "".join(f"<p>{rich(ly[k])}</p>" for k in ("reading", "note") if ly.get(k))
        secs.append(section("בקורס של המרצה", "school", f'<div class="layer">{inner}</div>'))

    ex = c["exam"]
    steps = '<li class="arr" aria-hidden="true">←</li>'.join(
        f'<li class="here">{esc(p)}</li>' if i == ex["here"] else f"<li>{esc(p)}</li>" for i, p in enumerate(ex["path"]))
    body = f'<h4>{esc(ex["pathLabel"])}</h4><ol class="path">{steps}</ol>'
    if ex.get("traps"):
        body += '\n<h4>מלכודות שמורידות נקודות</h4><ul class="plain">\n' + "\n".join(f"<li>{rich(t)}</li>" for t in ex["traps"]) + "\n</ul>"
    secs.append(section("למבחן", "target", body))

    pr = c.get("practice") or []
    if pr:
        body = "\n".join(
            f'<details class="qa"><summary><span>{rich(p["q"])}</span><span class="open">הצגת ראשי פרקים</span></summary>'
            f'<div class="ans"><ul class="plain">' + "".join(f"<li>{rich(a)}</li>" for a in p["a"]) + "</ul></div></details>"
            for p in pr)
        secs.append(section("תרגול", "help", body, len(pr)))

    rel = c.get("related") or []
    if rel:
        items = []
        for r in rel:
            name, kw, text = r[0], r[1], r[2]
            m = DOCKET_LEAD.match(text)
            if m:
                ask = js_str(f"נתח את {m.group(1)} {re.sub(r'\s*\(\s*\d+/\d+\s*\)', '', name)}")
                items.append(f'<div class="rel go" onclick="sendPrompt({ask})"><span class="kw">{esc(kw)}</span>'
                             f'<b>{esc(name)} ↗</b><p>{rich(text)}</p></div>')
            else:
                items.append(f'<div class="rel"><span class="kw">{esc(kw)}</span><b>{esc(name)}</b><p>{rich(text)}</p></div>')
        secs.append(section("פסקי דין קשורים", "link", '<div class="related">\n' + "\n".join(items) + "\n</div>"))

    if c.get("context"):
        secs.append(section("הקשר אקטואלי", "world", f'<p>{rich(c["context"])}</p>'))

    src = "".join(
        f'<li><a href="{esc(s[1])}">{esc(s[0])}</a></li>' if isinstance(s, list) else f"<li>{rich(s)}</li>"
        for s in c["sources"])
    secs.append(section("מקורות", "file-text", f'<ul class="sources">{src}</ul>'))

    parts.append('<div class="sections">\n' + "\n".join(secs) + "\n</div>\n</div>")

    head = (ASSETS / "head.html").read_text(encoding="utf-8").rstrip("\n")
    tail = (ASSETS / "tail.html").read_text(encoding="utf-8").rstrip("\n")
    sr = f'<h2 class="sr-only">כרטיס ספריית הלכות ל{esc(plain(docket + " " + c["name"]))}</h2>'
    return "\n".join([sr, head, *parts, tail]) + "\n"


def render_widget(c):
    docket = c.get("docket") or c["cite"]
    sr = f'<h2 class="sr-only">כרטיס ספריית הלכות ל{esc(plain(docket + " " + c["name"]))}</h2>'
    data = json.dumps(c, ensure_ascii=False, separators=(",", ":"))
    data = data.replace("</", "<\\/").replace("<!--", "<\\!--").replace("\u2028", "\\u2028").replace("\u2029", "\\u2029")
    retry = json.dumps(f"הכרטיס של {docket} לא נטען. הצג אותו שוב בגרסה המלאה", ensure_ascii=False)
    return "\n".join([
        sr,
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
    ap.add_argument("--inline", action="store_true", help="full HTML with the design inside, for when the CDN is blocked")
    ap.add_argument("-o", "--out")
    a = ap.parse_args()
    card = json.loads(Path(a.card).read_text(encoding="utf-8"))
    out = render_inline(card) if a.inline else render_widget(card)
    if a.out:
        Path(a.out).write_text(out, encoding="utf-8")
    sys.stdout.write(out)


if __name__ == "__main__":
    main()
