# 翻译 Skill for Claude Code

一条可复用的英中翻译流水线，封装为 Claude Code Skill。支持书籍、杂志、报告等长文档的全流程翻译：文本提取 → 术语表构建 → 批量翻译 → 格式化 → Word 输出。

## 快速开始

在 Claude Code 对话框中直接输入：

**翻译书籍**（LinguaGacha + API，适合 10 万词以上）：
```
"C:\path\to\book.docx" 翻译这本书，学术风格，20并发
```

**翻译短文**（Claude 直接翻译，零依赖）：
```
翻译这篇文章，学术风格：
[粘贴英文原文]
```

## 工作流

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

## 工具链

- **Claude Code**（Anthropic CLI）：子 agent 并行、Grep 检索、文件读写、脚本执行
- **[LinguaGacha](https://github.com/neavo/LinguaGacha)**：开源翻译引擎，术语表注入、断点续翻、高并发
- **翻译 API**：任意 OpenAI 兼容接口（Gemini Flash 等）

## 已验证项目

| 项目 | 原文规模 | 术语表 | 译本规模 | 翻译引擎 |
|------|----------|--------|----------|----------|
| 《命运的四颗星》印度军事回忆录 | 13.3 万词 / 542 页 | 185 条 | 24 万字 | Gemini Flash |
| 《至高之争》AI 竞赛纪实 | 9.7 万词 / 350 页 | 247 条 | 20 万字 | Gemini 2.5 Flash |
| 《新科学家》2026.2.21 期 | 1.6 万词 / 杂志 | — | 10 万字 | Gemini 3 Flash |

## 仓库结构

```
.claude/skills/south-asia-translator/   # Skill 核心（入库）
├── skill.md                            #   skill 定义
├── scripts/                            #   自动化脚本
│   ├── extract_text.py                 #     文本提取（docx/epub/pdf/txt）
│   ├── run_linguagacha.py              #     LinguaGacha 控制 + 智能术语表选择
│   ├── format_book.py                  #     书籍格式化
│   ├── md_to_docx.py                   #     MD → Word
│   └── save_glossary.py                #     术语表生成
├── templates/                          #   配置模板
├── glossaries/                         #   术语表（南亚军事 + IT 通用）
└── references/                         #   翻译参考文档
```

翻译产出（译本、术语表、中间文件）保存在本地 `archive/`，不入库。

## 首次配置 LinguaGacha（可选）

短文翻译无需配置。书籍翻译需要：

1. 下载 [LinguaGacha](https://github.com/neavo/LinguaGacha/releases)，解压到项目根目录的 `LinguaGacha/` 文件夹
2. 准备一个 OpenAI 兼容 API（如 OpenRouter、代理服务等）
3. 在 Claude Code 中告知 API 地址、密钥和模型 ID，Claude 会自动完成配置

## 几点体会

1. **术语表必须先行。** 10 万词以上的书如果不先统一译法，后期返工量巨大。让子 agent 并行调研权威来源，把术语灌入翻译引擎，全书人名地名一次到位。
2. **Skill 的价值在第二次使用时才显现。** 第一本书花了大量时间解决工程问题。固化为 Skill 后，第二本书一句指令启动，第三本（杂志）同样如此。
3. **翻译不是研究的前置步骤，而是研究本身。** 结构化译本落地后，用 Grep 几秒钟挖出的素材比通读原著高效得多。
4. **自动化解决了 80% 的工作，但决定质量的是剩下的 20%。** 翻译、格式化、初步分析都可以自动化。逻辑框架和文风判断只能人来定。
