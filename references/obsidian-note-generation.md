# Obsidian Note Generation & Index Update Pattern

Code pattern for generating individual literature notes and updating index pages from `selected.json`. This is an **optional integration** — skip if you don't use Obsidian. Run as a Python code block after the digest is finalized.

> Replace all `<VAULT_PATH>` placeholders below with your actual Obsidian vault path (e.g. `~/research`). Category names and tags in the examples are the **generic default sections** — adapt them to your own digest categories.

## Tag Generation (Category-Based)

The recommended approach maps each paper's assigned category to tags, then adds content-specific tags by keyword matching in title+abstract:

```python
def make_tags(cat, text):
    tags = []
    t = text.lower()
    if cat == "生物信息学":
        tags.extend(["bioinformatics", "method"])
        if "foundation model" in t or "llm" in t: tags.append("foundation-model")
        if "single-cell" in t or "scatac" in t: tags.append("single-cell")
    elif cat == "单细胞与空间":
        tags.append("single-cell")
        if "spatial" in t: tags.append("spatial-transcriptomics")
        if any(kw in t for kw in ["method","algorithm","model"]): tags.append("method")
        if "atlas" in t: tags.append("cell-atlas")
    elif cat == "基因调控与发育":
        tags.extend(["gene-regulation", "development"])
        if "enhancer" in t: tags.append("enhancer")
        if "chromatin" in t: tags.append("chromatin")
        if "transcription factor" in t: tags.append("transcription-factor")
        if "epigen" in t: tags.append("epigenomics")
        if "single-cell" in t: tags.append("single-cell")
        if "stem cell" in t or "ipsc" in t: tags.append("stem-cell")
    elif cat == "进化与基因组":
        tags.extend(["genomics", "evolution"])
        if "single-cell" in t: tags.append("single-cell")
        if "speciation" in t: tags.append("speciation")
        if "assembly" in t or "genome" in t: tags.append("genome")
    return ", ".join(tags)
```

## Keyword→Tag Normalization Map

Alternative approach using a keyword→tag lookup map (generic examples — build your own for your topics):

```python
tag_map = {
    "single-cell": "single-cell", "scRNA-seq": "single-cell",
    "scatac": "single-cell", "spatial transcriptom": "spatial-transcriptomics",
    "multi-omics": "multi-omics", "multiomic": "multi-omics",
    "cell atlas": "cell-atlas", "organoid": "organoid",
    "deep learning": "deep-learning", "neural network": "deep-learning",
    "foundation model": "foundation-model", "llm": "foundation-model",
    "enhancer": "regulatory", "promoter": "regulatory",
    "cis-regulatory": "regulatory", "chromatin": "chromatin",
    "epigen": "epigenetics", "transcription factor": "transcription-factor",
    "atac-seq": "epigenomics", "chip-seq": "epigenomics",
    "alternative splicing": "alternative-splicing", "splice": "alternative-splicing",
    "morphogen": "development", "morphogenesis": "development",
    "gastrulation": "development", "stem cell": "stem-cell", "ipsc": "stem-cell",
    "comparative genomic": "comparative-genomics", "phylogen": "phylogenetics",
    "positive selection": "selection", "synteny": "synteny",
    "molecular evolution": "molecular-evolution", "genome evolution": "genome-evolution",
    "genome assembly": "genome-assembly", "pangenome": "pangenome",
    "speciation": "speciation", "ortholog": "orthology",
    "protein structure": "structure-prediction", "alphafold": "structure-prediction",
    "electrophysiology": "electrophysiology", "neural circuit": "neural-circuit",
}
```

## Short Title Generation

```python
import re
def make_short_title(title, max_len=80):
    words = title.split()
    short = "-".join(words[:8])
    short = re.sub(r'[^a-zA-Z0-9\-]', '', short)
    short = re.sub(r'-+', '-', short)
    short = short.strip('-')
    if len(short) > max_len:
        short = short[:max_len].rstrip('-')
    return short
```

## Index Assignment Logic & Paths

Papers are assigned to index pages by category. The canonical paths (generic example):

| Category | Index Path |
|---|---|
| 生物信息学 | `<VAULT_PATH>/Index/Bioinformatics & Methods.md` |
| 单细胞与空间 | `<VAULT_PATH>/Index/Single-cell & Spatial.md` |
| 基因调控与发育 | `<VAULT_PATH>/Index/Gene Regulation & Development.md` |
| 进化与基因组 | `<VAULT_PATH>/Index/Evolution & Genomics.md` |

**Keyword triggers for additional assignments** (a paper may appear in multiple indexes; generic example — replace with your topic keywords):
| Index Page | Trigger Keywords in title+abstract |
|---|---|
| Bioinformatics & Methods | deep learning, foundation model, bioinformatic, computational biology, method, algorithm, pipeline, benchmark |
| Single-cell & Spatial | single-cell, single cell, scRNA-seq, scATAC-seq, spatial transcriptom, multi-omics, multiomic, cell atlas |
| Gene Regulation & Development | enhancer, promoter, cis-regulatory, chromatin, epigenom, ATAC-seq, ChIP-seq, transcription factor, regulatory, histone, DNA methylation, Hi-C, 3D genome, development, morphogenesis, stem cell, organoid |
| Evolution & Genomics | comparative genomics, phylogen, evolution, selection, synteny, pangenome, speciation, ortholog, genome assembly, molecular evolution |

Index entries use wikilink format (note name is the `.md` filename without extension):
```
- [[{YYYY-MM-DD} - {Short-Title}|{Display title (60-70 chars)}...]] — {Journal} — {keywords}
```

Before appending, check if the note name already exists in the index to avoid duplicates.

## File Structure

```
<VAULT_PATH>/
├── Literature/
│   └── {YYYY-MM-DD} - {Short-Title}.md
└── Index/
    ├── Bioinformatics & Methods.md
    ├── Single-cell & Spatial.md
    ├── Gene Regulation & Development.md
    └── Evolution & Genomics.md
```

## Verification

After generation, spot-check one note and one index page to verify wikilinks resolve correctly and YAML frontmatter is valid.