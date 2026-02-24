# -*- coding: utf-8 -*-
"""
format_supremacy.py v4 - 格式化 Supremacy 译本
正确处理 epub 拆分的章节标题和断裂段落
"""
import re
from pathlib import Path

INPUT_FILE = Path(r"C:\Users\bisu5\Desktop\南亚研究skills\supremacy_project.translated.txt")
OUTPUT_FILE = Path(r"C:\Users\bisu5\Desktop\南亚研究skills\《至高之争》AI竞赛与世界变局_中文译本.md")

raw = INPUT_FILE.read_text(encoding='utf-8')
lines = raw.split('\n')
lines = [l.rstrip() for l in lines]

# 定位正文起点（找到"献给"之后的内容）
start_idx = 0
for i, line in enumerate(lines):
    if line.strip().startswith('献给'):
        start_idx = i
        break

content = lines[start_idx:]

# ═══ 辅助函数 ═══

def is_page_number(s):
    s = s.strip()
    return bool(s and re.match(r'^(\d{1,3}|[xivXIV]+)$', s))

def is_epub_junk(s):
    s = s.strip()
    junk = ['us.macmillan.com', 'macmillanusa.com', '电子书', '版权是违法',
            '出版集团', '新闻邮件', '访问我们', '正文开始', '印刷版',
            '开始阅读', '封面页', '关于作者', '版权页', '购买此',
            '特别优惠', '侵犯版权', '通知出版商', '订阅新闻', '指南封面',
            '扉页', '版权声明', '版权正文', 'Newsletter', 'Copyright']
    return any(m in s for m in junk)

TERMINAL = set('。？！；」）】')

def ends_complete(s):
    s = s.rstrip()
    if not s:
        return True
    c = s[-1]
    if c in TERMINAL:
        return True
    if c in '.?!)' and len(s) > 20:  # 英文句末
        return True
    return False

# TOC 中的标题（有冒号版，用于构建标题映射）
toc_chapters = {}  # {章节号: 标题}
toc_acts = {}      # {幕号: 标题}
for line in lines[:200]:
    s = line.strip()
    m = re.match(r'^第(\d+)章[：:]\s*(.+)$', s)
    if m:
        toc_chapters[m.group(1)] = m.group(2)
    m = re.match(r'^第([一二三四])幕[：:]\s*(.+)$', s)
    if m:
        toc_acts[m.group(1)] = m.group(2)

print(f"TOC: {len(toc_acts)} 幕, {len(toc_chapters)} 章")

# ═══ Phase 1: 遍历内容行，识别标题并合并断裂段落 ═══

NUM_MAP = {'1': '一', '2': '二', '3': '三', '4': '四'}
ZH_NUM = {'一': '1', '二': '2', '三': '3', '四': '4', '五': '5', '六': '6',
           '七': '7', '八': '8', '九': '9', '十': '10', '十一': '11', '十二': '12',
           '十三': '13', '十四': '14', '十五': '15', '十六': '16'}
output = []

# 书名
output.append("""> 【译者说明】本书原著为英文版 *Supremacy: AI, ChatGPT, and the Race That Will Change the World* (2024)，作者为帕尔米·奥尔森（Parmy Olson），彭博社专栏作家。本译文采用 LinguaGacha + Gemini 翻译引擎完成初译，经 Claude Code 审校整理。

# 至高之争：AI、ChatGPT与改变世界的竞赛

**Supremacy: AI, ChatGPT, and the Race That Will Change the World**

*帕尔米·奥尔森（Parmy Olson）著*

---
""")

def next_nonblank(lines, start):
    """找到下一个非空、非页码行及其索引"""
    j = start
    while j < len(lines):
        s = lines[j].strip()
        if s and not is_page_number(s) and not is_epub_junk(s):
            return j, s
        j += 1
    return j, ''

seen = set()
skip_lines = {'目录', '扉页', '版权声明', '献词', '序言', 'Contents', 'Title Page',
              'Copyright Notice', 'Dedication', 'Cover', 'Guide', 'Newsletter Sign-up',
              'Copyright', 'Also by Parmy Olson', 'About the Author', '索引', 'Index',
              '关于作者', '时事通讯注册', '版权', '订阅新闻简报版权'}

i = 0
while i < len(content):
    s = content[i].strip()

    if not s or is_page_number(s) or is_epub_junk(s):
        i += 1
        continue

    # 跳过 epub 元数据
    if s in skip_lines:
        i += 1
        continue

    # ─── 献词 ───
    if s.startswith('献给'):
        output.append(f'\n*{s}*\n')
        i += 1
        continue

    # ─── 序言 ───
    if s == '序言' and '序言' not in seen:
        output.append('\n## 序言\n')
        seen.add('序言')
        i += 1
        continue

    # ─── 幕标题（带冒号） ───
    m = re.match(r'^第([一二三四])幕[：:]\s*(.+)$', s)
    if m and f'act_{m.group(1)}' not in seen:
        output.append(f'\n## 第{m.group(1)}幕：{m.group(2)}\n')
        seen.add(f'act_{m.group(1)}')
        i += 1
        continue

    # ─── 幕标题（拆分形式："第X幕" 独立行） ───
    m = re.match(r'^第([一二三四])幕$', s)
    if m and f'act_{m.group(1)}' not in seen:
        act_num = m.group(1)
        # 从下一个非空行获取副标题
        j, subtitle = next_nonblank(content, i + 1)
        # 用 TOC 中的标题如果有的话
        if act_num in toc_acts:
            subtitle = toc_acts[act_num]
        output.append(f'\n## 第{act_num}幕：{subtitle}\n')
        seen.add(f'act_{act_num}')
        # 跳过副标题行
        i = j + 1
        continue

    # ─── 章标题（带冒号） ───
    m = re.match(r'^第(\d+)章[：:]\s*(.+)$', s)
    if m and f'ch_{m.group(1)}' not in seen:
        output.append(f'\n### 第{m.group(1)}章：{m.group(2)}\n')
        seen.add(f'ch_{m.group(1)}')
        i += 1
        continue

    # ─── 章标题（拆分形式："第X章" 独立行） ───
    m = re.match(r'^第(\d+)章$', s)
    if m and f'ch_{m.group(1)}' not in seen:
        ch_num = m.group(1)
        j, subtitle = next_nonblank(content, i + 1)
        if ch_num in toc_chapters:
            subtitle = toc_chapters[ch_num]
        output.append(f'\n### 第{ch_num}章：{subtitle}\n')
        seen.add(f'ch_{ch_num}')
        i = j + 1
        continue

    # ─── 章标题（中文数字："第一章" 等） ───
    m = re.match(r'^第([一二三四五六七八九十]+)章(?:[：: ]\s*(.+))?$', s)
    if m:
        zh_n = m.group(1)
        ch_num = ZH_NUM.get(zh_n, zh_n)
        if f'ch_{ch_num}' not in seen:
            subtitle = m.group(2) or ''
            if not subtitle:
                j, subtitle = next_nonblank(content, i + 1)
            else:
                j = i
            if ch_num in toc_chapters and not subtitle:
                subtitle = toc_chapters[ch_num]
            output.append(f'\n### 第{ch_num}章：{subtitle}\n')
            seen.add(f'ch_{ch_num}')
            i = j + 1
            continue

    # ─── 英文幕/章标题（跳过） ───
    if re.match(r'^(Act \d|Chapter \d)', s, re.I):
        i += 1
        continue

    # ─── 致谢 ───
    if s in ('致谢', 'Acknowledgments') and '致谢' not in seen:
        output.append('\n## 致谢\n')
        seen.add('致谢')
        i += 1
        continue

    # ─── 资料来源 ───
    if s in ('资料来源', 'Sources') and '资料来源' not in seen:
        output.append('\n## 资料来源\n')
        seen.add('资料来源')
        i += 1
        continue

    # ─── 索引 ───
    if s in ('索引', 'Index') and '索引' not in seen:
        output.append('\n## 索引\n')
        seen.add('索引')
        i += 1
        continue

    # ─── 跳过垃圾合并行 ───
    if re.match(r'^第[一二三四]幕.{0,4}第\d+章', s):
        i += 1
        continue

    # ─── 正文段落 ───
    # 收集完整段落（合并断裂行）
    para = s
    i += 1
    while i < len(content) and not ends_complete(para):
        ns = content[i].strip()
        if not ns:
            # 空行：检查后面是不是碎片
            j, next_s = next_nonblank(content, i + 1)
            if next_s and not re.match(r'^第[一二三四]幕', next_s) and \
               not re.match(r'^第\d+章', next_s) and \
               next_s not in ('致谢', '资料来源', '索引', 'Acknowledgments', 'Sources', 'Index') and \
               len(next_s) < 50:
                # 短碎片，合并
                para = para + next_s
                i = j + 1
                continue
            else:
                break
        elif is_page_number(ns) or is_epub_junk(ns):
            i += 1
            continue
        elif re.match(r'^第[一二三四]幕', ns) or re.match(r'^第\d+章', ns):
            break
        elif ns in skip_lines or ns in ('致谢', '资料来源', '索引'):
            break
        else:
            # 非空、非标题行，且当前段落未完成
            para = para + ns
            i += 1
            continue
        break

    # 清理
    para = re.sub(r'([\u4e00-\u9fff])\s+([\u4e00-\u9fff])', r'\1\2', para)
    para = re.sub(r'([\u4e00-\u9fff])\s+([\u4e00-\u9fff])', r'\1\2', para)
    output.append(para + '\n')

full = '\n'.join(output)
full = re.sub(r'\n{4,}', '\n\n\n', full)

OUTPUT_FILE.write_text(full, encoding='utf-8')

headings = re.findall(r'^(#{1,3} .+)$', full, re.MULTILINE)
total_zh = len(re.findall(r'[\u4e00-\u9fff]', full))
print(f"输出: {OUTPUT_FILE}")
print(f"总字符: {len(full):,}")
print(f"中文字符: {total_zh:,}")
print(f"标题: {len(headings)}")
for h in headings:
    print(f"  {h}")
