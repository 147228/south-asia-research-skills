---
name: translator
description: 英中翻译助手。推荐使用 LinguaGacha 翻译引擎处理长文/书籍，短文可直接用 Claude 翻译。功能包括：LinguaGacha 流水线、智能术语表、Word 格式输出、六维度质量评分。适用于任何领域的英中翻译。当用户需要翻译英文内容时使用此技能。
---

# 英中翻译助手

通用翻译工作流助手，适用于任何领域（国际关系、军事、科技、经济、人文社科等）。

---

## 翻译模式

### 推荐：LinguaGacha（长文/书籍）

高并发批量翻译引擎，术语表自动注入，断点续翻，成本低。

```
"C:\路径\original.docx" 翻译这个
```

流水线自动执行：提取文本 → 智能选择术语表 → LinguaGacha 翻译 → 格式化 → Word 输出。

### Claude 直译（短文/即时）

无需配置，直接使用：

```
翻译这段话：
[粘贴英文原文]
```

### Fallback：Claude 分批翻译

若无法运行 LinguaGacha（无执行环境、无 API、用户拒绝配置），Claude 按段落/标题分批翻译长文：
- 保持原文结构（章节、段落顺序不变）
- 生成英中对照表
- 在输出开头标注 `[FALLBACK] 本译文由 Claude 分批翻译，未经 LinguaGacha 流水线处理`
- 专有名词首次出现标注英文，全文保持一致

---

## 首次配置（仅需一次）

**下载 LinguaGacha**：https://github.com/neavo/LinguaGacha/releases（v0.55.0+），解压到项目根目录 `LinguaGacha/LinguaGacha/app.exe`

**配置 API**：
```bash
cd ".claude/skills/translator/scripts"
python run_linguagacha.py setup
# 填入 API URL 和 Key，其余回车用默认值
```

| 参数 | 默认值 | 说明 |
|------|--------|------|
| API URL | `https://xxxx.xxx/v1` | OpenAI 兼容端点 |
| model_id | `gemini-3-flash-preview` | 推荐模型 |
| 并发数 | 20 | 太高会触发限流 |

---

## 术语表

翻译时自动扫描输入文本前100行，匹配最相关的术语表：

- 南亚/军事 → `south_asia_military.json`（108条）
- IT/软件 → `microsoft_it_terminology.json`（47,883条）
- 无匹配 → 不加载（避免污染）

手动指定：`--glossary glossaries/xxx.json`

添加新术语表：JSON 放入 `glossaries/`，在 `run_linguagacha.py` 的 `DOMAIN_KEYWORDS` 中加关键词。

术语表格式：`[{"src": "English", "dst": "中文", "info": "备注"}]`

---

## 输出格式

### Word 文档（最终产物）

命名：`《书名》中文标题_中文译本.docx`
示例：`《至高之争》AI竞赛与世界变局_中文译本.docx`

排版：

| 项目 | 规格 |
|------|------|
| 纸张 | A4，页边距 2.54cm |
| 正文 | 宋体 12pt / Times New Roman 12pt |
| 行距 | 1.5倍，无首行缩进 |
| 一级标题 | 黑体 16pt 加粗居中 |
| 二级标题 | 黑体 14pt 加粗 |

### 文章结构

1. 英语标题
2. 来源说明 + 原标题 + 作者
3. 编者按（如需要，500字以内，【编者按】开头）
4. 正文：一段英文 + 一段译文，交替排列
5. 作者介绍

---

## 翻译原则

- **忠实原文**：准确传达原意，不增不减不改
- **中文表达**：符合中文习惯，可调整句法结构，避免翻译腔
- **简练书面**：去冗余，前提动词，拆长句（详见 [common-expressions.md](references/common-expressions.md)）
- **专有名词**：人名/机构名首次标注英文全名，后续用中文简称，全文统一
- **政治合规**：涉华内容符合我国立场，涉台涉藏涉疆审慎处理

---

## 质量评分（六维度，总分10分）

| 维度 | 分值 | 要点 |
|------|------|------|
| 中文表达自然度 | 1.5 | 避免英文句式 |
| 语言客观流畅度 | 2.0 | 精准客观，节奏流畅 |
| 动词位置优化度 | 1.5 | 动词紧随主语 |
| 句式简化度 | 1.5 | 拆分长句 |
| 认知负荷控制 | 2.0 | 信息层次分明 |
| 意思准确度 | 2.5 | 完整传达，无遗漏 |

迭代优化目标：9.5/10 分后生成 Word。详细标准见 [scoring-standards.md](references/scoring-standards.md)。

---

## 常用命令

```bash
cd ".claude/skills/translator/scripts"

# LinguaGacha
python run_linguagacha.py setup                    # 首次配置
python run_linguagacha.py create "input.txt"       # 创建项目并翻译
python run_linguagacha.py status                   # 查看进度
python run_linguagacha.py start                    # 断点续翻
python run_linguagacha.py retry                    # 重试失败项

# 工具
python extract_text.py "book.docx"                 # 提取文本
python format_book.py input.txt output.md          # 格式化
python md_to_docx.py output.md output.docx         # 转 Word
python save_glossary.py                            # 术语表工具
```

---

## 参考文档

- [common-expressions.md](references/common-expressions.md) — 简化表达对照表
- [scoring-standards.md](references/scoring-standards.md) — 六维度评分详细标准
- [terminology.md](references/terminology.md) — 南亚领域译法示例
- [terminology_sources.md](references/terminology_sources.md) — 12个权威术语来源
- [LinguaGacha 官方文档](https://github.com/neavo/LinguaGacha)
