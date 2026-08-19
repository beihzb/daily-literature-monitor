# 文献推荐与真实性验证

当用户要求"推荐文章"（如早会/文献分享）时，**推荐来源建议限定为每日文献速递输出**（`<OUTPUT_DIR>/<date>/digest.md`，如最近一个月内），不要从其他渠道自选。用户看重真实性——推荐后常要求"确保文章真实，检查一遍"，必须逐篇用官方 API 验证后再交付。

## 验证工作流（两套 API，全部直连可用）

### PubMed 文章（有 PMID）

```bash
curl -s "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id={PMID}&retmode=json"
```

校验：`result.{PMID}.title`、`fulljournalname`、`pubdate`、`articleids`（取 `idtype == "doi"`）。标题、期刊、日期三项与 digest 一致即通过。

### bioRxiv 预印本（有 DOI）

```bash
curl -s "https://api.biorxiv.org/details/biorxiv/{DOI}"
```

⚠️ **必须去掉版本号**：`10.64898/2026.03.22.713558v1` 会返回 `DOI not recognizable`，去掉 `v1` 后缀（`10.64898/2026.03.22.713558`）才能查到。校验 `collection[0].title`、`date`、`version`。

## 关键陷阱：digest 标题可能被意译

每日速递的 digest 标题是 LLM 改写/翻译过的，**可能与官方标题不同**。实测案例（示例）：

- digest 写：`Neural computations in peripheral visual field during active search`
- 官方 bioRxiv 标题：`Visual Attention in The Periphery during Visual Search`

内容主题一致，但**分享/引用时必须用官方标题**。验证时标题不完全一致 ≠ 文章不存在——对比主题关键词即可，确认存在后用官方标题交付。

## 注意

- 新 bioRxiv DOI 前缀 `10.64898/`（2026 起）与旧 `10.1101/` 并存，API 对两者都认（去掉版本号后）
- 验证批量 PMID 时用 Python 循环 + json 解析，一次跑完再汇总
- 验证结果用表格汇报（✅/⚠️），⚠️ 项必须说明差异原因（如标题意译），不能含糊带过
