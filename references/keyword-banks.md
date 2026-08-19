# Category Keyword Banks (Generic Examples)

Generic example keyword lists for the daily literature monitor. These are
**placeholders that demonstrate the method — they are not a personal research
profile**. Replace them with YOUR own research topics before first use.

> ⚙️ **使用说明（必读）**：以下分类与关键词是通用示例，不绑定任何个人研究方向。
> 部署后请按自己的研究方向替换：增删分类章节、修改关键词、调整 emoji。
> 修改后**同步更新三处**，否则 digest 校验会失败：
> - `SKILL.md` 中 "Digest Format" 的章节顺序定义
> - `scripts/normalize-digest.py` 中的 `SECTION_ORDER` 和 `EMOJI_MAP`
> - 采集脚本中的 `BIORXIV_KEYWORDS`（`templates/collector-template.py`）

## Section Name/Emoji Mapping (default examples)

The emoji + section name at each header below is the canonical form for new digests.

| Section (default example) | English | Notes |
|---|---|---|
| 💻 生物信息学 | Bioinformatics | computational methods & tools |
| 🔬 单细胞与空间 | Single-cell & Spatial | single-cell / spatial omics |
| 🧬 基因调控与发育 | Gene Regulation & Development | gene regulation & development |
| 🌲 进化与基因组 | Evolution & Genomics | evolutionary & comparative genomics |

## Scoring Verification: Two-Pass Manual Curation

After the automated keyword scoring pass produces a candidate pool (typically 30-80 papers ranked by score), always do a **manual verification pass** before writing the digest:

1. **Print all candidates** with index number, score, tier, primary category, and title in one compact listing.
2. **Scan the titles quickly** — flag clearly irrelevant papers (physics, materials, clinical, economics) that slipped through the keyword filter.
3. **For borderline papers**, read the abstract to confirm genuine relevance.
4. **Collect PMIDs** of the confirmed relevant papers, organized by category.
5. **Build a separate selection for each category** — don't trust the auto-assigned primary_category blindly; a paper auto-classified into one category may actually belong elsewhere.

If the first pass is still noisy (scores inflated by generic terms), switch to hardcoded PMID selection: read all titles from raw.json in one visual scan, collect PMIDs manually, then write code to resolve metadata for only those PMIDs.

## 💻 生物信息学 (Bioinformatics) — example

```
deep learning, foundation model, graph neural network,
variational autoencoder, computational method,
bioinformatic tool, bioinformatic pipeline,
protein structure prediction, AlphaFold, ESMFold,
large language model, LLM, representation learning,
transfer learning, self-supervised learning,
contrastive learning, transformer model,
sequence-to-function, protein language model,
gene regulatory network, GRN inference,
cell-type annotation, cell atlas, trajectory inference,
pseudotime, RNA velocity, lineage tracing,
perturbation modeling, perturbation prediction,
batch correction, data integration, multi-modal,
information bottleneck, disentanglement,
cell segmentation, composite markers,

# Genomic foundation models / DNA language models
genomic foundation model, dna language model, genomic language model,
dna foundation model, genome language model,
dna tokenization, genome tokenization, genomic pretraining,
nucleotide transformer, dna-bert, evo, caduceus, hyenadna,
nucleotide language model, genome-scale model,
long-context dna, autoregressive dna, generative dna model,
dna self-supervised, genome self-supervised,
single-species foundation model, pangenome pretraining,
organism-specific language model, plant genomic model,
regulatory genomics prediction, sequence-to-expression model,
enformer, borzoi, selex, basset, deepstarr,
variant effect prediction, noncoding variant interpretation,
splicing prediction, splice-site prediction,
regulatory variant prioritization, genome-wide prediction,

# Single-cell foundation models and interpretability
single-cell foundation model, scGPT, scFoundation, Geneformer,
scBERT, cell type annotation, cell perturbation prediction,
sparse autoencoder, model interpretability, mechanistic understanding,
hidden representation, latent feature, feature interpretation,
cell embedding, gene embedding, attention mechanism,

# Clinical and speech AI models
self-supervised representation, clinical biomarker, speech biomarker,
multimodal clinical model, health outcome prediction,

# Bioinformatics tools / databases / platforms
database resource, webserver, web server, Galaxy platform,
computational workflow, reproducible analysis,
image registration, image analysis, image segmentation,
microscopy method, light-sheet microscopy, imaging technique,
protein motif prediction, short linear motif, SLiM,
drug discovery, virtual screening, high-throughput screening,
mass spectrometry, proteomics tool,
algorithm, optimization, Riemannian matching,
diffeomorphic matching, multi-scale registration,
normalization method, count data normalization,
single-cell method, spatial method,
benchmark, benchmarking dataset, reference dataset,
multi-platform comparison, cross-platform evaluation,
deep learning model, pretraining dataset,
scaling law, model evaluation
```

**Note:** This category absorbs method/tool papers that are primarily computational. If a paper presents a new method applied to single-cell data, judge by contribution: method development → 💻, biological discovery → 🔬.

## 🔬 单细胞与空间 (Single-cell & Spatial) — example

```
single-cell, single cell, single-cell rna, scRNA-seq, scRNAseq,
scATAC-seq, scATACseq, snRNA-seq, snRNAseq, snATAC-seq,
single-nucleus, single nucleus, single-nuclei, snRNA,
single-cell genomics, single-cell multi-omics,
spatial transcriptom, spatial transcriptomics,
spatially resolved, spatial genomics, spatial proteomics,
multi-omics, multiomic, multi-omics integration, multi-ome,
MERFISH, seqFISH, seqfish, Slide-seq, Visium, Stereo-seq,
Xenium, CosMx, GeoMx, spatial barcoding,
CITE-seq, multi-modal omics, multimodal,
cell atlas, cell type atlas, cell state atlas,
cellular heterogeneity, cell type diversity,
cell-cell communication, ligand-receptor,
niche analysis, spatial neighborhood,
microenvironment profiling, tumor microenvironment,
droplet-based, 10x Genomics, chromium,
single-cell profiling, single-cell resolution,
single-cell landscape, single-cell map,
single-cell analysis, single-cell method,
long-read single-cell, single-cell long-read,
scMultiome, scRNA+scATAC,
single-cell CRISPR, Perturb-seq, CROP-seq,
single-cell proteomics, single-cell metabolomics,
spatial metabolomics, imaging mass cytometry,
single-cell lineage tracing, single-cell phylogeny,
cell-cell interaction, ligand-receptor analysis,
single-cell atlas, cell atlas integration
```

## 🧬 基因调控与发育 (Gene Regulation & Development) — example

```
enhancer, promoter, cis-regulatory, cis regulatory,
transcription factor binding, transcription factor,
chromatin accessibility, ATAC-seq, ATACseq,
ChIP-seq, ChIPseq, epigenom, epigenetics,
regulatory element, regulatory region, regulatory landscape,
DNA methylation, histone modification, histone mark,
H3K27ac, H3K4me3, H3K27me3, CTCF binding,
open chromatin, DNase-seq, regulatory network,
super-enhancer, insulator element, chromatin loop,
enhancer-promoter, promoter-enhancer,
silencer element, repressor element,
nucleosome positioning, chromatin remodel,
pioneer factor, TF motif, binding motif,
polycomb, PRC1, PRC2, trithorax, BRD4,
non-coding RNA, lncRNA, long non-coding, microRNA, miRNA,
enhancer RNA (two-word phrase only — never bare "eRNA": it substring-matches
"internal", "external", "maternal", "paternal", "governance"),
alternative splicing, RNA processing, spliceosome,
RNA modification, m6A, epitranscriptom,
RNA-binding protein, RBP,
3'UTR, RNA stability, RNA localization,
chromatin state, topologically associating domain, TAD boundary,
Hi-C, 3D genome, genome architecture,
gene regulation, transcriptional regulation,
gene regulatory network, regulon,
cell fate specification, cell lineage, fate map,
stem cell, organoid, morphogenesis, embryonic development,
gastrulation, neural tube, limb bud, somite, germ layer,
morphogen, morphogen gradient,
BMP signaling, Wnt signaling, Shh signaling, FGF signaling,
hedgehog signaling, developmental timing, phenotypic plasticity
```

**Ambiguous keywords (generic guidance — build the same table for YOUR keywords):**
- `HiC` — also used in materials science. Use "Hi-C" or require 3D-genome context.
- `TAD` — also used in clinical contexts (thyroid eye disease). Require "topologically associating domain" or 3D-genome context.
- `transcription factor` — ubiquitous in cancer/signaling papers. Require ≥1 other regulatory keyword.
- `non-coding RNA` / `lncRNA` — many papers identify lncRNAs in cancer without studying mechanism. Require ≥1 mechanistic keyword (enhancer, chromatin, splicing, degradation, etc.).
- `conserved` — only count when the paper explicitly compares across species or discusses conserved non-coding elements.
- `development` — matches "drug development". Require embryonic/organismal context.
- `plasticity` — matches materials science / synaptic plasticity. Require developmental/organismal context.
- `regeneration` — matches liver/wound healing regeneration. Require developmental context (limb, amphibian, zebrafish, etc.).

## 🌲 进化与基因组 (Evolution & Genomics) — example

```
comparative genomics, comparative genomic,
phylogenom, positive selection,
gene family evolution, gene family expansion,
synteny, genome evolution, molecular evolution,
dN/dS, Ka/Ks, adaptive evolution,
purifying selection, natural selection,
evolutionary rate, evolutionary constraint,
ortholog, paralog, gene duplication,
gene loss, gene gain,
convergent evolution, parallel evolution,
evolutionary genomics, ancestral reconstruction,
phylogenetic analysis, phylogenetic tree,
molecular clock, divergence time,
speciation, introgression, hybridization,
pangenome, pan-genome, selective sweep,
conserved synteny, chromosomal evolution,
karyotype evolution, genome rearrangement,
whole genome duplication, polyploid,
horizontal gene transfer, codon usage,
substitution rate, mutation rate,
genome assembly, de novo assembly, genome annotation,
reference genome, genome quality, BUSCO, contig, scaffold,
long-read sequencing, PacBio, ONT, Oxford Nanopore,
HiFi sequencing, genome polishing, genome finishing,
telomere-to-telomere, T2T genome,
structural variant, copy number variation, CNV,
polygenic risk score, PRS, GWAS, genome-wide association,
population genetics, demographic history,
effective population size, linkage disequilibrium,
haplotype, allele frequency, selection scan,
pharmacogenomics, drug binding variant,
multi-population, trans-ancestry,
heritability, genetic correlation, pleiotropy,
shared heritability, genetic variance
```

**Ambiguous keyword guidance:**
- `evolution` — matches climate/geology papers ("evolution of the westerlies"). Require biological context (gene, genome, species, cell, organism).
- `comparative` — matches "comparative effectiveness" (clinical trials). Require genomics context.
- `morphology` — matches "tumor morphology". Require tissue/organismal/developmental context.
- `single-cell` — cancer scRNA-seq in an unrelated field still matches; judge by topic fit, not just the keyword.

## Special-Focus Bonus (optional)

You may define a `SPECIAL_FOCUS` list for your single most important research area. Matches get +5 for title, +1 for abstract. Keep it short (≤20 keywords; multi-word phrases preferred). Generic example:

```python
SPECIAL_FOCUS = [
    "chromatin accessibility", "single-cell atlas", "genome assembly",
    "transcription factor", "spatial transcriptom",
    # replace with YOUR core interests
]
```

## Dimension-Level Weighting (Alternative to Flat 5×/1×)

Instead of assigning 5× for title and 1× for abstract universally, assign each keyword a **content weight** (1-5) based on specificity, THEN multiply by a presence factor (3× for title, 1× for abstract). This captures that some keywords (e.g., "cell atlas", "H3K27ac") are more specific and should score higher within a category, while others (e.g., "morpholog", "visual") are broader and should contribute less.

```python
keyword_rules = [
    # (keyword, category, weight_1_5)
    ("chromatin accessibility", "基因调控与发育", 5),  # highly specific → high weight
    ("enhancer", "基因调控与发育", 4),
    ("single-cell atlas", "单细胞与空间", 4),
    ("transcription factor", "基因调控与发育", 3),
    ("cell atlas", "单细胞与空间", 2),   # broader
    ("evolution", "进化与基因组", 2),
    ("morpholog", "基因调控与发育", 1),  # generic → low weight
]
```

The per-paper score becomes:
```python
total = Σ(keyword_weight × presence_factor)
# presence_factor = 3 for title, 1 for abstract, 0 for none
```

This prevents generic terms from dominating while still contributing. Tier bonus (+8 tier 1, +4 tier 2) is applied as a post-hoc tiebreaker, not a multiplier.

## Scoring Weights

**Two-pass approach (recommended over tier multipliers).** Tier multipliers amplify false positives from high-impact journals. Do NOT use tier multipliers in the scoring pass.

| Signal | Weight |
|--------|--------|
| Title keyword match | 5× |
| Abstract keyword match | 1× |

**Tier as tiebreaker (post-scoring, optional):** After ranking by keyword score, break ties between papers with similar scores using:
- ⭐ (Cell/Nature/Science): +3 point tiebreaker bonus
- 🔥 (Nat Commun, PNAS, Nat Methods, eLife, Nat Neurosci, etc.): +1 point tiebreaker bonus
- 📝 (bioRxiv) or unlabeled: no bonus

Never use the raw JSON `tier` field directly — it assigns eLife tier=3 (would get no bonus) but per display rules eLife is 🔥 and deserves +1. See SKILL.md Digest Visual Format section for the journal-name-based badge lookup. Minimum threshold to enter the candidate pool: score ≥ 3.0.