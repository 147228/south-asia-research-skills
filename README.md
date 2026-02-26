# 用 Claude Code 翻译两本书

我用 Claude Code 搭建了一条书籍翻译流水线，先后翻译了两本截然不同的英文书：一本 542 页的印度军事回忆录，一本关于 AI 竞赛的非虚构纪实。第一本书翻译过程中，流水线被固化为可复用的 Claude Code Skill；第二本书验证了这条流水线的通用性——换一本完全不同领域的书，一句指令即可启动全流程。

| | 书一 | 书二 |
|---|---|---|
| **书名** | 《命运的四颗星》(*Four Stars of Destiny*) | 《至高之争》(*Supremacy*) |
| **作者** | 纳拉瓦内（M.M. Naravane），印度陆军参谋长 | 帕尔米·奥尔森（Parmy Olson），彭博社专栏作家 |
| **原书格式** | Word (.docx)，542 页 | ePub，约 350 页 |
| **原书词数** | 13.3 万词 / 3,752 条 | 9.7 万词 / 8,542 条 |
| **译本规模** | 24 万中文字符 | 20 万中文字符（15.7 万汉字） |
| **术语表** | 185 条（军事、人名、地名） | 247 条（AI、公司、人名） |
| **翻译引擎** | LinguaGacha + Gemini Flash | LinguaGacha + Gemini 2.5 Flash |
| **附加产出** | 研究报告 + 6 张 SVG 图表 | — |

### 工具

- **Claude Code**（Anthropic 命令行工具）：子 agent 并行、Grep 检索、文件读写、脚本执行
- **[LinguaGacha](https://github.com/neavo/LinguaGacha)**：开源翻译引擎，术语表注入、断点续翻、高并发
- **翻译 API**：OpenAI 兼容接口（Gemini Flash 等模型）

```
原始文件 ──→ extract_text.py ──→ 纯文本
  (.docx/.epub/.pdf)                 │
                          ┌──────────┴──────────┐
                          │                     │
                    Claude 子 agent          LinguaGacha
                     （术语调研）             （批量翻译）
                          │                     │
                    glossary.json ──→ 术语注入 ──┘
                                                │
                                         翻译原始输出
                                                │
                                    format_book.py（章节重建）
                                                │
                                    md_to_docx.py（Word 输出）
                                                │
                                  ┌─────────────┴─────────────┐
                                  │                           │
                            中文译本 .md                 中文译本 .docx
```

---

## 第一本：《命运的四颗星》

印度陆军参谋长纳拉瓦内的回忆录，542 页，13.3 万词。内容涉及印巴边境、中印对峙、军政决策等敏感领域，术语翻译要求高。

### 翻译

```
[文件路径] Naravane Watermark Removed.docx
翻译这本书：先过一遍术语表，用 LinguaGacha 翻译，接第三方 API，用子 agent 先调研确认术语表再开始
```

Claude Code 自动完成：提取文本 → 子 agent 并行调研人名/地名/军事术语权威译法（新华社、军科院来源）→ 生成 185 条术语表 → 配置 LinguaGacha → 拆分 3,752 条翻译条目 → 运行翻译。

中途 50 并发触发 API 限流（429）。一句 `换成 gemini-2.5-flash，断点继续`，靠 LinguaGacha 的断点续翻从第 800 条无缝接上。翻译完成后自动导出、重建章节结构、生成 Word 文档。

**产出：24 万字中文译本。**

### 研究报告

翻译完成后，我向 Claude Code 提了 6 个研究问题（信息上报流程、响应速度、权力分配、危机应对、高层vs基层、选人用人）。Claude Code 启动 6 个子 agent 并行，每个 agent 在 24 万字译本中做 Grep 检索 + 联网搜索公开资料。

Grep 检索挖出了一些用通读几乎不可能发现的关键素材。比如搜索"兵棋推演"，定位到纳拉瓦内担任模拟解放军指挥官的一段叙述：他制定了详尽进攻方案，导演部发现黄方（解放军）占据优势后，虚构了一场"雨只下在黄方一侧"的特大风暴强行拖延 48 小时。最终蓝方"像往常一样获胜了"。这段埋在第三百多页的回忆成为报告中"认知偏差"一节的核心论据。

搜索"热钦山口"还原了 2020 年 8 月 31 日夜间的完整时间线：解放军坦克推进 → 前线要求开火 → 陆军参谋长被告知"未经最高层批准不得开火" → 反复致电 → 55 分钟后总理指示"做你认为合适的事"。一个设计了十二级上报链条来确保文官控制的体制，在最需要政治决断的时刻把责任推给了军方。

报告经四轮迭代打磨（调结构 → 压缩40% → 逐段去引用堆砌 → 全文逻辑审查），最终 172 行，配 6 张手写 SVG 图表。

### 固化为 Skill

```
请把这些工作用到的文件整理一下放在一起，工作流程固化为 skill
```

Claude Code 创建了 `.claude/skills/south-asia-translator/`，包含完整的 skill 定义、脚本、术语表模板、翻译提示词和质量检查清单。

---

## 第二本：《至高之争》

Parmy Olson 的 *Supremacy: AI, ChatGPT, and the Race That Will Change the World*（2024），讲 OpenAI 与 DeepMind 的 AI 竞赛。ePub 格式，约 9.7 万词。这是对第一本建立的翻译流水线的复用验证——领域完全不同（AI产业 vs 军事），格式也不同（ePub vs Word）。

### 启动翻译

```
"C:\...\Supremacy_AI,_ChatGPT,...epub" 翻译这本书，学术风格，20并发
```

一句指令，Claude Code 自动走完全流程：

1. **ePub 支持**：原有 `extract_text.py` 只支持 docx/pdf/txt，Claude Code 自动安装 `ebooklib` + `beautifulsoup4`，新增 epub 提取函数，产出 8,542 行纯文本
2. **术语表构建**：子 agent 为 AI 领域重新调研，生成 247 条术语表（Sam Altman → 萨姆·奥尔特曼、Demis Hassabis → 戴密斯·哈萨比斯、transformer → Transformer 架构 等）
3. **翻译提示词**：自动替换军事风格提示词为 AI/科技书面语风格
4. **LinguaGacha 翻译**：8,542 条中 900 条翻译完成，7,295 条空行自动跳过，347 条规则跳过
5. **格式化**：ePub 拆分造成的碎片行合并、章节标题重建（4 幕 16 章）、元数据清理

### ePub 格式的特殊挑战

ePub 本质是一组 XHTML 文件打包，斜体/粗体等格式标记会把文本切成碎片行。比如一句完整的话 "Sam Altman walked into *the office* that morning" 提取后可能变成三行。另外章节标题在正文中是拆分形式（"第X章"一行，副标题下一行），而目录中是完整形式（"第X章：副标题"）。

格式化脚本经历了四次迭代：v1-v2 被 ePub 元数据噪音和碎片合并问题困扰；v3 过度合并吞掉了章节标题；v4 最终实现了正确的 TOC 标题查找 + 中文/阿拉伯数字章节匹配 + 碎片行合并 + 垃圾过滤，产出 23 个标题层级（4 幕 + 16 章 + 序言/致谢/资料来源）的完整结构。

**产出：20 万字中文译本（`.md` + `.docx`），15.7 万汉字。**

---

## 复用

所有脚本和配置封装在 `.claude/skills/south-asia-translator/`。在 Claude Code 对话框中：

**翻译书籍**（需要 LinguaGacha + API）：
```
"C:\path\to\book.docx" 翻译这本书，学术风格，20并发
```
支持 .docx / .epub / .pdf / .txt。并发数建议：代理 API 用 20，官方 API 可用 50+。

**翻译短文**（Claude 直接翻译，零依赖）：
```
翻译这篇文章，学术风格：
[粘贴英文原文]
```

---

## 几点体会

1. **术语表必须先行。** 10 万词以上的书如果不先统一译法，后期返工量巨大。让子 agent 并行调研权威来源，把术语灌入翻译引擎，全书人名地名一次到位。两本书的术语表构建都由 Claude Code 自动完成——军事领域查新华社/军科院，AI 领域查科技媒体通行译法——无需人工编写。

2. **Skill 的价值在第二次使用时才显现。** 第一本书花了大量时间解决 docx 提取、格式化脚本调试、LinguaGacha 配置等工程问题。固化为 Skill 后，第二本书一句指令启动，Claude Code 自动识别 ePub 格式并扩展提取脚本、自动替换术语表和提示词、自动处理格式化。工程问题不再需要人介入。

3. **翻译不是研究的前置步骤，而是研究本身。** 24 万字的结构化译本一旦落地，用 Grep 几秒钟挖出的素材比通读 542 页原著高效得多。翻译完成的那一刻，研究已经完成了大半。

4. **自动化解决了 80% 的工作，但决定质量的是剩下的 20%。** 翻译、格式化、初步分析都可以自动化。报告的逻辑框架、文风判断、"哪些洞察保留哪些该砍"只能人来定。

---

## 目录结构

```
南亚研究skills/
├── README.md                            # 本文件
├── CLAUDE.md                            # Claude Code 项目指令
├── .gitignore
│
├── .claude/skills/
│   └── south-asia-translator/           # 翻译 Skill（核心）
│       ├── skill.md                     #   skill 定义
│       ├── scripts/                     #   自动化脚本
│       │   ├── extract_text.py          #     文本提取（docx/epub/pdf/txt）
│       │   ├── run_linguagacha.py       #     LinguaGacha 控制
│       │   ├── format_book.py           #     书籍格式化
│       │   ├── md_to_docx.py            #     MD → Word
│       │   └── save_glossary.py         #     术语表生成
│       ├── templates/                   #   模板
│       ├── glossaries/                  #   术语表
│       └── references/                  #   参考文档
│
├── 《命运的四颗星》纳拉瓦内回忆录_中文译本.md   # 书一译本
├── 《至高之争》AI竞赛与世界变局_中文译本.md     # 书二译本
├── 印度军政决策机制研究报告.md                  # 书一衍生研究报告
├── diagrams/                                   # 研究报告配图（6 张 SVG）
├── format_supremacy.py                         # 书二格式化脚本
├── glossary_naravane.json                      # 书一术语表
└── glossary_supremacy.json                     # 书二术语表
```
