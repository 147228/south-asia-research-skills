# 权威术语库来源指南

> 翻译前查阅本指南，选择合适的术语来源构建领域术语表。

## 可直接下载（结构化数据）

### 1. 微软语言门户术语集（IT/计算机）
- **URL**: https://learn.microsoft.com/en-us/globalization/reference/microsoft-terminology
- **下载**: https://download.microsoft.com/download/b/2/d/b2db7a7c-8d33-47f3-b2c1-ee5e6445cf45/MicrosoftTermCollection.zip
- **格式**: TBX (XML)，含简体中文（zh-CN）
- **覆盖**: 操作系统、办公软件、开发工具、云服务等全部 IT 术语
- **权威性**: ★★★★★ 行业标准，中文软件本地化事实标准

### 2. WHO ICD-11 国际疾病分类（医学）
- **URL**: https://icd.who.int/
- **API**: https://icd.who.int/icdapi （需注册 OAuth2）
- **格式**: JSON（API 返回）、Excel（下载区）
- **覆盖**: 17,000+ 疾病/病症编码，120,000+ 可编码医学术语，含中文版
- **权威性**: ★★★★★ WHO 官方，全球医学分类标准

### 3. ECDICT 英中词典数据库（通用词典）
- **URL**: https://github.com/skywind3000/ECDICT
- **下载**: GitHub 直接下载 CSV
- **格式**: CSV/SQLite，222万+ 词条
- **覆盖**: 通用英中词典，含柯林斯星级、牛津3000标记、考试标签
- **权威性**: ★★★☆☆ 社区维护，聚合多词典来源

### 4. CC-CEDICT 开源中英词典
- **URL**: https://www.mdbg.net/chinese/dictionary?page=cedict
- **下载**: MDBG.net 下载 ZIP
- **格式**: 纯文本，可通过工具转 JSON/CSV
- **覆盖**: 124,000+ 词条，含繁简体、拼音
- **权威性**: ★★★☆☆ CC 协议社区维护，1997 年起

## 在线查询（无法批量下载）

### 5. 术语在线 termonline.cn（科技全领域）
- **URL**: https://www.termonline.cn/
- **机构**: 全国科学技术名词审定委员会（国务院授权）
- **覆盖**: 45万+ 术语，100+ 学科（数理化生、工程、农医、人文社科、军事）
- **字段**: 规范中文名、英文名、定义、学科分类、台湾用名、缩写
- **API**: 机构用户可申请（联系 termonline@cnctst.cn）
- **权威性**: ★★★★★ 中国科学术语最高权威，国务院批准

### 6. UNTERM 联合国术语数据库（国际关系）
- **URL**: https://unterm.un.org/
- **覆盖**: 6种联合国官方语言（含中文），涵盖国名、条约名、机构名、地名
- **权威性**: ★★★★★ 联合国官方

### 7. CATL 中国特色话语术语库（政治话语）
- **URL**: http://term.catl.org.cn/
- **机构**: 中国翻译研究院 / 中国外文局
- **覆盖**: 5万+ 术语，中国政治话语的英/法/俄/德/日/韩等多语种翻译
- **权威性**: ★★★★★ 国家级政治话语翻译标准

### 8. IMF 多语种术语库（经济金融）
- **URL**: https://www.imf.org/en/About/Terminology
- **覆盖**: 15万+ 术语，货币银行、公共财政、国际收支、税收、统计等
- **权威性**: ★★★★★ IMF 官方

## 专业 PDF 参考（需 OCR/提取）

### 9. DTIC 英中军事术语对比词典
- **URL**: https://apps.dtic.mil/sti/tr/pdf/ADA307236.pdf
- **机构**: 美国国防技术信息中心 / 美国国会图书馆
- **覆盖**: PLA 军事术语，含简体中文、拼音、电报码、中美苏定义对比
- **权威性**: ★★★★☆ 美国政府出版，基于 PLA 来源

### 10. P5 核术语表（核军控）
- **URL**: https://digitallibrary.un.org/record/3956428
- **覆盖**: 核军控、裁军与防扩散术语，6种联合国语言含中文
- **机构**: 中美英法俄五国联合编制（中国牵头）
- **权威性**: ★★★★★ 五常联合官方出版

### 11. NATO AAP-06 术语表（军事）
- **URL**: https://nso.nato.int/natoterm/
- **覆盖**: 20,000+ 北约军事术语（仅英法，无中文）
- **用法**: 翻译北约术语时参考英文定义，交叉对照中文军事词典
- **权威性**: ★★★★★ NATO 官方

### 12. IATE 欧盟术语库（法律/贸易/环境）
- **URL**: https://iate.europa.eu/
- **下载**: https://iate.europa.eu/download-iate（可批量下载）
- **覆盖**: 700万+ 术语，24种EU语言（无中文）
- **用法**: 国际关系、贸易、法律术语的英文权威定义
- **权威性**: ★★★★★ 欧盟官方

## 使用建议

### 按翻译领域选择术语源

| 领域 | 首选来源 | 补充来源 |
|------|----------|----------|
| 科技（通用） | 术语在线 termonline.cn | 微软术语（IT子领域） |
| 医学/生物 | WHO ICD-11 + 术语在线 | - |
| 军事/国防 | DTIC 军事词典 + 本 skill 南亚军事术语表 | NATOTerm（英文参考） |
| 国际关系 | UNTERM + CATL | - |
| 经济金融 | IMF 术语库 | 世界银行术语表 |
| 中国政治话语 | CATL term.catl.org.cn | 中国时政术语汉英对照 |
| IT/计算机 | 微软术语集 | - |
| 法律/贸易 | IATE + UNTERM | - |

### 如何构建 LinguaGacha 术语表

1. 从上述来源查询目标领域术语
2. 整理为 JSON 格式：`[{"src": "English", "dst": "中文", "info": "备注"}]`
3. 保存到 `glossaries/领域名.json`
4. 翻译时通过 `--glossary` 参数指定
