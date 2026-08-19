# 📚 Daily Literature Monitor — 每日文献速递

**Automated daily literature monitoring for scientists: collect from PubMed + bioRxiv → LLM filters by relevance → deliver a topic-grouped digest.**

A ready-to-use **agent skill** that turns *"what's new in my field today?"* into a scheduled, noise-filtered, topic-grouped daily digest — no manual searching, no API keys, no third-party dependencies.

为科研人员打造的自动化学术文献监控技能：从 **PubMed + bioRxiv** 采集当天论文 → **LLM 按你的研究兴趣筛选去噪** → 生成按主题分类的中文/多语言速递并定时投递。

## Features — 功能特性

- 🗞️ **Two free data sources** — [PubMed E-utilities](https://www.ncbi.nlm.nih.gov/home/develop/api/) (all papers from your target journals, no keyword pre-filtering) + [bioRxiv API](https://www.biorxiv.org/about/api) (subject + keyword pre-filtered preprints). Both are free, keyless public APIs. / 双数据源免费采集（PubMed 精选期刊全量 + bioRxiv 分类预过滤）
- 🧠 **LLM relevance filtering** — keyword scoring builds a candidate pool, then the LLM applies semantic judgment to pick the 15–25 papers that matter for *your* topics. / LLM 语义筛选：15-25 篇精选 + 一句话摘要 + 主题标签
- 🗂️ **Topic-grouped digests** — papers are organized into your research categories with one-sentence summaries and tags; `raw.json` + `selected.json` archived for full traceability. / 按主题分类整理，三件套归档可追溯
- ⏰ **Scheduled delivery** — designed for cron / schedulers; deliver via chat, email, or plain file archive. / 定时投递：聊天 / 邮件 / 本地归档
- 🐍 **Zero third-party dependencies** — the collector is pure Python 3.8+ standard library (`urllib`). / 纯标准库，零第三方依赖
- 🧪 **Battle-tested** — the bundled reference docs are distilled from many real daily runs: false-positive traps, cross-day deduplication, regex pitfalls. / 文档沉淀了大量实战经验（误报陷阱、跨日去重、正则坑）
- 🧩 **Optional integrations** — Obsidian vault notes & index pages, official-API paper verification before sharing. / 可选：Obsidian 笔记 + 文献分享前官方 API 验真

## How It Works — 工作原理

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
```

## Repository Layout — 仓库结构

```
daily-literature-monitor/
├── SKILL.md                          # Main skill document (instructions for the agent)
├── README.md                         # This file: install + configuration guide
├── scripts/
│   └── normalize-digest.py           # Pre-delivery format validator/fixer
├── templates/
│   └── collector-template.py         # Data collector template (copy & customize)
└── references/
    ├── keyword-banks.md              # Example keyword banks per digest section
    ├── false-positive-filters.md     # Proven exclusion patterns (physics/clinical/short words)
    ├── multi-pass-filtering-workflow.md  # 3-pass screening pattern for noisy high-volume days
    ├── cron-digest-operational-lessons.md # Real-run lessons (dedup, regex traps, validation)
    ├── obsidian-note-generation.md   # Optional: Obsidian note/index generation
    └── verify-papers-before-sharing.md   # Official-API verification before recommending papers
```

## Requirements — 环境要求

| Dependency | Version | Notes |
|---|---|---|
| Python | 3.8+ | collector uses standard library only (`urllib`) — **no third-party packages** |
| Agent platform | any | Hermes / Claude Code / OpenClaw / Cursor, anything that loads skills |
| Network | direct to PubMed / bioRxiv | both APIs are free and need no API key |

## Installation — 安装

### 1. Install as an agent skill (recommended)

| Platform | Install |
|---|---|
| Hermes | `cp -r daily-literature-monitor ~/.hermes/skills/` |
| Claude Code | copy into `.claude/skills/` (project) or `~/.claude/skills/` (user) |
| OpenClaw | `openclaw skills install ./daily-literature-monitor --as daily-literature-monitor` |
| Any agent | point the agent at `SKILL.md` and follow its workflow |

### 2. Prepare the collector script

```bash
cp templates/collector-template.py ~/scripts/daily_papers_collect.py
```

Edit the **customization block** at the top of the script (`JOURNALS`, `BIORXIV_SUBJECTS`, `BIORXIV_KEYWORDS`), then test:

```bash
python3 ~/scripts/daily_papers_collect.py --days 1 --out-dir ~/litmon_test
# → ~/litmon_test/raw_<date>.json
```

### 3. Schedule a daily run (cron / scheduler)

Create a daily scheduled task in your agent platform, roughly:

```
Load the daily-literature-monitor skill and follow SKILL.md:
1. Run the collector: python3 ~/scripts/daily_papers_collect.py
2. Read raw.json, score with the keyword banks in references/keyword-banks.md
3. Curate 15-25 papers, group by topic section, write a digest in your preferred language
4. Save selected.json + digest.md into the output dir, then deliver to chat/email
```

> Schedule it late at night / early morning of the target day to cover PubMed + bioRxiv daily updates. / 定时建议设在目标日期的前一日深夜或当日凌晨。

### 4. Standalone CLI (no agent)

The collector works without any agent — you just lose the LLM filtering step:

```bash
python3 ~/scripts/daily_papers_collect.py --days 2 --out-dir ~/literature/daily
# or set the env var
export LITMON_OUTPUT_DIR=~/literature/daily
```

## Customization Guide — 个性化配置（部署后必做）

The default configuration consists of **generic examples, not a personal research profile**. Replace them with your own topics / 默认配置为通用示例，请按下表替换为你的研究方向：

| # | What to change | Where |
|---|---|---|
| 1 | Monitored journals 期刊列表 | `JOURNALS` dict in the collector script |
| 2 | bioRxiv categories 分类 | `BIORXIV_SUBJECTS` in the collector script |
| 3 | bioRxiv keyword pre-filter 预过滤关键词 | `BIORXIV_KEYWORDS` in the collector script |
| 4 | Digest sections + keywords 分类章节与关键词库 | `references/keyword-banks.md` (category names, emoji, keyword lists) |
| 5 | Section order validation 章节顺序校验 | `SECTION_ORDER` / `EMOJI_MAP` in `scripts/normalize-digest.py` |
| 6 | Summary language 摘要语言 | your preference (default example sections use Chinese names; change freely) |
| 7 | Output directory 输出目录 | `--out-dir` flag or `LITMON_OUTPUT_DIR` env var |

> ⚠️ **Keep these three in sync / 三处必须同步**: `references/keyword-banks.md` ↔ "Digest Format" in `SKILL.md` ↔ `SECTION_ORDER`/`EMOJI_MAP` in `scripts/normalize-digest.py`.

## What Each Run Produces — 每次运行输出

Each run writes three files into `<output-dir>/<date>/`:

| File | Contents |
|---|---|
| `raw.json` | Collector output: all candidate papers of the day (title, abstract, journal, DOI, link, tier) |
| `selected.json` | LLM-curated result: raw entries + `category` + `index` |
| `digest.md` | The final formatted digest for delivery |

## Known Pitfalls — 已知陷阱（运行前必读）

1. **Cross-day deduplication 跨日去重** — collection windows overlap across days; always check the previous day's `digest.md` before finalizing, or the same paper may be delivered twice.
2. **Short-substring keyword catastrophe 短词子串灾难** — e.g. `"rod"` matches ~50% of English abstracts; always use multi-word phrases (`"transcription factor binding"`, `"chromatin accessibility"`, `"cell atlas"`), never bare 2–4 letter acronyms without `\b` word boundaries.
3. **Non-breaking spaces in PubMed titles** — `\xa0` breaks substring matching; normalize whitespace before title matching.
4. **Validate with Python, not shell grep 校验用 Python** — digests contain emoji with variation selectors that can hang platform security scanners.
5. **bioRxiv DOI version suffix** — strip the trailing `v1` when verifying via the bioRxiv API.

## Documentation — 文档索引

| File | Purpose |
|---|---|
| `references/keyword-banks.md` | Example keyword lists per digest section (customize!) |
| `references/false-positive-filters.md` | Proven exclusion patterns for physics/engineering/clinical noise (customize!) |
| `references/multi-pass-filtering-workflow.md` | 3-pass filtering pattern for high-volume noisy days |
| `references/cron-digest-operational-lessons.md` | Real-run lessons: dedup, regex traps, validation scripts |
| `references/obsidian-note-generation.md` | Optional Obsidian note/index generation pattern |
| `references/verify-papers-before-sharing.md` | Official-API verification before recommending papers |
| `templates/collector-template.py` | Reusable PubMed + bioRxiv collector (customize `JOURNALS`/`SUBJECTS`/`KEYWORDS`) |
| `scripts/normalize-digest.py` | Pre-delivery format normalizer (edit `SECTION_ORDER`/`EMOJI_MAP`) |

## Related Topics — 相关检索词

*Literature monitoring · PubMed automation · bioRxiv preprints · daily paper digest · LLM relevance filtering · agent skills · research automation · scholarly search · scientific literature · knowledge management · Obsidian integration · cron pipeline* / *文献监控 · 每日文献速递 · 文献筛选 · 科研自动化*

## License — 许可

MIT License — free to use, modify, and distribute. / 自由使用、修改、分发。

## Changelog

- **v1.0.0** — Initial public release. Generic (de-personalized) default configuration; fixed section-header regex in `normalize-digest.py` (accepts both `**━━ … (N)**━━` and legacy `**━━ … (N) ━━**` styles); added `Sci Adv → Science Advances` normalization; bilingual README.