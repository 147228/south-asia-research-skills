# Translator Skill for Claude Code

通用英中翻译技能（Claude Code Skill），从短文到书籍的全场景翻译。

## 一键安装

```bash
git clone https://github.com/147228/south-asia-research-skills.git
# 将 .claude/skills/translator/ 复制到你的项目中
```

## 两种使用模式

### 模式一：开箱即用（Claude 翻译）

无需任何配置，在 Claude Code 中直接使用：

```
翻译这段话：
The rapid development of artificial intelligence...
```

适合：段落级翻译、即时查看。长文也可用 Claude 分批翻译（保持原结构、生成对照表）。

### 模式二：LinguaGacha 增强（推荐，适合长文/书籍）

一次性配置后即可翻译任意长度文档：

**配置（仅需一次，只填 URL 和 Key）：**
1. 下载 [LinguaGacha](https://github.com/neavo/LinguaGacha/releases)（v0.55.0+），解压到项目根目录的 `LinguaGacha/LinguaGacha/` 下
2. 运行配置：
   ```bash
   cd .claude/skills/translator/scripts
   python run_linguagacha.py setup
   # 只需填 API URL 和 Key，其他直接回车用默认值
   ```

**翻译：**
```
"C:\path\to\book.docx" 翻译这本书
```

Claude 自动完成：提取文本 → 智能选择术语表 → LinguaGacha 翻译 → 格式化 → 输出 Word 文档。

**输出示例：**
```
《至高之争》AI竞赛与世界变局_中文译本.docx
```
Word 排版：宋体12pt + Times New Roman、1.5倍行距、章节标题加粗居中。

## 术语表

预置两个领域术语表，翻译时根据文本内容自动匹配：

| 文件 | 领域 | 条目数 |
|------|------|--------|
| `south_asia_military.json` | 南亚军政 | 108 |
| `microsoft_it_terminology.json` | IT/软件 | 47,883 |

可在 `glossaries/` 目录下添加自定义术语表。

## 项目结构

```
.claude/skills/translator/
├── skill.md              # 技能定义（完整文档）
├── scripts/              # 自动化脚本
├── templates/            # 配置模板 + 翻译提示词
├── glossaries/           # 术语表（按领域）
└── references/           # 翻译参考文档
```

## 速度参考（Gemini Flash + 20并发）

| 规模 | 耗时 | 示例 |
|------|------|------|
| 1万词 | 1-2分钟 | 短篇报告 |
| 5万词 | 5-10分钟 | 长篇论文 |
| 13万词 | 20-30分钟 | 书籍 |

## License

MIT
