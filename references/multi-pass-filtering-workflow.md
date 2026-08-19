# Multi-Pass Filtering Workflow

This document captures a 3-pass filtering approach for high-volume days. It provides a reproducible pattern for screening 200-250 papers when keyword scoring produces noisy results.

## Overview

**Problem**: Single-pass keyword scoring on 249 papers produced 180 candidates with ≥3 score — the noise floor was too high because short keywords ("rod", "visual", "cell", "development") matched generic text in unrelated abstracts.

**Solution**: 3 passes of progressive refinement, executed entirely in Python (agent code block or local script):

```
Pass 1: Broad keyword match → 130 candidates (still noisy)
Pass 2: Domain-specific high-specificity keywords → identify genuine matches
Pass 3: Manual abstract review → final curation of 22 papers
```

## Pass 1: Broad Biology + Keyword Screening

**Goal**: Eliminate obvious non-biology papers (physics, chemistry, materials, engineering, climate) while capturing all potentially relevant papers.

**Approach**: Use broad biology-context keywords to filter. If ≥1 biology keyword matches, keep the paper.

```python
# Broad biology context check
bio_kw = ['cell', 'gene', 'protein', 'RNA', 'DNA', 'genome', 'transcription',
          'chromatin', 'neuron', 'tissue', 'organoid', 'stem cell',
          'mutant', 'evolution', 'development', 'receptor', 'synapse',
          'epigenom', 'transcriptom', 'proteom', 'metabolom',
          'single-cell', 'enhancer', 'promoter']

text = (title + ' ' + abstract).lower()
if any(kw in text for kw in bio_kw):
    keep = True
```

**What this eliminates**: Solar cells, electrocatalysis, skyrmions, spin Seebeck effect, supernovae, quantum transport, CO2 capture, power converters, coastal flooding, aerosol volatility, adhesion physics — typically 100-150 papers gone in one pass.

## Pass 2: Domain-Specific Keyword Matching

**Goal**: Assign papers to research domains with high specificity.

**Key insight**: Short keywords do NOT work. The string "rod" matches ~50% of all English abstracts. Always use multi-word phrases:

```python
# Correct approach — multi-word phrases only (generic examples; use YOUR phrases)
regulation_kw = [
    'transcription factor binding',  # ✓ specific
    'chromatin accessibility',       # ✓ specific
    'enhancer-promoter',             # ✓ phrase
    'cell atlas',                    # ✓ specific
    'single-cell rna',               # ✓ phrase
    'genome assembly',               # ✓ phrase
    'positive selection',            # ✓ phrase
    'alternative splicing',          # ✓ phrase
]

# WRONG approach — single short words that cause false positives
kw_bad = [
    'rod',      # ✗ matches "method", "period", "introduce", etc.
    'eye',      # ✗ matches "eyelash", "buckeye", "eye-tracking"
    'visual',   # ✗ matches "visual inspection", "visualization"
    'light',    # ✗ matches "light-weight", "light-emitting"
]
```

**Scoring (no tier multiplier)**:
- Each matched keyword: +2 for title match, +1 for abstract match
- Special focus bonus (your top topic): +5 per match
- Tier used as post-hoc tiebreaker only (+3 tier 1, +1 tier 2)
- No score from single-word short keywords

## Pass 3: Manual Curation by Abstract Reading

**Goal**: Select 15-25 papers that are genuinely relevant, eliminating false positives that passed Passes 1-2.

**Approach**: Print PMID + title + first 500 chars of abstract for each candidate, read them, and curate:

```python
for p in candidates:
    print(f"PMID: {p.get('pmid','')} | {p['journal']} | T{p['tier']}")
    print(f"Title: {p['title']}")
    print(f"Abstract: {p.get('abstract','')[:500]}")
```

**Curation rules applied in this session (generic examples):**
1. A paper mentioning a topic keyword in genuine context → keep under that category
2. A paper mentioning a keyword only in passing (e.g., as a model system) → drop
3. A paper about the topic in a distant organism/system → drop (unless a comparative/evolutionary angle)
4. A paper matching only an ambiguous term with no other interest signals → drop
5. A high-tier paper from another field that uses scRNA-seq → keep under 🔬 single-cell
6. bioRxiv papers with clearly relevant titles but no/missing abstract → tentative keep, verify title

## Output Interface

After manual curation, build the digest by matching against raw.json:

```python
# Use PMID for PubMed papers, title substring for bioRxiv (no PMID)
selections = [
    ('pmid', '42480528', 'bioinfo', 'protein language model MSA'),
    ('pmid', '42480525', 'regulation', 'enhancer domestication'),
    ('title', 'Single-cell characterization of immune infiltration', 'singlecell', 'scRNA-seq tumor'),
]

def find_paper(selections, papers):
    """Find papers matching PMID or title substring."""
    found = []
    for id_type, id_val, area, tags in selections:
        for p in papers:
            if id_type == 'pmid' and p.get('pmid') == id_val:
                found.append((p, area, tags))
                break
            elif id_type == 'title' and id_val.lower() in p.get('title', '').lower():
                found.append((p, area, tags))
                break
    return found
```

## When to Use This Pattern

- **Primary**: When keyword scoring produces >100 candidates (signal-to-noise too low)
- **Alternative**: When the `references/keyword-banks.md` and `references/false-positive-filters.md` would take too long to load and tune mid-session
- **Not needed**: When the keyword banks produce the expected 30-40 candidate pool (load them as references during setup)

## Key Lessons

1. **Short substrings are the worst keyword pattern** — e.g. "rod" matched 96/249 papers, only 1 genuine hit. Always use multi-word phrases.
2. **Tier multipliers amplify noise** — using tier as a score multiplier (×4 for Nature) gives physics/engineering papers an unfair boost when they happen to contain coincidental keyword overlaps. Use tier as post-hoc tiebreaker or flat bonus.
3. **Read abstracts before deciding** — the title alone is often misleading. A paper titled "Using deep learning to analyze..." might be about clinical MRI, not genomics. Abstract reading in Pass 3 catches this.
4. **Use a Python code block with standard library** — reading raw.json via `with open() as f: data = json.load(f)` avoids terminal output caps when dumping large JSON.
