# Translator Skill for Claude Code

通用英中翻译技能，支持从短文到书籍的全场景翻译。

## 特性

- **开箱即用**：无需配置，Claude 直接翻译短文
- **LinguaGacha 增强**：长文/书籍翻译，20并发，断点续翻
- **智能术语表**：根据文本内容自动选择最匹配的领域术语表
- **全格式支持**：`.docx` / `.epub` / `.pdf` / `.txt` 输入，`.md` / `.docx` 输出
- **质量保障**：六维度评分体系，TEP 标准流程

## 安装

将本目录复制到你的项目的 `.claude/skills/translator/` 下：

```bash
# 方式一：克隆整个仓库
git clone https://github.com/147228/south-asia-research-skills.git
cp -r south-asia-research-skills/.claude/skills/translator .claude/skills/translator

# 方式二：直接在项目中使用
# 确保 .claude/skills/translator/ 目录存在即可
```

安装完成后，在 Claude Code 对话中即可使用翻译功能。

## 使用

**翻译短文**（开箱即用，无需配置）：
```
翻译这段话：
[粘贴英文原文]
```

**翻译书籍/长文**（需一次性配置 LinguaGacha）：
```
"C:\path\to\book.docx" 翻译这本书
```

详细使用说明见 [skill.md](skill.md)。

## 目录结构

```
translator/
├── skill.md              # 技能定义（入口，完整使用文档）
├── README.md             # 本文件
├── scripts/              # 自动化脚本
│   ├── extract_text.py   # 文本提取（docx/epub/pdf/txt）
│   ├── run_linguagacha.py # LinguaGacha 控制（含智能术语表选择）
│   ├── format_book.py    # Markdown 格式化
│   ├── md_to_docx.py     # MD → Word
│   └── save_glossary.py  # 术语表生成/合并
├── templates/            # 模板
│   ├── linguagacha_config.json  # LinguaGacha 配置模板
│   └── academic_prompt.txt      # 学术翻译提示词
├── glossaries/           # 术语表（按领域）
│   ├── README.md         # 术语表说明
│   ├── south_asia_military.json    # 南亚军政 108条
│   └── microsoft_it_terminology.json # IT术语 47,883条
└── references/           # 翻译参考
    ├── terminology.md          # 南亚译法示例
    ├── terminology_sources.md  # 12个权威术语来源
    ├── common-expressions.md   # 简化表达对照
    └── scoring-standards.md    # 六维度评分标准
```

## License

MIT
