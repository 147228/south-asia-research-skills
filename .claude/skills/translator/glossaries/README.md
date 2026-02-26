# 术语表 (Glossaries)

本目录存放 LinguaGacha 兼容的 JSON 格式术语表，按领域分文件组织。

## 预置术语表

| 文件 | 领域 | 条目数 | 来源 |
|------|------|--------|------|
| `south_asia_military.json` | 南亚军政（人名、地名、军事术语） | 108 | 新华社、军科院标准译法 |
| `microsoft_it_terminology.json` | IT/软件术语 | 47,883 | Microsoft Language Portal |

## 自动选择机制

翻译时，`run_linguagacha.py` 会扫描输入文本前100行，根据关键词匹配自动选择最相关的术语表。如果没有匹配的领域，则不加载术语表。

也可通过 `--glossary` 参数手动指定。

## 格式规范

术语表使用 LinguaGacha 兼容的 JSON 数组格式：

```json
[
  {"src": "English Term", "dst": "中文译名", "info": "备注说明"},
  {"src": "Another Term", "dst": "另一个译名", "info": "来源或上下文"}
]
```

字段说明：
- `src`：英文原词（必填）
- `dst`：中文译名（必填）
- `info`：备注信息（可选，如来源、适用场景等）

## 添加新术语表

1. 创建符合上述格式的 JSON 文件，放入本目录
2. 在 `scripts/run_linguagacha.py` 的 `DOMAIN_KEYWORDS` 字典中添加对应关键词映射
3. 翻译时系统将自动检测并使用

也可使用 `scripts/save_glossary.py` 交互式创建术语表。

## 权威来源推荐

构建术语表时，优先参考以下来源（详见 `references/terminology_sources.md`）：

- 全国科学技术名词审定委员会（术语在线 termonline.cn）
- 联合国术语数据库（UNTERM）
- 微软语言门户（Microsoft Language Portal）
- 中国社科院各研究所出版物
- 外交部官方翻译
