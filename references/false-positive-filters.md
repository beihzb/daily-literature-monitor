# False-Positive Filter Lists

Proven exclusion patterns to prevent physics, engineering, and clinical papers from contaminating topic scoring. These are **methodology, not a personal research profile** — the specific examples below are generic; build the same tables for YOUR own keyword banks.

> ⚙️ **通用化说明**：核心方法论是通用的——**短单词子串匹配会造成大量假阳性，必须用短语 + 共现约束**。以下是通用示例规则；部署后请按自己的关键词库为每个易误报的短词建立同样的"必须短语 + 共现约束"规则。

## Physics/Engineering Keywords to Filter

Applied to combined title+abstract text. If ≥2 matches found, the paper is excluded (these terms almost never co-occur in biology papers).

```
photonic, waveguide, nanocavity, silicon photonic,
optical Kerr, femtosecond laser, terahertz, plasmonic,
metamaterial, dielectric resonator, upconversion,
nonlinear optic, optical switch, all-optical,
laser, nanophotonic, electrooptic,
photonic crystal, optical fiber, optoelectronic,
solar cell, perovskite solar, photovoltaic,
LiDAR, optical coherence tomography, OCT imaging,
photoacoustic, Raman spectroscop, optical trapping,
diffractive optical, metalens, holograph, speckle, wavefront,
optical computing, photonic neural
```

## News/Opinion/Editorial Title Prefixes

Skip papers where the first 60 characters of title contain:

```
"news", "briefing", "exclusive:", "podcast", "editorial",
"obituary", "correction", "retraction", "feature:",
"interview", "q&a", "book review", "world view"
```

## Clinical Trial Keywords

Skip papers with ≥2 matches (these are clinical, not basic research):

```
phase ii, phase iii, randomized trial, clinical trial,
placebo-controlled, double-blind, metastatic breast,
melanoma, non-small cell lung, hepatocellular carcinoma,
colorectal cancer, pancreatic cancer, ovarian cancer,
gastric cancer, bladder cancer, renal cell carcinoma,
prostate cancer, leukemia, lymphoma, multiple myeloma,
covid-19, sars-cov-2, pembrolizumab, nivolumab,
atezolizumab, durvalumab, ipilimumab, bevacizumab
```

## Keyword-Matching Pitfalls (Regex Boundaries)

Short keywords (≤3 chars) that appear as substrings cause massive false positives. Use word-boundary regex (`\bkeyword\b`) or only match them in multi-word phrases:

| Short Keyword | False-match examples | Fix |
|---|---|---|
| AI | "maintenance", "domain", "explain", "mountain", "captain", "contain", "bargain" | Never match bare "AI". Use only phrase "artificial intelligence" or `\bAI\b` with word boundaries |
| LLM | "hallmarks" (contains "llm"), "illuminate" (contains "llm") | Use `\bLLM\b` or spell out "large language model" |
| RNA | "internal", "external", "maternal", "paternal", "governance" | Use "non-coding RNA", "RNA-binding protein", "single-cell RNA" phrases |
| HiC | materials science papers | Use "Hi-C" or require 3D-genome context |
| TAD | clinical contexts (thyroid eye disease) | Require "topologically associating domain" or 3D-genome context |

**Implementation rule**: In the keyword scoring code, always use `\b` word boundaries for keywords ≤4 characters. For 2-character bioinfo acronyms (AI, LLM, HiC, TAD), word boundaries are **mandatory** — without them these match as substrings in common words like "hallmarks", "maintenance", "domain", contaminating the entire scoring pass. **The same trap applies to any short keyword in YOUR banks** — audit them all before scoring.

## Ambiguous Common Terms

These terms match common interests but also appear in unrelated biology/medicine papers. Papers matching ONLY these terms (with no other interest signals) should be manually reviewed, not auto-selected:

| Term | False-match context | Actual interest context |
|---|---|---|
| plasticity | macrophage plasticity, synaptic plasticity (unrelated) | developmental plasticity, phenotypic plasticity |
| comparative | "comparative effectiveness" (clinical trials) | comparative genomics |
| transcriptional | ubiquitous in cancer/immunology papers | cis-regulatory, enhancer, promoter context |
| evolution (general) | "clonal evolution" in cancer, chemical evolution, geological evolution | molecular evolution, phylogenetics |
| evolution (climate) | "Evolution of Southern Hemisphere Westerly", climate evolution — geology/meteorology papers | biological evolution, molecular evolution |
| conserved | "conserved response" to stress/injury, "conserved metabolic pathway" (yeast cell biology not comparative) | conserved non-coding elements, conserved developmental mechanisms, cross-species conservation |
| morphology | "tumor morphology" | morphogenesis, tissue morphology |
| single-cell | cancer scRNA-seq (unrelated field) | developmental/neural scRNA-seq |
| neural | "neural network" (AI/ML papers) | biological neural circuits |
| development | "drug development" | embryonic development |
| pathway | "signaling pathway" (generic cancer) | developmental signaling pathways |
| network | "protein-protein interaction network" (generic) | gene regulatory network, neural circuit |

**Rule**: If a paper's only match is one of these ambiguous terms AND the paper is from a clinical/immunology/cancer context, reduce score by 2-3 points or skip. Require ≥1 specific term (e.g., "enhancer", "ATAC-seq", "morphogenesis", "cell atlas") for auto-acceptance.

**Specific patterns observed in real runs (generic lessons):**
- "conserved" in paper "Hsp70 is phosphorylated in a conserved response to DNA damage" → yeast cell biology, NOT comparative/evolutionary. Filter: if "conserved" appears with yeast context and no developmental terms, score as evo 0.
- "evolution" in paper "Evolution of Southern Hemisphere Westerly asymmetry since the Early Miocene" → climate science, NOT biological evolution. Filter: check if abstract mentions wind, climate, precipitation alongside evolution → exclude.
- A perception-related keyword matched a materials-science paper about structural color across the visible spectrum → optics/materials, NOT the biology topic. Check the abstract's subject domain before accepting.

## Category-Specific Zero-Day Handling

Some days produce ZERO papers in a given category (e.g., 207 total papers but ZERO in a topic category). Guidelines:

1. **Empty categories are normal.** Do NOT force-fit unrelated papers into empty categories.
2. **For tangential papers** (one sentence mentioning a topic-related term in the abstract), still include them in the correct category but note in the digest that coverage is thin.
3. **Accept that some days are lean.** The digest quality is better with 18 good papers across 4 categories than 23 papers across 6 where 2 categories are forced.

## Proven Effectiveness

From a real run: 185 papers collected → 101 survived keyword scoring → 30 passed ≥3.0 threshold → 20 manually curated. The physics filter eliminated ~12 false positives that would have ranked in the top 30 due to coincidental substring matches in non-bio contexts.

From another run: 39 papers collected → auto-scoring inflated a liver fibrosis paper (matched "plasticity") and an enzyme encapsulation paper (matched "comparative"). Manual override dropped both. The ambiguous-terms table above covers these patterns.

From a high-volume run: 207 papers → 111 survived keyword scoring → 23 manually curated. Key patterns discovered:
- "evolution" in climate/geology papers must be filtered (3 papers from this run)
- "conserved" in yeast/single-cell-biology papers is NOT comparative/evolutionary (2 papers)
- a perception-related keyword matched materials-science "visible spectrum" papers
- a short substring keyword matched a fiber-microelectrode materials paper (1 of 96 matches was genuinely relevant)