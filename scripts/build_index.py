#!/usr/bin/env python3
"""Build a lookup index of Israeli Supreme Court rulings.

Source: the Hugging Face dataset LevMuchnik/SupremeCourtOfIsrael (cases_all.parquet),
a 2022 snapshot of the Supreme Court website. Runs in the "Rulings index" GitHub Action,
because the Claude workspace cannot reach Hugging Face but can reach GitHub releases.

Usage: build_index.py <cases_all.parquet> <out_dir> [--min-decision-pages N]

Writes to out_dir:
  index.json.gz          metadata for every kept document (see FIELDS), used to identify a case
  heads.json.gz          the opening of each text (court, bench, parties), for search by parties,
                         because the website metadata often anonymises names that the text keeps
  shard-<year>-<b>.jsonl.gz  full texts, one JSON object per line {"id","case","type","date","text"}
                         keyed by the case year and the case number bucket (number // 1000)
  stats.json             counts per document type, kept and dropped, shard sizes
  NOTES.md               release notes

Kept documents: judgments (TypeCode 2), published versions (Type mentions פד"י),
and non technical decisions with at least --min-decision-pages pages
(many substantive leave-to-appeal rulings are decisions). English documents are dropped.
"""
import argparse
import collections
import datetime as dt
import gzip
import json
import os
import re
import sys

import pyarrow.parquet as pq

FIELDS = ["id", "case", "num", "year", "name", "parties", "type", "date", "pages", "judges", "shard"]
WANTED = [
    "Id", "CaseNum", "Year", "CaseDesc", "CaseName", "Type", "TypeCode", "Technical", "Pages",
    "VerdictsDt", "meta_verdict_dt", "meta_judge", "meta_side_nm", "text",
]
REQUIRED = {"Id", "CaseDesc", "Type", "text"}
CASE_RE = re.compile(r"(\d{1,6})\s*/\s*(\d{2}|\d{4})\s*$")
HEAD_CHARS = 700


def case_year(yy: str) -> int:
    y = int(yy)
    if len(yy) == 4:
        return y
    return 1900 + y if y > 30 else 2000 + y


def parse_case(desc: str, num, year):
    """Return (number, 4-digit case year) from 'ע"א 8146/13', falling back to the row fields."""
    m = CASE_RE.search(desc or "")
    if m:
        return int(m.group(1)), case_year(m.group(2))
    try:
        return int(num), int(year)
    except (TypeError, ValueError):
        return None, None


def iso_date(*vals):
    for v in vals:
        if v is None:
            continue
        if isinstance(v, (dt.datetime, dt.date)):
            d = v.date() if isinstance(v, dt.datetime) else v
        else:
            s = str(v)[:10]
            try:
                d = dt.date.fromisoformat(s)
            except ValueError:
                continue
        if d.year >= 1948:  # the dataset uses 1920 as a placeholder
            return d.isoformat()
    return None


def as_list(v):
    if v is None:
        return []
    if isinstance(v, str):
        try:
            v = json.loads(v)
        except ValueError:
            return [v]
    return [str(x).strip() for x in v if x is not None and str(x).strip()]


def clean_text(t: str) -> str:
    lines = [ln.rstrip() for ln in (t or "").replace("\r\n", "\n").replace("\r", "\n").split("\n")]
    t = "\n".join(lines).strip("\n")
    return re.sub(r"\n{4,}", "\n\n\n", t)


def keep(row, min_pages: int) -> bool:
    typ = row.get("Type") or ""
    if "אנגלית" in typ or "English" in typ:
        return False
    if row.get("TypeCode") == 2 or "פד" in typ:
        return True
    technical = str(row.get("Technical")).lower() in ("true", "1")
    pages = row.get("Pages") or 0
    return typ.startswith("החלט") and not technical and pages >= min_pages


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("parquet")
    ap.add_argument("out")
    ap.add_argument("--min-decision-pages", type=int, default=5)
    args = ap.parse_args()

    pf = pq.ParquetFile(args.parquet)
    names = set(pf.schema_arrow.names)
    missing = REQUIRED - names
    if missing:
        sys.exit(f"missing columns {sorted(missing)}; found {sorted(names)}")
    cols = [c for c in WANTED if c in names]
    print(f"rows {pf.metadata.num_rows}, columns used {cols}", flush=True)

    os.makedirs(args.out, exist_ok=True)
    writers = {}
    rows = []
    heads = []
    seen_ids = set()
    all_types = collections.Counter()
    kept_types = collections.Counter()
    no_case = 0
    empty = 0

    for batch in pf.iter_batches(batch_size=2000, columns=cols):
        for r in batch.to_pylist():
            typ = r.get("Type") or ""
            all_types[typ] += 1
            if not keep(r, args.min_decision_pages):
                continue
            text = clean_text(r.get("text"))
            if len(text) < 200:
                empty += 1
                continue
            num, year = parse_case(r.get("CaseDesc"), r.get("CaseNum"), r.get("Year"))
            if num is None:
                no_case += 1
                continue
            doc_id = int(r["Id"])
            if doc_id in seen_ids:
                continue
            seen_ids.add(doc_id)
            shard = f"{year}-{num // 1000}"
            date = iso_date(r.get("meta_verdict_dt"), r.get("VerdictsDt"))
            case = re.sub(r"\s+", " ", (r.get("CaseDesc") or "").strip())
            w = writers.get(shard)
            if w is None:
                w = writers[shard] = gzip.open(os.path.join(args.out, f"shard-{shard}.jsonl.gz"), "wt", encoding="utf-8", compresslevel=6)
            w.write(json.dumps({"id": doc_id, "case": case, "type": typ, "date": date, "text": text}, ensure_ascii=False) + "\n")
            rows.append([
                doc_id, case, num, year, (r.get("CaseName") or "").strip(),
                " | ".join(as_list(r.get("meta_side_nm"))), typ, date,
                int(r.get("Pages") or 0), ", ".join(as_list(r.get("meta_judge"))), shard,
            ])
            heads.append([doc_id, re.sub(r"\s+", " ", text[:2000]).strip()[:HEAD_CHARS]])
            kept_types[typ] += 1
        print(f"  scanned {sum(all_types.values())}, kept {len(rows)}, shards {len(writers)}", flush=True)

    for w in writers.values():
        w.close()

    rows.sort(key=lambda x: (x[3], x[2], x[0]))
    built = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%MZ")
    index = {"source": "huggingface.co/datasets/LevMuchnik/SupremeCourtOfIsrael", "built": built, "fields": FIELDS, "rows": rows}
    with gzip.open(os.path.join(args.out, "index.json.gz"), "wt", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, separators=(",", ":"))
    with gzip.open(os.path.join(args.out, "heads.json.gz"), "wt", encoding="utf-8") as f:
        json.dump({"built": built, "fields": ["id", "head"], "rows": heads}, f, ensure_ascii=False, separators=(",", ":"))

    sizes = {n: os.path.getsize(os.path.join(args.out, n)) for n in os.listdir(args.out) if n.endswith(".gz")}
    years = [r[3] for r in rows]
    stats = {
        "built": built,
        "documents_scanned": sum(all_types.values()),
        "documents_kept": len(rows),
        "dropped_short_text": empty,
        "dropped_no_case_number": no_case,
        "case_years": [min(years), max(years)] if years else None,
        "shards": len(writers),
        "largest_shard_bytes": max((v for k, v in sizes.items() if k.startswith("shard-")), default=0),
        "total_bytes": sum(sizes.values()),
        "types_all": dict(all_types.most_common()),
        "types_kept": dict(kept_types.most_common()),
    }
    with open(os.path.join(args.out, "stats.json"), "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)
    with open(os.path.join(args.out, "NOTES.md"), "w", encoding="utf-8") as f:
        f.write(
            "Full texts of Israeli Supreme Court rulings for lookup by case number or parties.\n\n"
            f"Built {built} from LevMuchnik/SupremeCourtOfIsrael (2022 snapshot of the Supreme Court website).\n"
            f"{len(rows)} documents in {len(writers)} shards, case years {stats['case_years']}.\n\n"
            "Use scripts/rulings/lookup.py to search it.\n"
        )
    print(json.dumps({k: v for k, v in stats.items() if not k.startswith("types")}, ensure_ascii=False, indent=2))
    print("kept types", dict(kept_types.most_common(12)))


if __name__ == "__main__":
    main()
