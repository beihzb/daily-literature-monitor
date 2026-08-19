# Digest 运行实操经验（多次运行沉淀的通用教训）

## 1. 跨日窗口重叠 → 必须对上一日 digest 去重（每次必做）
采集脚本按设计拉取重叠窗口（如某日 raw.json 同时含 bioRxiv 前两天的批次），而较早批次的论文大多已被上一日 digest 收录。每次运行都可能有一批候选已在上一日 digest 中出现 → 必须剔除，否则同一篇连发两天。

流程：
1. 定稿前先读上一日 `<OUTPUT_DIR>/<prev-date>/digest.md`，提取已覆盖标题/DOI 集合。
2. 候选论文逐一比对，重复者剔除（bioRxiv DOI 前缀相同，按标题或 DOI 匹配均可）。
3. 精选数可能因此低于下限 → 回到被跳过清单补选低相关度但尚可接受的论文。

## 2. normalize-digest.py 章节正则的历史误报（v1.0.0 已修复）
早期 `scripts/normalize-digest.py` 对标题格式 `**━━ 名称 (N) ━━**`（以 `━━**` 收尾）可能报 "Could not find any section headers"——正则只认 `**━━` 收尾。**v1.0.0 起已同时兼容两种收尾格式**。若仍遇到类似误报：不要改写 digest 格式，自行用 Python 校验完整性（条目数、章节、链接、预印本标记）。

## 3. 校验命令避免 shell grep 匹配 emoji
digest 内容恒含 ⚠️/👁️ 等带变体选择符（variation selector）的 emoji。部分 agent 平台的安全扫描会对含变体选择符的 shell 命令做特殊处理（可能挂起或拦截）。**校验一律用 Python 脚本**（heredoc 或代码块），不要用 shell grep 匹配含 emoji 的 pattern。

## 4. 可直接复用的校验脚本
```python
import json, re
base = '<OUTPUT_DIR>/<DATE_DIR>/'
md = open(base + 'digest.md').read()
entries = md.count('\n🆕 ')
sections = re.findall(r'^## \*\*━━ (.+?) \((\d+)\) ━━\*\*$', md, re.M)
links = md.count('🔗 [')
preprints = md.count('⚠️预印本')
print(entries, sections, links, preprints)
with open(base + 'selected.json') as f:
    d = json.load(f)
print(d['date'], d.get('total_scanned'), d.get('selected_count'))
from collections import Counter
print(dict(Counter(p['category'] for p in d['selected'])))
print('一致:', entries == d['selected_count'])
```

## 5. 日期与归档约定
- 若 cron 在深夜运行，DATE_DIR 可能是运行日的"次日"——digest 标题日期 = DATE_DIR，不要写成运行当天。明确你的时区和 cron 时间，保持一致。
- `selected.json` schema 建议：`{date, total_scanned, selected_count, selected:[...]}`，每条 selected 论文在原始 dict 上追加 `category` 与 `index`（raw.json 内下标）字段。
- 归档三件套：raw.json（脚本生成）+ selected.json + digest.md（均存于 DATE_DIR）。

## 6. digest 校验正则的四个坑
1. **章节名含空格 → `(\S+?)` 正则失配**：`re.findall(r'\*\*━━\s*(\S+?)\s*\(\d+\)\*\*━━', md)` 对 `**━━ 💻 生物信息学 (3)**━━` 返回空——`\S+?` 只能匹配一个非空格 token（"💻"），跨不过 "生物信息学" 前的空格。必须用 `re.findall(r'\*\*━━\s*(.*?)\s*\((\d+)\)\*\*━━', md)`。
2. **顺序比对前先剥 emoji 前缀**：`(.*?)` 取出的名字带 emoji（"💻 生物信息学"），与 expected 列表（"生物信息学"）直接 `==` 恒为 False。先 `re.sub(r'^[^\u4e00-\u9fff]+', '', name)` 再比。
3. **📝 描述"英文过多"启发式是假阳性源**：用英文词占比检查中文描述，会把含 scRNA-seq / CRISPR / ATAC-seq 等合法缩写的描述误报为英文。标准英文缩写是允许的；不要用英文词数占比校验中文描述，改为抽查每条是否以中文为主、缩写是否属于领域标准。
4. **digest↔selected.json 链接比对要两侧都 `rstrip('/')`**：pubmed link 带尾部斜杠，只剥一侧会产出假 mismatch。

## 7. 关键词打分 ≠ 全部命中：整池扫描仍必要
某次 240 篇池打分得 35 候选（阈值≥3），24 篇定稿中 3 篇**完全不在打分候选内**，全靠整池 title+abstract 片段扫描（已打分部分 + 剩余未打分部分全部过一遍 snippet）捞回。打分阈值偏严时约 10%+ 最终入选来自打分池之外——流程必须是"打分排序 → 整池扫 snippet（含未打分者）→ 人工定稿"，不能只信打分结果。
