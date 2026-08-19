#!/usr/bin/env python3
"""
Template: Daily paper collector (PubMed + bioRxiv).
Customize JOURNALS, BIORXIV_SUBJECTS, and BIORXIV_KEYWORDS for your use case.
Output: JSON file with papers ready for LLM filtering.

Requires: Python 3.8+ (standard library only — urllib).
NCBI E-utilities and bioRxiv API are free and need no API key.
"""

import argparse
import json, os, re, sys, time, urllib.request, urllib.parse
from datetime import datetime, timedelta, timezone

# ── CUSTOMIZE THESE ─────────────────────────────────────
# Where to write raw_<date>.json. Override with --out-dir or $LITMON_OUTPUT_DIR.
# The directory itself is created in main() once the effective path is known.
OUTPUT_DIR = os.path.expanduser(os.environ.get("LITMON_OUTPUT_DIR", "~/literature/daily_papers"))

# Journals to monitor: {name: tier} (1=top, 2=high, 3=good) — generic example
JOURNALS = {
    "Cell": 1, "Nature": 1, "Science": 1,
    "Neuron": 2, "Nat Genet": 2, "Nat Methods": 2,
    # Add yours...
}
JOURNAL_QUERY = " OR ".join(f'"{j}"[Journal]' for j in JOURNALS)

# bioRxiv categories to include (generic example subjects)
BIORXIV_SUBJECTS = {
    "bioinformatics", "neuroscience", "genetics",
    "genomics", "molecular-biology",
}

# bioRxiv keyword pre-filter (lowercase, matched against title+abstract)
BIORXIV_KEYWORDS = [
    "evolution", "developmental", "single-cell", "genome",
    # Add yours...
]
# ─────────────────────────────────────────────────────────


def http_get_json(url, timeout=30, retries=3):
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "literature-monitor/1.0 (educational use)"})
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return json.loads(resp.read())
        except Exception:
            if attempt == retries - 1:
                raise
            time.sleep(2 ** attempt)


def http_get_text(url, timeout=30, retries=3):
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "literature-monitor/1.0 (educational use)"})
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.read().decode("utf-8", errors="replace")
        except Exception:
            if attempt == retries - 1:
                raise
            time.sleep(2 ** attempt)


def strip_xml(text):
    if not text:
        return ""
    text = re.sub(r"<[^>]+>", "", text)
    for e, c in [("&amp;", "&"), ("&lt;", "<"), ("&gt;", ">"), ("&quot;", '"')]:
        text = text.replace(e, c)
    return re.sub(r"&\w+;", " ", text).strip()


def matches_keywords(text):
    t = text.lower()
    return any(kw.lower() in t for kw in BIORXIV_KEYWORDS)


def collect_pubmed(date_str: str) -> list:
    """ALL papers from target journals on a date. No keyword filtering."""
    query = f'({JOURNAL_QUERY}) AND {date_str}[pdat]'

    # Search
    params = urllib.parse.urlencode({
        "db": "pubmed", "term": query, "retmax": 200,
        "retmode": "json", "sort": "pubdate", "datetype": "pdat",
    })
    search = http_get_json(
        f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?{params}"
    )
    idlist = search.get("esearchresult", {}).get("idlist", [])
    if not idlist:
        return []

    # Summaries
    papers_by_id = {}
    for i in range(0, len(idlist), 50):
        batch = idlist[i:i+50]
        params_s = urllib.parse.urlencode({
            "db": "pubmed", "id": ",".join(batch), "retmode": "json",
        })
        details = http_get_json(
            f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?{params_s}"
        )
        for uid in batch:
            rec = details.get("result", {}).get(uid, {})
            if not rec or "error" in rec:
                continue
            doi = rec.get("elocationid", "").replace("doi: ", "")
            if not doi:
                for aid in rec.get("articleids", []):
                    if aid.get("idtype") == "doi":
                        doi = aid.get("value", "")
                        break
            papers_by_id[uid] = {
                "source": "pubmed", "pmid": uid,
                "title": strip_xml(rec.get("title", "")),
                "journal": rec.get("source", ""),
                "pubdate": rec.get("pubdate", ""),
                "doi": doi,
                "link": f"https://pubmed.ncbi.nlm.nih.gov/{uid}/",
                "tier": JOURNALS.get(rec.get("source", ""), 3),
                "abstract": "",
            }
        time.sleep(0.35)

    # Abstracts via efetch (XML, NOT JSON!)
    for i in range(0, len(idlist), 20):
        batch = idlist[i:i+20]
        params_a = urllib.parse.urlencode({
            "db": "pubmed", "id": ",".join(batch),
            "rettype": "abstract", "retmode": "xml",
        })
        xml_text = http_get_text(
            f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?{params_a}"
        )
        articles = re.split(r"<PubmedArticle>", xml_text)
        for art in articles:
            pmid_match = re.search(r"<PMID[^>]*>(\d+)</PMID>", art)
            if not pmid_match:
                continue
            pmid = pmid_match.group(1)
            if pmid not in papers_by_id:
                continue
            abs_matches = re.findall(
                r"<AbstractText[^>]*>(.*?)</AbstractText>", art, re.DOTALL
            )
            papers_by_id[pmid]["abstract"] = strip_xml(" ".join(abs_matches))
        time.sleep(0.35)

    return list(papers_by_id.values())


def collect_biorxiv(date_start: str, date_end: str) -> list:
    """bioRxiv preprints filtered by category + keywords."""
    papers, cursor, seen = [], 0, set()
    while True:
        url = f"https://api.biorxiv.org/details/biorxiv/{date_start}/{date_end}/{cursor}"
        try:
            data = http_get_json(url)
        except Exception:
            break
        collection = data.get("collection", [])
        if not collection:
            break
        for item in collection:
            doi = item.get("doi", "")
            if doi in seen:
                continue
            seen.add(doi)
            if item.get("category", "").lower().strip() not in BIORXIV_SUBJECTS:
                continue
            title = item.get("title", "").strip()
            abstract = item.get("abstract", "").strip()
            if not matches_keywords(title + " " + abstract):
                continue
            papers.append({
                "source": "biorxiv",
                "biorxiv_id": doi.split("/")[-1] if doi else "",
                "title": title, "journal": "bioRxiv",
                "pubdate": item.get("date", ""), "doi": doi,
                "link": f"https://www.biorxiv.org/content/{doi}v1" if doi else "",
                "abstract": abstract,
                "category": item.get("category", ""), "tier": 4,
            })
        next_cur = data.get("messages", [{}])[0].get("cursor", 0)
        if next_cur == 0 or len(collection) < 100:
            break
        cursor = next_cur
        time.sleep(0.5)
    return papers


def main():
    parser = argparse.ArgumentParser(description="Daily literature collector (PubMed + bioRxiv)")
    parser.add_argument("--out-dir", default=None, help="Output directory (default: OUTPUT_DIR above or $LITMON_OUTPUT_DIR)")
    parser.add_argument("--days", type=int, default=2, help="Days of history to collect (default: 2)")
    parser.add_argument("--date", default=None, help="Collect for a specific date YYYY-MM-DD (overrides --days)")
    args = parser.parse_args()

    if args.out_dir:
        global OUTPUT_DIR
        OUTPUT_DIR = args.out_dir

    # Create the effective output dir only after --out-dir is applied, so a
    # bare `--out-dir` argument never crashes module import with mkdir errors.
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    tz = timezone(timedelta(hours=8))
    now = datetime.now(tz)

    if args.date:
        d = datetime.strptime(args.date, "%Y-%m-%d").replace(tzinfo=tz)
        days_to_collect = [d]
    else:
        days_to_collect = [now - timedelta(days=days_ago) for days_ago in range(1, args.days + 1)]

    all_papers = []
    for d in days_to_collect:
        ds = d.strftime("%Y/%m/%d")
        try:
            all_papers.extend(collect_pubmed(ds))
        except Exception as e:
            print(f"PubMed {ds}: {e}", file=sys.stderr)
        ds_bx = d.strftime("%Y-%m-%d")
        try:
            all_papers.extend(collect_biorxiv(ds_bx, ds_bx))
        except Exception as e:
            print(f"bioRxiv {ds_bx}: {e}", file=sys.stderr)

    # Deduplicate
    seen, unique = set(), []
    for p in all_papers:
        key = p.get("doi") or p.get("title", "")
        if key and key not in seen:
            seen.add(key)
            unique.append(p)

    unique.sort(key=lambda x: (x["tier"], 0 if x["source"] == "pubmed" else 1))

    out = os.path.join(OUTPUT_DIR, f"raw_{now.strftime('%Y-%m-%d')}.json")
    with open(out, "w") as f:
        json.dump({
            "date": now.strftime("%Y/%m/%d"),
            "total": len(unique),
            "sources": {
                "pubmed": sum(1 for p in unique if p["source"] == "pubmed"),
                "biorxiv": sum(1 for p in unique if p["source"] == "biorxiv"),
            },
            "papers": unique,
        }, f, ensure_ascii=False, indent=2)
    print(out)


if __name__ == "__main__":
    main()