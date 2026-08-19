---
name: daily-literature-monitor
description: "Automated daily paper collection from PubMed + bioRxiv with LLM relevance filtering and scheduled digest delivery. Use when the user wants a daily briefing of new papers from selected journals, needs noise-filtered literature monitoring across multiple research topics, or asks to set up a literature digest pipeline."
license: MIT
metadata:
  author: Hermes Agent
  version: 1.0.0
  tags:
    - Literature
    - Automation
    - PubMed
    - bioRxiv
    - Cron
    - Research
    - Digest
---

# Daily Literature Monitor

Automated daily pipeline: collect papers from multiple sources → LLM filters by relevance → deliver curated digest. Designed for researchers who want a daily briefing of new papers in their field without manual searching.

> ⚠️ **通用化说明**：本 skill 的默认配置（期刊列表、分类章节、关键词库、输出语言）均为**通用示例**，不绑定任何个人研究方向。**部署后第一步是自定义这些配置**——见 `README.md` 的 "Customization Guide"。
>
> ⚠️ **cron 筛选必读**：采集窗口跨日重叠，筛选前必须读上一日 `digest.md` 剔除已覆盖论文（否则同篇连发两天）；digest 校验一律用 Python，禁止 shell grep 匹配含 emoji 的 pattern（变体选择符触发安全扫描导致命令挂起）；`normalize-digest.py` 的章节正则已同时兼容 `**━━ 名称 (N)**━━` 与 `**━━ 名称 (N) ━━**` 两种收尾格式。详见 `references/cron-digest-operational-lessons.md`。

## When to Use

- User wants a daily digest of papers from target journals + bioRxiv preprints
- User has defined research interests and wants LLM to filter noise
- User wants scheduled delivery (cron / scheduler / recurring task)
- User needs to monitor multiple disparate topics from high-volume journals
- User wants summaries grouped by research topic (language per user preference)

## Architecture

```
⏰ Scheduled trigger (daily)
│
├─ 1. Python data collector
│   ├─ PubMed: ALL papers from target journals (wide, no keyword filtering)
│   └─ bioRxiv: papers in relevant categories, filtered by keywords
│   Output: JSON with title, abstract, journal, DOI, link, tier
│
├─ 2. LLM relevance filter
│   Input: all candidate papers (title + abstract)
│   Classify: keyword scoring → candidate pool (30-40 papers)
│   Curate: LLM selects 15-25 papers with semantic judgment
│   Prioritize: journal tier × topic relevance × novelty
│   Output: 15-25 papers with annotations
│
├─ 3. Formatted delivery + archive
│   Group by topic category
│   Markdown digest → chat/email/any delivery channel
│   Save selected.json + digest.md in date directory
│
└─ 4. (Optional) Knowledge-base integration
    Individual notes per paper (e.g. Obsidian vault)
    Works even when delivery channel is down
```

## Target Journals (default)

| Tier | Journals |
|---|---|
| 1 | Cell, Nature, Science |
| 2 | Nat Biotechnol, Nat Methods, Neuron, Nat Genet, Nat Neurosci, Nat Commun, Science Advances, Current Biology, Molecular Cell, Developmental Cell, eLife, PNAS, Genome Res, Nucleic Acids Res |
| 3 | Nat Ecol Evol, Mol Biol Evol, Genome Biol, Cell Genom, Cell Syst, Nat Struct Mol Biol, Nat Med, Cell Host Microbe, PLoS Genet |
| 4 | bioRxiv (keyword pre-filtered) |

The actual journal list lives in the collector script (`templates/collector-template.py`) in the `JOURNALS` dict — always trust the collector script over this document. Edit that dict to change monitored journals.

Daily output: 15-25 selected papers, grouped by topic. Each paper gets a one-sentence summary and topic tags.

For high-impact journals (Cell, Nature, Science), the user's interests may appear in papers whose titles/abstracts don't contain obvious keywords. A paper about "chromatin remodeling in neural progenitors" might be highly relevant to "gene regulation during brain development" without containing those exact words. LLM semantic filtering catches these — keyword pre-filtering would miss them.

For bioRxiv (high volume, lower signal), keyword pre-filtering is still used to keep the candidate pool manageable.

## Customization Points (must-do on first deploy)

1. **Journals** → edit `JOURNALS` dict in collector script
2. **bioRxiv categories** → edit `BIORXIV_SUBJECTS` in collector script
3. **bioRxiv keyword filter** → edit `BIORXIV_KEYWORDS` in collector script
4. **Digest sections + keywords** → edit `references/keyword-banks.md` (category names, emoji, keyword lists)
5. **Section order validation** → edit `SECTION_ORDER` / `EMOJI_MAP` in `scripts/normalize-digest.py`
6. **Summary language** → user preference (default examples use Chinese; change freely)
7. **Output directory** → `--out-dir` flag or `LITMON_OUTPUT_DIR` env var (default `~/literature/daily_papers` — change to your own path)

## Title Searching Pitfall: Non-Breaking Spaces in PubMed Titles

PubMed titles sometimes contain Unicode non-breaking space characters (`\xa0`, `\u00a0`) that make substring matching fail. A `find_paper()` helper that searches by title fragment will silently return `None` because `"satellite expansion"` does not match `"satellite\xa0expansion"`.

**Fix:** Normalize whitespace in titles before matching:

```python
def find_paper(title_fragment, papers):
    for p in papers:
        raw_title = p.get("title", "")
        # Normalize all Unicode whitespace (including \xa0 / \u00a0) to regular spaces
        normal = re.sub(r'[\s\u00a0\u2000-\u200b\u2028\u2029]+', ' ', raw_title).strip()
        if title_fragment.lower() in normal.lower():
            return p
    return None
```

This pattern applies to any `find_paper()` or `is_dedup()` function that does substring matching against PubMed/bioRxiv titles. Always normalize whitespace first.

## Deduplication Against Previous Days

Check the previous day's `selected.json` for dedup (not all historical files). Rationale: papers that appeared 2+ days ago are already stale and unlikely to re-appear, and checking only yesterday minimizes false matches from similar-but-different papers.

```python
import json
from pathlib import Path

yesterday = (datetime.date.today() - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
ypath = Path(f'<OUTPUT_DIR>/{yesterday}/selected.json').expanduser()
yesterday_titles, yesterday_dois, yesterday_pmids = set(), set(), set()
if ypath.exists():
    with open(ypath) as f:
        ydata = json.load(f)
    for p in ydata['papers']:
        t = p.get('title','').strip().lower().rstrip('.')
        if t: yesterday_titles.add(t)
        d = p.get('doi','').strip().lower().rstrip('.')
        if d: yesterday_dois.add(d)
        pmid = p.get('pmid','')
        if pmid: yesterday_pmids.add(pmid)
```

**Title normalization trap:** PubMed titles often end with a trailing period (`.`), while bioRxiv titles do not. Always strip trailing periods AND whitespace from both cached titles and new paper titles before comparing:

```python
def norm_title(t):
    t = t.strip().rstrip('.').rstrip()
    return t.lower()
```

**Colon-without-space trap:** bioRxiv titles sometimes have colons without a following space (e.g., `"see point what they see:A behavioral study"`). Fix with regex before dedup comparison:

```python
def fix_colon(t):
    return re.sub(r':([A-Z])', r': \1', t)
```

**PMID extraction from stored links:** `selected.json` links like `https://pubmed.ncbi.nlm.nih.gov/42216562/` end with a trailing slash. Always use `link.rstrip('/').split('/')[-1]` — `link.split('/')[-1]` returns an empty string.

#### Manual Curation Dedup (when curating by eye, not by script)

The programmatic `is_dedup()` only helps if you actually run it. When doing manual curation, ALSO read the previous day's `digest.md` (not just `selected.json`) and mark already-featured papers as you scan. **Expect a meaningful fraction of first-pass picks to be duplicates** (in one 305-paper run, 5 of ~30 first-pass candidates (~17%) had already been featured the day before — mostly bioRxiv preprints re-posted/re-collected in the overlapping window). Consequence: **don't shortlist exactly 15-25 candidates — shortlist 30+ so you can swap out duplicates without re-scanning the pool.** When a candidate is dropped, replace it from the tier-2/3 published papers you skipped, not by loosening relevance.

Two-step pattern that worked (305-paper pool):
1. First scan: print `[idx] | source | journal | title` + first ~300 chars of abstract for the whole pool in chunks of ~50-100 via a Python loop, shortlist by index. The abstract snippet is what lets you judge relevance in one pass without opening every full abstract.
2. Second pass: pull FULL abstracts ONLY for the shortlisted indices, write summaries from those, then cross-check the shortlist against yesterday's `digest.md` titles and swap out duplicates.

## Filtering Methodology (Hybrid Scoring + Manual Curation)

Score each paper against research interest categories using topic-specific keyword lists:

```
score = Σ(topic_keyword_hits × weight) × tier_factor + special_focus_bonus
```

- **Title match weight**: 5× (title is high-signal)
- **Abstract match weight**: 1×
- **Tier factor**: tier 1 = 4.0, tier 2 = 3.0, tier 3 = 2.0, tier 4 = 1.0
- **Special focus bonus**: keywords from the user's core interests get +5 for title match, +1 for abstract match
- **Minimum threshold**: combined_score ≥ 3.0 to enter candidate pool

## Scoring Failure Recovery

**When >100 papers have scores ≥3.0 (i.e., almost everything matches), the approach is fundamentally wrong.** This happens when ad-hoc keyword lists are too broad — every abstract contains some fraction of generic terms like "tool", "development", "evolution", "method", "visual", "data", "analysis", "pathway", "network", "model", "growth", "response", "role", "process", "activity", "change", "level", "factor", "state", "signal", "system".

**Recovery procedure:**

1. **Stop refining keywords.** Adding more exclusion rules to an already-swamped scoring pass is a losing game. The noise floor is too high.
2. **Biology-context pre-filter (fastest intermediate).** Apply a regex-based biology context check to the entire paper pool: scan for basic biological signal (cell, gene, protein, RNA, DNA, genome, transcription, chromatin, neuron, tissue, organoid, stem cell, etc.) in title + abstract. Papers without any biological signal are excluded — this eliminates chemistry, physics, materials, climate, geology, and engineering papers in one pass (a 295-paper pool → ~60-80 candidates).
3. **Score the surviving pool** using the keyword banks (`references/keyword-banks.md`). At this stage, the noise floor is low enough that keyword scoring produces 30-50 candidates, not 100+.
4. **Manual review** of the top 30-50 candidates to select 15-25 high-quality papers. Use the hardcoded PMID/title-key selection pattern if the keyword scores are still noisy.
5. **If keyword scores are still noisy after the biology pre-filter**, switch to hardcoded PMID/title-key manual curation:
   ```python
   selections = [
       ('pmid', '42270639', 'bioinfo', 'foundation-model single-cell'),
       ('title', 'Chromatin accessibility profiling reveals enhancer rewiring', 'regulation', 'chromatin ATAC-seq enhancer'),
   ]
   ```
   - For PubMed papers: use `pmid` as identifier (stable, unique, dedup-safe)
   - For bioRxiv papers: use a unique title substring as identifier (no PMID available)
   - Each entry carries: (id_type, id_value, area, tags_string)
   - Write a `find_paper()` function that matches by PMID or title substring against the raw.json `papers` list (use the whitespace-normalized version from the Title Searching Pitfall section)
   - Write an `is_dedup()` function that checks DOI + PMID + link + normalized title against yesterday's selected.json
   - **Title-only scan misses relevance; add an abstract snippet.** Print `[idx] | source | journal | title` plus the first ~300 chars of the abstract per line, chunked over the pool. With the snippet you can judge topic fit in the SAME pass. Then pull full abstracts only for the shortlisted indices. Caveat: the ~300-char snippet is enough to detect a false positive but not to write a quality summary — always fetch the full abstract for finalists.
   - **Write selections in section order** (see Digest Format section) so the digest comes out correctly without a separate sort step
6. **Use the curated reference files.** `references/keyword-banks.md` and `references/false-positive-filters.md` contain tuned keyword lists that produce the correct 30-40 candidate pool. Do NOT construct keyword lists from scratch mid-session.
7. **Accept the manual curation cost.** With 60-80 candidates (after biology pre-filter), scanning titles takes ~3 minutes. This is still faster than trying to fix a broken scoring pass.

**What NOT to do:** Do not add more generic exclusion keywords. Do not lower the threshold below 3.0 when already swamped. Do not use tier multipliers (they amplify noise from high-tier journals). Do not add multi-word phrases containing stopwords.

## False-Positive Filtering (Critical)

Short/ambiguous keywords cause massive false positives. Apply these filters BEFORE scoring:

1. **Skip papers with no abstract** — News, editorials, and commentary from Nature/Cell/Science often have empty abstracts
2. **Skip news/opinion content** — Check title prefix for: "news", "briefing", "exclusive:", "podcast", "editorial", "obituary", "correction"
3. **Filter clinical trials** — If ≥2 clinical-trial keywords present (e.g., "phase ii" + "pembrolizumab"), skip
4. **Physics/engineering false positives** — Papers about optical physics, lasers, photonics, metamaterials, etc. falsely match physics-flavored keywords (e.g. "optic", "laser"). If ≥2 physics keywords present, skip. See `references/false-positive-filters.md` for the full list.
5. **Ambiguous short keywords trap**: short keywords have multiple meanings across fields (e.g., "HiC" = materials science vs genomics, "TAD" = clinical vs genomics). They should appear ONLY in multi-word phrases (e.g., "topologically associating domain") or be weighted lower. Build this list for every short keyword in YOUR keyword banks.

#### ⚠️ Short-Substring Keyword Catastrophe

Short substrings are the single most destructive false-positive pattern in the pipeline. The string "rod" (case-insensitive) appears as a substring in ~50% of English-language abstracts — matching "method", "period", "introduce", "corridor", "erode", "microdroplet", "historiography", "prodromal", and thousands more. In one 249-paper session, `"rod"` matched 96 papers (39% of all papers), of which exactly 1 was genuinely relevant.

**Never use short standalone keywords. Always use specific multi-word phrases for your own topics** (e.g. "transcription factor binding", "chromatin accessibility", "cell atlas"), and never match bare 2-4 letter acronyms without `\b` word boundaries.

See `references/false-positive-filters.md` for the complete list of proven filters.

## Data Collector Script

The Python script handles all API calls and outputs a JSON file. See `templates/collector-template.py` for a reusable, well-commented template that you can copy and customize.

Key design decisions:
- **PubMed `[pdat]`**: Use `YYYY/MM/DD[pdat]` for date filtering (most reliable format; avoid colon-range syntax which breaks in URL encoding)
- **efetch returns XML**: PubMed's efetch with `retmode=xml` returns XML, not JSON. Always use `resp.read().decode()` not `json.loads()` for efetch
- **bioRxiv API**: `https://api.biorxiv.org/details/biorxiv/YYYY-MM-DD/YYYY-MM-DD/cursor` returns JSON with pagination via cursor
- **Deduplicate by DOI** after merging sources
- **Tier system**: journals hardcoded with impact tiers for LLM prioritization (tier 1: Cell/Nature/Science, tier 4: preprints)
- **CLI**: `python3 collector-template.py [--out-dir DIR] [--days N] [--date YYYY-MM-DD]`

## Digest Format (default)

### Section Order (default example)

The digest MUST use exactly this section order. Do NOT reorder based on which category has the most or highest-scoring papers. **Edit this list to match YOUR research topics** (and keep `scripts/normalize-digest.py` in sync):

1. 💻 生物信息学 (Bioinformatics)
2. 🔬 单细胞与空间 (Single-cell & Spatial)
3. 🧬 基因调控与发育 (Gene Regulation & Development)
4. 🌲 进化与基因组 (Evolution & Genomics)

**Extra sections:** Do NOT create sections beyond the configured list. If a paper doesn't fit any category, either (a) fold it into the closest matching category, or (b) if truly unique, place it at the end under the most relevant existing category with a clarifying tag. Inventing extra section headers causes format drift.

### Full Paper Entry Template

```
🆕 **{English title}**
📰 *{Journal}* | 🔗 [PubMed](link) / [bioRxiv](link)
📝 {One-sentence summary in user's preferred language}
🏷️ {Comma-separated tags in user's preferred language}
```

- Mark preprints with ⚠️预印本
- Skip sections with zero papers
- Summary must be a concise one-sentence takeaway of the core finding or method, written by the LLM — do not paste the English abstract
- Tags should reflect topic, method, and organism keywords

### Link Label Convention
- PubMed papers: `🔗 [PubMed](https://pubmed.ncbi.nlm.nih.gov/{PMID}/)`
- bioRxiv papers: `🔗 [bioRxiv](https://www.biorxiv.org/content/{DOI})` — use the full biorxiv.org URL, not api.biorxiv.org

### Journal Name Normalization
Raw JSON uses abbreviated names; the digest must use canonical display names. Common mismatches:
- `Sci Adv` (raw) ↔ `Science Advances` (display)
- `Proc Natl Acad Sci U S A` (raw) ↔ `PNAS` (display)
- `Elife` (raw) ↔ `eLife` (display)
- `Nat Commun` / `Sci Adv` / `Nat Ecol Evol` — already correct, no change needed

Always check `journal.lower()` for substring matching, NOT exact match.

### Pre-Delivery Checklist (MANDATORY — run before output)

1. **Section header format** — must be `**━━ {emoji} {name} (N)**━━`, NOT markdown headers (`## Section`), NOT `---` delimiters
2. **Section order** — must match the configured section order exactly (sections with 0 papers skipped)
3. **Journal name normalization** — no raw `Elife`, `Proc Natl Acad Sci U S A`, `Sci Adv` strings; bioRxiv links must be full biorxiv.org URLs
4. **Counts match** — number of `🆕` entries in digest == `selected_count` in selected.json
5. **Preprint markers** — all bioRxiv entries carry ⚠️预印本
6. **Archive** — save `raw.json` (collector output) + `selected.json` + `digest.md` in `<OUTPUT_DIR>/<date>/`
7. **Run the normalizer** — `python3 scripts/normalize-digest.py <digest.md> --fix` catches the common format failures

## Obsidian Vault Integration (Optional)

If the user maintains an Obsidian vault (or similar knowledge base), optionally write per-paper notes and update index pages. See `references/obsidian-note-generation.md` for the code pattern. This is strictly optional — the core deliverable is the digest itself.

## References

| File | Purpose |
|---|---|
| `references/keyword-banks.md` | Tuned keyword lists per digest section (customize!) |
| `references/false-positive-filters.md` | Proven exclusion patterns for physics/engineering/clinical noise (customize!) |
| `references/multi-pass-filtering-workflow.md` | 3-pass filtering pattern for high-volume noisy days |
| `references/cron-digest-operational-lessons.md` | Real-run lessons: dedup, regex traps, validation scripts |
| `references/obsidian-note-generation.md` | Optional Obsidian note/index generation pattern |
| `references/verify-papers-before-sharing.md` | Official-API verification before recommending papers |
| `templates/collector-template.py` | Reusable PubMed + bioRxiv collector (customize JOURNALS/SUBJECTS/KEYWORDS) |
| `scripts/normalize-digest.py` | Pre-delivery format normalizer (edit SECTION_ORDER/EMOJI_MAP) |
