---
name: translator
description: 英中翻译助手（LinguaGacha优先）。默认使用LinguaGacha翻译引擎处理所有翻译任务，仅在用户明确要求或文本极短（<500词）时才使用Claude直译。功能包括：LinguaGacha流水线管理、术语表管理、分段对照翻译、专有名词规范化、编者按撰写、六维度质量评分、Word格式输出。适用于任何领域的英中翻译：国际关系、军事、科技、经济、学术论文等。当用户需要翻译英文内容时使用此技能。
---

# 英中翻译助手

## 核心定位

**通用翻译工作流助手** —— 以 **LinguaGacha** 为核心翻译引擎，从原文到成稿的全流程辅助。适用于任何领域（国际关系、军事、科技、经济、人文社科等）。

---

## ⚠️ 翻译模式选择（必读）

**默认使用 LinguaGacha**。收到翻译请求时，按以下规则判断：

```
收到翻译请求
  │
  ├─ 文本 ≥ 500词 或 有文件路径 ──→ 【必须】使用 LinguaGacha 流水线
  │
  ├─ 文本 < 500词 且 用户直接粘贴 ──→ 可用 Claude 直译（快速模式）
  │
  └─ 用户明确说"用Claude翻译" ──→ Claude 直译
```

**禁止行为**：
- ❌ 不得在未询问用户的情况下跳过 LinguaGacha 而使用 Claude 分批翻译
- ❌ 不得用多个 Claude sub-agent 并行翻译来替代 LinguaGacha
- ❌ 不得因为"更方便"而选择 Claude 直译处理长文本

**必须行为**：
- ✅ 收到文件路径时，第一反应是走 LinguaGacha 流水线
- ✅ 如果 LinguaGacha 未安装，提示用户下载安装而不是转用 Claude
- ✅ 如果 API 未配置，引导用户配置而不是转用 Claude

---

## 快速上手

### 两种翻译模式

| | 开箱即用模式 | LinguaGacha 增强模式（推荐） |
|---|---|---|
| **适用场景** | 短文（<500词）、即时翻译 | 长篇、书籍、批量翻译 |
| **配置要求** | 无需任何配置 | 一次性配置（3步） |
| **翻译引擎** | Claude 直译 | LinguaGacha + LLM API |
| **术语表** | 手动维护 | 自动注入，全文统一 |
| **速度参考** | 即时 | 1万词/1-2分钟（20并发） |
| **断点续翻** | 不支持 | 支持 |

### 开箱即用（Claude 直译）

无需配置，直接使用：
```
翻译这段话：
[粘贴英文原文]
```

Claude 自动完成翻译 + 术语规范化 + 六维度评分。适合段落级翻译和即时查看结果。

### LinguaGacha 增强模式（推荐，适合长文）

```
"C:\路径\original.docx" 翻译这个
```

Claude 自动执行完整流水线：
1. 提取文本 → `extract_text.py`
2. 智能选择术语表 → 根据文本内容自动匹配最相关的术语表
3. 配置 LinguaGacha → 检查 `linguagacha_config.json`
4. 启动翻译 → `run_linguagacha.py create`
5. 监控进度 → `run_linguagacha.py status`
6. 导出译文 → 自动输出到 `_译文/` 和 `_译文_双语对照/` 目录
7. （可选）格式化 Word → `format_book.py` + `md_to_docx.py`
8. （可选）审校优化 → 六维度评分，目标 9.5/10

### 首次配置 LinguaGacha（仅需一次，只需填 URL 和 Key）

**第1步：下载 LinguaGacha**

从 https://github.com/neavo/LinguaGacha/releases 下载最新版（v0.55.0+），解压到项目根目录：
```
项目根目录/
└── LinguaGacha/
    └── LinguaGacha/
        └── app.exe
```

**第2步：运行配置**

```bash
cd ".claude/skills/translator/scripts"
python run_linguagacha.py setup
```

只需填两项：
- **API URL**：你的中转 API 地址（如 `https://yunwu.ai/v1`）
- **API Key**：你的 API Key

其他参数（模型、并发数）有默认值，直接回车即可。配置完成后所有翻译任务自动使用 LinguaGacha。

---

## 术语表智能选择

翻译时，系统会扫描输入文本前100行，自动检测内容领域并选择最匹配的术语表：

- **南亚/军事内容** → `south_asia_military.json`（108条）
- **IT/软件内容** → `microsoft_it_terminology.json`（47,883条）
- **无匹配领域** → 不加载术语表（避免不相关术语污染翻译）

也可手动指定：
```bash
python run_linguagacha.py create input.txt --glossary glossaries/my_glossary.json
```

添加新领域术语表：将 JSON 文件放入 `glossaries/` 目录，并在 `run_linguagacha.py` 的 `DOMAIN_KEYWORDS` 中添加对应关键词即可。

---

## LinguaGacha 翻译流水线（核心功能）

### 概述

LinguaGacha 是一个基于 LLM 的批量翻译引擎，通过 OpenAI 兼容 API 调用大模型进行翻译。优势：
- **高并发**：20 线程并发翻译，1.6万词约2分钟完成
- **断点续翻**：中断后可从断点继续，不重复翻译
- **术语表支持**：JSON 格式术语表，确保专有名词统一
- **双语对照输出**：自动生成纯译文 + 双语对照两个版本
- **成本低**：使用 Gemini Flash 等模型，成本远低于 Claude 直译

### 安装要求

- **LinguaGacha v0.55.0+**：https://github.com/neavo/LinguaGacha/releases
  - 解压到项目根目录的 `LinguaGacha/LinguaGacha/` 下
  - 确保 `app.exe` 可访问
- **OpenAI 兼容 API**：如 yunwu.ai、OpenRouter、本地部署等
- **Python 3.9+**，python-docx 库（仅 Word 输出需要）

### 六步工作流

#### 第1步：提取文本
```bash
cd ".claude\skills\translator\scripts"
python extract_text.py "C:\path\to\book.docx"
# 输出: book.clean.txt（自动清理InDesign标记、页码等）
```
支持格式：`.docx` / `.pdf` / `.txt` / `.epub`

#### 第2步：构建术语表（可选但推荐）

使用 Claude 子 agent 搜索权威译法：
```
帮我为这本关于[主题]的书构建术语表，搜索权威来源的标准译法
```

术语表格式（LinguaGacha 兼容 JSON）：
```json
[
  {"src": "English Term", "dst": "中文译名", "info": "备注说明"}
]
```

预置术语表位于 `glossaries/` 目录，可按领域添加新文件。

#### 第3步：配置 LinguaGacha

**首次使用**需要配置 API：
```bash
python run_linguagacha.py setup
# 交互式输入: API URL, API Key, 模型ID, 并发数
```

**如果已有配置**（`linguagacha_config.json` 存在于项目根目录），可跳过此步。

关键参数：
| 参数 | 推荐值 | 说明 |
|------|--------|------|
| API URL | https://yunwu.ai/v1 | OpenAI 兼容端点 |
| model_id | gemini-2.5-flash | 推荐模型（速度快、质量好） |
| concurrency_limit | 20 | 并发数，太高会触发限流 |
| output_token_limit | 16384 | 输出 token 上限 |
| temperature | 0.3 | 低温度保证翻译一致性 |

#### 第4步：运行翻译
```bash
# 创建项目并开始翻译
python run_linguagacha.py create "C:\path\to\book.clean.txt"

# 指定自定义术语表
python run_linguagacha.py create "C:\path\to\book.clean.txt" --glossary glossaries/my_glossary.json

# 指定自定义提示词
python run_linguagacha.py create "C:\path\to\book.clean.txt" --prompt my_prompt.txt
```

**翻译完成后**，LinguaGacha 自动输出两个目录：
- `项目名_译文/` → 纯中文译文
- `项目名_译文_双语对照/` → 英中双语对照

#### 第5步：监控与故障处理
```bash
# 查看进度
python run_linguagacha.py status

# 断点续翻（中断后继续）
python run_linguagacha.py start

# 重试失败项
python run_linguagacha.py retry
```

**常见问题**：
- `UnicodeEncodeError: 'gbk'`：这是 Windows 控制台显示问题，不影响翻译结果
- `LANGUAGE_SKIPPED`：表示该行无需翻译（纯数字、URL等），属于正常行为
- API 超时：降低 `concurrency_limit` 或检查网络

#### 第6步：格式化输出（可选）
```bash
python format_book.py input_translated.txt output.md    # Markdown 格式化
python md_to_docx.py output.md output.docx              # 转 Word 文档
```

Word 排版规格：
- A4 纸张，页边距 2.54cm
- 正文：宋体 12pt，1.5 倍行距
- 章节标题：黑体，16pt(部)/14pt(章)加粗

### 速度参考（Gemini Flash + 20并发）

| 文档规模 | 预计耗时 | 备注 |
|----------|----------|------|
| 1万词 | 1-2分钟 | 短篇报告/文章 |
| 5万词 | 5-10分钟 | 长篇论文 |
| 13万词 | 20-30分钟 | 书籍 |
| 30万词 | 1-2小时 | 大部头著作 |

### 翻译提示词定制

默认提示词位于 `templates/academic_prompt.txt`，可为不同类型文档创建专用提示词：

```bash
# 使用自定义提示词
python run_linguagacha.py create input.txt --prompt my_custom_prompt.txt
```

提示词要点（LinguaGacha 格式要求）：
1. 严格按照输入行数翻译，不得拆分或合并行
2. 保留原文中的控制字符（空白符、转义符等）
3. 完整翻译所有文本，包括专有名词
4. 说明文档类型和翻译风格要求

---

## Claude 直译模式（短文/快速模式）

### 适用场景
- 文本少于 500 词
- 用户直接粘贴原文
- 用户明确要求不使用 LinguaGacha
- 需要即时交互式翻译

### 工作流

Claude 自动完成：
1. 翻译初稿（英中对照）
2. 撰写编者按（如需要）
3. 术语规范化（人名、机构名首次标注英文）
4. 迭代评分优化（六维度评分，目标9.5/10分）
5. 生成 Word 文档

---

## 翻译原则

### 总体要求
- **信**：准确传达原意，不增不减
- **达**：符合中文表达习惯，可调整句法结构
- **雅**：语言简练书面，避免翻译腔

### 政治合规底线（涉及中国相关内容时）
- 涉及中国主权、领土完整的表述必须符合我国立场
- 涉台、涉藏、涉疆表述需特别审慎
- 如原文有反华立场，在编者按中提示读者

## 输出格式

### 最终产物

翻译完成后自动输出 **Word 文档（.docx）**，命名格式：
```
《书名/文章名》中文标题_中文译本.docx
```

示例：
- `《至高之争》AI竞赛与世界变局_中文译本.docx`
- `《命运的四颗星》纳拉瓦内回忆录_中文译本.docx`

### Word 排版规范

| 项目 | 要求 |
|------|------|
| 纸张 | A4，页边距 2.54cm |
| 字号 | 小四/12pt |
| 中文字体 | 宋体 |
| 英文字体 | Times New Roman |
| 行间距 | 1.5倍 |
| 缩进 | 无首字符缩进 |
| 一级标题 | 黑体 16pt 加粗，居中 |
| 二级标题 | 黑体 14pt 加粗，前空一行 |

### 文件命名（学术编译场景）
`【0】译者名字-提交日期-文章中文题目.docx`

### 文件管理结构
```
translations/
├── YYYYMMDD_文章标题/
│   ├── source/
│   │   └── original.txt          # 英文原文
│   ├── drafts/
│   │   ├── draft1.docx           # 初译稿
│   │   ├── draft2.docx           # 二稿
│   │   └── draft3.docx           # 三稿
│   └── final/
│       └── 【0】译者-日期-标题.docx  # 终稿
```

### 文章结构（按顺序）
1. **英语标题**
2. **来源说明**：本文编译自《xxx》xxxx年xx月xx日文章
3. **原标题**：原标题为xxx
4. **作者**：作者为xxx
5. **编译/审核**：编译：xxx / 审核：xxx
6. **编者按**：【编者按】开头，500字以内（如需要）
7. **正文**：一段英文 + 一段译文，交替排列（**必须完整，不得遗漏**）
8. **作者介绍**：作者曾任/现任职务

### 排版规范
| 项目 | 要求 |
|------|------|
| 字号 | 小四/12号 |
| 中文字体 | 宋体 |
| 英文字体 | Times New Roman |
| 行间距 | 1.5倍 |
| 缩进 | 无首字符缩进 |
| 一级标题 | 加粗，居中 |
| 二级标题 | 加粗，前空一行 |

## 专有名词处理

### 人名规则
- 格式：中文译名（英文原文）
- 首次出现标注英文全名，后续使用中文简称
- 同一人名全文保持一致

### 机构名规则
- 首次出现：全称（以下简称xxx）
- 后续出现：使用简称

### 货币换算
- 格式：X美元（约合人民币X元）
- 汇率按当前市场汇率估算

### 印度数字单位（南亚领域适用）
| 英文 | 数值 | 换算 |
|------|------|------|
| Lakh | 十万 | 1 Lakh = 100,000 |
| Crore | 千万 | 1 Crore = 10,000,000 |
| Lakh Crore | 万亿 | 1 Lakh Crore = 1,000,000,000,000 |

## 翻译禁忌

### 禁止保留
- 无注释"今年""本周""上个月"等模糊时间 → 查明具体日期
- 无注释的外文词（GDP等高知晓度词除外）
- 未经核实的数据、史实

### 禁止使用
- 无必要的"的""了""其""一个"
- 动名词做主语（如"提高产品附加值"优于"使产品附加值得到提升"）
- 缺少主语的句子（使用"通过""由于""经过""为了"时注意）

### 禁止风格
- 翻译腔/硬译
- 过长的定语从句直译
- 被动语态滥用

## 简化表达对照

| 口语化/冗长 | 书面化/简练 |
|-------------|-------------|
| 从中国进口 | 自华进口 |
| 从美国进口 | 自美进口 |
| 相比 | 较 |
| 可能会 | 或/恐 |
| 就……来看 | 以……为例 |
| 对……来说 | 就……而言 |
| 怪罪 | 归咎于 |
| 头几个月 | 初 |
| 这一 | 此 |
| 有望在/将在 | 拟/拟于 |
| 对……持谨慎态度 | 顾虑为 |
| 公司 | 企业 |

完整列表见：[common-expressions.md](references/common-expressions.md)

## 编者按撰写（如需要）

### 五要素
1. **核心内容**：精准提炼文章要点
2. **重要性**：为什么值得翻译
3. **推荐理由**：对读者的意义和启发
4. **注意提示**：如作者立场偏颇、数据存疑等
5. **借鉴意义**：对相关研究/政策的参考价值

### 格式要求
- 字数：500字以内
- 开头：【编者按】

## 质量检查清单

参考 ISO 17100 标准，建立多维度质量检查体系。

### 翻译前准备（Pre-Translation）
- [ ] 通读原文，理解整体结构、论点和作者立场
- [ ] 标记不确定的术语和表述
- [ ] 查找专有名词固定译法（参考 `glossaries/` 和 [terminology.md](references/terminology.md)）
- [ ] 确认文章发布日期，计算时间表述
- [ ] 识别文章类型（新闻/论文/报告/评论/书籍/杂志）
- [ ] 确认目标读者群体和翻译风格要求
- [ ] **选择翻译模式**：≥500词 → LinguaGacha；<500词 → Claude 直译

### 翻译中控制（In-Translation QA）
- [ ] **结构对照**：一段英文对应一段译文
- [ ] **术语标注**：人名机构名首次出现标注英文
- [ ] **疑问标记**：不确定处用【？】标出
- [ ] **语言风格**：前提动词，避免翻译腔
- [ ] **数字核对**：数字、百分比、日期逐一核对
- [ ] **引文检查**：引用内容与原文完全一致

### 翻译后审校（Post-Translation Review）

#### 1. 内容准确性（Accuracy）
- [ ] 逐段核对，确保无遗漏、无多译
- [ ] 译文忠实原文，无增删改
- [ ] 数字、日期、人名、地名准确无误
- [ ] 专业术语翻译准确

#### 2. 术语一致性（Terminology Consistency）
- [ ] 同一人名全文统一
- [ ] 同一机构名全文统一
- [ ] 专业术语前后一致
- [ ] 简称使用规范

#### 3. 语言流畅度（Fluency）
- [ ] 以读者视角通读全文，语句通顺
- [ ] 无翻译腔、硬译
- [ ] 句子结构符合中文表达习惯

#### 4. 格式规范性（Formatting）
- [ ] 字体：中文宋体、英文 Times New Roman
- [ ] 字号、行距、标题格式正确
- [ ] 英文原文与中文译文交替排列

#### 5. 政治合规性（如涉及中国相关内容）
- [ ] 涉华表述符合我国立场
- [ ] 边境争议地区表述准确

## TEP 标准流程

参考 ISO 17100 国际翻译标准，采用三步质量保障流程：

### T - Translation（翻译）
- 通读全文，理解文章结构和论点
- 查找专有名词固定译法
- **使用 LinguaGacha 进行翻译**（长文）或 Claude 直译（短文）
- 人名机构名首次出现标注英文原文
- 初步检查数字、日期、引文准确性

### E - Editing（编辑审校）
- 术语一致性检查
- 语言优化（去翻译腔，简化冗长表达，参考 common-expressions.md）
- 内容核查（数据、史实、引文）

### P - Proofreading（校对）
- 语言校对（typo、错别字、语病、标点）
- 格式校对（字体、字号、行距、标题）
- 完整性校对（编者按、作者介绍、文件命名）

## 六维度质量评分

### 评分维度（总分10分）
1. **中文表达自然度** (1.5分) - 避免英文句式，符合中文表达习惯
2. **语言客观流畅度** (2.0分) - 精准客观，无冗余，节奏流畅
3. **动词位置优化度** (1.5分) - 动词紧随主语，避免头重脚轻
4. **句式简化度** (1.5分) - 拆分复杂长句，避免从句嵌套
5. **认知负荷控制** (2.0分) - 信息层次分明，降低理解难度
6. **意思准确度** (2.5分) - 完整传达原意，无遗漏曲解

详细评分标准见：[scoring-standards.md](references/scoring-standards.md)

### 迭代优化
```
继续优化：使用评分系统进行迭代优化，目标达到9.5/10分时自动生成Word文档
```

---

## 术语表管理

### 目录结构
术语表统一存放在 `glossaries/` 目录下，按领域分文件：

```
glossaries/
├── south_asia_military.json     # 南亚军政通用术语（预置）
├── science_general.json         # 科学通用术语
├── international_relations.json # 国际关系术语
└── ...                          # 按需添加
```

### 格式规范（LinguaGacha 兼容）
```json
[
  {"src": "English Term", "dst": "中文译名", "info": "备注说明"}
]
```

### 使用方式
- LinguaGacha 翻译时，系统自动根据文本内容选择最匹配的术语表
- 也可通过 `--glossary` 参数手动指定
- 不指定且无匹配领域时，不加载术语表（避免污染翻译）
- 可通过 `save_glossary.py` 交互式创建/合并术语表

### 权威术语来源
构建术语表时应优先参考以下权威来源：
- **全国科学技术名词审定委员会**（术语在线 termonline.cn）
- **联合国术语数据库**（UNTERM）
- **微软语言门户**（Microsoft Language Portal）
- **中国社科院各研究所出版物**
- **外交部官方翻译**

---

## 目录结构

```
translator/
├── skill.md                          # 本文件（技能定义）
├── scripts/                          # 自动化脚本
│   ├── extract_text.py               # 文本提取（docx/pdf/txt/epub）
│   ├── run_linguagacha.py            # LinguaGacha 控制脚本（核心）
│   ├── format_book.py                # Markdown 格式化
│   ├── md_to_docx.py                 # Markdown 转 Word
│   └── save_glossary.py              # 术语表生成/导出工具
├── templates/                        # 模板文件
│   ├── academic_prompt.txt           # 学术翻译提示词（LinguaGacha 用）
│   └── linguagacha_config.json       # LinguaGacha 配置模板
├── glossaries/                       # 术语表（按领域组织，LinguaGacha JSON 格式）
│   ├── microsoft_it_terminology.json # 微软 IT 术语（47,883条，来源：Microsoft）
│   └── south_asia_military.json      # 南亚军政术语（108条，预置示例）
└── references/                       # 参考文档
    ├── terminology.md                # 南亚人名/机构/地名译法（示例）
    ├── terminology_sources.md        # 权威术语库来源指南（12个来源）
    ├── common-expressions.md         # 简化表达对照（通用）
    └── scoring-standards.md          # 六维度评分标准（通用）
```

---

## 参考文档

- **权威术语来源**：[terminology_sources.md](references/terminology_sources.md) - 12个权威术语数据库的详细使用指南
- **惯用表达**：[common-expressions.md](references/common-expressions.md) - 简化表达对照表
- **评分标准**：[scoring-standards.md](references/scoring-standards.md) - 六维度翻译质量评分体系
- **专有名词库（示例）**：[terminology.md](references/terminology.md) - 南亚领域译法参考
- **LinguaGacha 官方文档**：https://github.com/neavo/LinguaGacha
