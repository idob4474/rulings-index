#!/usr/bin/env python3
"""Find an Israeli Supreme Court ruling by case number or parties and extract its exact full text.

The data is the "rulings-2022" release built by .github/workflows/rulings-index.yml
(Supreme Court only, 2022 snapshot). Standard library only, plus the gh CLI for downloads.

  lookup.py 'ע"א 8146/13'            # by case number, any spelling: עא 8146/13, 8146-13, 8146/2013
  lookup.py "ג'ושה אלדג'אני"          # by party names
  lookup.py --id 123456               # extract one document by its id from an earlier listing
  lookup.py 'ע"א 8146/13' --all       # extract every listed document of the case

Exit codes: 0 text extracted, 2 several candidates (ask the user which one), 3 not found.
Options: --out DIR (default ./rulings), --source DIR (local index and shards instead of the
release), --refresh (download the index again).
"""
import argparse
import collections
import gzip
import json
import os
import re
import subprocess
import sys

REPO = os.environ.get("RULINGS_REPO", "idob4474/rulings-index")
TAG = os.environ.get("RULINGS_TAG", "rulings-2022")
CACHE = os.path.expanduser(os.environ.get("RULINGS_CACHE", "~/.cache/halachot-rulings"))
NUM_RE = re.compile(r"(\d{1,6})\s*[/\-\\]\s*(\d{4}|\d{2})(?!\d)")
LOWER_RE = re.compile(r"(?<!\d)\d{3,6}-\d{2}-\d{2}(?!\d)")  # district and magistrate courts, e.g. 58416-04-19
FINALS = str.maketrans("ךםןףץ", "כמנפצ")
JUDGMENT = "פסק-דין"
STOP = {"נ", "נגד", "ואח", "ואחרים", "בעמ", "מ", "בע", "את", "של", "ו"}
PREFIXES = set("והבלמשכ")
CHEAP = str.maketrans({**{c: None for c in "\"'`״׳‘’"}, **dict(zip("ךםןףץ", "כמנפצ"))})
RARE_DF = 1500  # a query word in fewer documents than this is treated as a name that must match


def norm(s: str) -> str:
    s = re.sub(r"[֑-ׇ]", "", s or "")  # niqqud and cantillation
    s = re.sub(r"[\"'`״׳‘’]", "", s)  # ג'ושה -> גושה, ע"א -> עא
    s = re.sub(r"[.,:;()\[\]\-/]", " ", s)
    return re.sub(r"\s+", " ", s.translate(FINALS)).strip()


def prefix_key(s: str) -> str:
    return norm(s).replace(" ", "")


def case_year(yy: str) -> int:
    y = int(yy)
    if len(yy) == 4:
        return y
    return 1900 + y if y > 30 else 2000 + y


def gh_api(path: str, accept=None, dest=None):
    """Call the GitHub REST API through gh. REST only: some environments block GraphQL,
    which `gh release` uses, and numeric repository paths, which `--paginate` follows."""
    cmd = ["gh", "api", path] + (["-H", f"Accept: {accept}"] if accept else [])
    if dest:
        tmp = dest + ".part"
        with open(tmp, "wb") as f:
            r = subprocess.run(cmd, stdout=f, stderr=subprocess.PIPE)
        if r.returncode != 0:
            os.remove(tmp)
            return None, r.stderr.decode(errors="replace").strip()
        os.replace(tmp, dest)
        return dest, ""
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        return None, r.stderr.strip()
    return json.loads(r.stdout), ""


def asset_ids(refresh=False) -> dict:
    path = os.path.join(CACHE, f"assets-{TAG}.json")
    if not refresh and os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    rel, err = gh_api(f"repos/{REPO}/releases/tags/{TAG}")
    if rel is None:
        sys.exit(f"cannot read release {TAG} of {REPO} ({err}). Is the repo attached to this session?")
    ids, page = {}, 1
    while True:
        batch, err = gh_api(f"repos/{REPO}/releases/{rel['id']}/assets?per_page=100&page={page}")
        if batch is None:
            sys.exit(f"cannot list assets of {TAG} ({err})")
        if not batch:
            break
        ids.update({a["name"]: a["id"] for a in batch})
        page += 1
    with open(path, "w", encoding="utf-8") as f:
        json.dump(ids, f)
    return ids


def fetch(name: str, source, refresh=False) -> str:
    if source:
        p = os.path.join(source, name)
        if not os.path.exists(p):
            sys.exit(f"missing {p}")
        return p
    os.makedirs(CACHE, exist_ok=True)
    p = os.path.join(CACHE, name)
    if refresh or not os.path.exists(p):
        for attempt in (0, 1):  # the release may have been rebuilt with new asset ids
            ids = asset_ids(refresh or attempt == 1)
            if name in ids:
                got, err = gh_api(f"repos/{REPO}/releases/assets/{ids[name]}", "application/octet-stream", p)
                if got:
                    break
            else:
                err = "not in the release"
        else:
            sys.exit(f"download of {name} from {REPO} release {TAG} failed: {err}")
    return p


def load_index(source, refresh):
    with gzip.open(fetch("index.json.gz", source, refresh), "rt", encoding="utf-8") as f:
        idx = json.load(f)
    fields = idx["fields"]
    return idx, [dict(zip(fields, r)) for r in idx["rows"]]


def by_number(rows, query):
    m = NUM_RE.search(query)
    num, year = int(m.group(1)), case_year(m.group(2))
    hits = [r for r in rows if r["num"] == num and r["year"] == year]
    want = prefix_key(query[: m.start()])
    note = ""
    if want:
        same = [r for r in hits if prefix_key(NUM_RE.sub("", r["case"])) == want]
        if same:
            hits = same
        elif hits:
            note = f"no {query[: m.start()].strip()} with this number, showing every procedure numbered {num}/{str(year)[2:]}"
    return hits, note


def by_parties(rows, query, source, refresh):
    want = collections.Counter(t for t in norm(query).split() if len(t) > 1 and t not in STOP)
    toks = list(want.elements())
    if not toks:
        return [], "no searchable words in the query"
    need = max(1, -(-len(toks) * 2 // 3))  # at least two thirds of the words
    # The metadata often anonymises names (פלוני נ. פלוני) that the opening of the text keeps.
    with gzip.open(fetch("heads.json.gz", source, refresh), "rt", encoding="utf-8") as f:
        heads = dict(json.load(f)["rows"])
    docs = [(r, " ".join((r["name"], r["parties"], heads.get(r["id"], ""))).translate(CHEAP)) for r in rows]

    # Fast substring pass. A rare word (usually a surname) must match, common ones may be missing.
    df = {t: sum(1 for _, h in docs if t in h) for t in want}
    absent = [t for t in want if df[t] == 0]
    note = f"these words appear in no ruling in the index, {' '.join(absent)}" if absent else ""
    rare = [t for t in want if 0 < df[t] <= RARE_DF]
    cands = [(r, h) for r, h in docs if all(t in h for t in rare) and sum(t in h for t in toks) >= need]

    first = {t[0] for t in want}
    scored = []
    for r, h in cands:
        words = collections.Counter()
        for w in norm(h).split():
            words[w] += 1
            # Hebrew attached prefixes, והמשיבה -> משיבה, לבנק -> בנק
            for k in (1, 2):
                if len(w) - k >= 2 and all(c in PREFIXES for c in w[:k]) and w[k] in first:
                    words[w[k:]] += 1
        score = sum(min(n, words[t]) for t, n in want.items())  # a repeated name must appear as often
        if score >= need and all(words[t] for t in rare):
            scored.append((score, r))
    if not scored:
        return [], note
    # best score first, then judgments, then longer documents, one line per case and document type
    seen, out = set(), []
    for s, r in sorted(scored, key=lambda x: (-x[0], x[1]["type"] != JUDGMENT, -x[1]["pages"])):
        k = (r["case"], r["type"])
        if k not in seen:
            seen.add(k)
            out.append(r)
    if len(out) > 15:
        note = (note + ". " if note else "") + f"{len(out)} matches, showing the best 15, add a party name to narrow"
    return out[:15], note


def show(r):
    return (f"  id {r['id']} | {r['case']} | {r['name']} | {r['type']} | ניתן {r['date'] or '?'} | "
            f"{r['pages']} עמ׳ | {r['judges']}")


def paragraph_report(text: str) -> str:
    nums = [int(m.group(1)) for m in re.finditer(r"(?m)^\s*(\d{1,3})\s*\.\s+\S", text)]
    if not nums:
        return "no numbered paragraphs found at line starts, cite by judge and position"
    resets = sum(1 for a, b in zip(nums, nums[1:]) if b <= a)
    return f"{len(nums)} numbered paragraph starts, highest {max(nums)}, {resets} restarts (a restart usually means a new opinion)"


def extract(r, source, out_dir):
    path = fetch(f"shard-{r['shard']}.jsonl.gz", source)
    with gzip.open(path, "rt", encoding="utf-8") as f:
        for line in f:
            if line.startswith(f'{{"id": {r["id"]},'):
                doc = json.loads(line)
                break
        else:
            sys.exit(f"id {r['id']} not found in {os.path.basename(path)}")
    os.makedirs(out_dir, exist_ok=True)
    safe = re.sub(r"[^\w\-]+", "_", f"{prefix_key(NUM_RE.sub('', r['case']))}_{r['num']}_{str(r['year'])[2:]}_{r['id']}")
    dest = os.path.join(out_dir, safe + ".txt")
    header = (f"מקור: מאגר פסקי הדין של בית המשפט העליון (LevMuchnik/SupremeCourtOfIsrael, תמונת מצב 2022)\n"
              f"מסמך {r['id']} | {r['case']} | {r['name']} | {r['type']} | ניתן {r['date'] or 'לבדוק בנוסח'}\n"
              f"שופטים לפי המטא דאטה: {r['judges']}\n" + "=" * 40 + "\n")
    with open(dest, "w", encoding="utf-8") as f:
        f.write(header + doc["text"] + "\n")
    print(f"TEXT {dest}")
    print(f"  {len(doc['text'])} chars, {paragraph_report(doc['text'])}")
    return dest


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("query", nargs="?", default="")
    ap.add_argument("--id", type=int)
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--out", default="rulings")
    ap.add_argument("--source")
    ap.add_argument("--refresh", action="store_true")
    a = ap.parse_args()

    idx, rows = load_index(a.source, a.refresh)
    print(f"index built {idx['built']}, {len(rows)} documents")

    if a.id is not None:
        hit = [r for r in rows if r["id"] == a.id]
        if not hit:
            print(f"NOT FOUND id {a.id}")
            sys.exit(3)
        extract(hit[0], a.source, a.out)
        return

    if LOWER_RE.search(a.query):
        print("NOT FOUND this is a lower court case number (number-month-year), the index holds Supreme Court rulings only")
        sys.exit(3)
    if NUM_RE.search(a.query):
        hits, note = by_number(rows, a.query)
        hits.sort(key=lambda r: (r["type"] != JUDGMENT, r["date"] or ""))
    else:
        hits, note = by_parties(rows, a.query, a.source, a.refresh)  # already ranked
    if note:
        print(f"NOTE {note}")
    if not hits:
        print("NOT FOUND in the 2022 Supreme Court snapshot (lower courts, rulings after 2022 and many older rulings are not in it)")
        sys.exit(3)

    judgments = [r for r in hits if r["type"] == JUDGMENT]
    cases = {r["case"] for r in hits}
    print(f"{len(hits)} documents in {len(cases)} case(s)")
    for r in hits:
        print(show(r))

    if a.all:
        for r in hits:
            extract(r, a.source, a.out)
    elif len(cases) == 1 and len(judgments) == 1:
        extract(judgments[0], a.source, a.out)
    elif len(cases) == 1 and len(hits) == 1:
        extract(hits[0], a.source, a.out)
    else:
        print("CHOOSE several candidates, run again with --id")
        sys.exit(2)


if __name__ == "__main__":
    main()
