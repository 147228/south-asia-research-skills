# -*- coding: utf-8 -*-
"""
Format the translated book into a proper Markdown document.
Version 2 - fixes heading separation issues.
"""
import re

INPUT_FILE = r"C:\Users\bisu5\Desktop\南亚研究skills\naravane_translated_clean.txt"
OUTPUT_FILE = r"C:\Users\bisu5\Desktop\南亚研究skills\《命运的四颗星》纳拉瓦内回忆录_中文译本.md"

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    raw_text = f.read()

lines = raw_text.split('\n')
lines = [line.rstrip() for line in lines]

# ═══════════════════════════════════════════════════════════
# PHASE 1: Extract sections from the raw file
# ═══════════════════════════════════════════════════════════

# Lines 5-17 (1-indexed): 本书各界赞誉
praise_lines = lines[4:17]

# Lines 131+ (1-indexed, 130+ 0-indexed): actual content (序言 onwards)
content_lines = lines[130:]

# ═══════════════════════════════════════════════════════════
# PHASE 2: Clean individual lines
# ═══════════════════════════════════════════════════════════

def is_running_header(line):
    """Return True if the line is a running page header/footer to remove."""
    s = line.strip()
    if not s:
        return False

    # Standalone roman numeral page numbers
    if re.match(r'^[xivXIV]+$', s):
        return True

    # Standalone arabic page numbers
    if re.match(r'^\d{1,3}$', s):
        return True

    # "NNN命运的四颗星" or "命运的四颗星NNN"
    if re.match(r'^\d{1,3}命运的四颗星$', s) or re.match(r'^命运的四颗星\d{1,3}$', s):
        return True

    # Chapter title + page number patterns
    header_patterns = [
        r'^擦伤.*\d+$',
        r'^磨砺.*\d+$',
        r'^从便装.*\d+$',
        r'^从平民.*\d+$',
        r'^胜利属于.*\d+$',
        r'^谁说谁得福.*\d+$',
        r'^凡呼喊者.*\d+$',
        r'^高呼者.*\d+$',
        r'^谁呼喊.*\d+$',
        r'^凡发此言.*\d+$',
        r'^奔赴异国.*\d+$',
        r'^奔赴异域.*\d+$',
        r'^战斗与参谋\d+$',
        r'^战斗部队与参谋.*\d+$',
        r'^指挥与参谋\d+$',
        r'^一线与机关\d+$',
        r'^前线与参谋\d+$',
        r'^密拉特.*\d+$',
        r'^营级指挥.*\d+$',
        r'^营指挥部.*\d+$',
        r'^向东看.*\d+$',
        r'^致谢\d+$',
        r'^注释\d+$',
        r'^\d+注释$',
        r'^缩略语表\d+$',
        r'^\d+缩略语表$',
        r'^老兵永不死.*\d+$',
        r'^老兵不死.*\d+$',
        r'^回归行伍.*\d+$',
        r'^再次向东.*\d+$',
        r'^弯刀军.*\d+$',
        r'^东向行动.*\d+$',
        r'^序言[xiv]+$',
        r'^[xiv]+引言$',
        r'^引言[xiv]+$',
        r'^[xiv]+序言$',
        r'^x目录$',
        # Running headers like "突破257" etc
        r'^突破\d+$',
        r'^短兵相接.*\d+$',
        r'^突围.*\d+$',
        r'^改组\d+$',
        r'^巩固\d+$',
        r'^履新\d+$',
        r'^"印度观光".*\d+$',
    ]

    for pat in header_patterns:
        if re.match(pat, s):
            return True

    return False

def clean_spaces(text):
    """Remove stray spaces within Chinese text."""
    # Chinese char + spaces + Chinese char
    text = re.sub(r'([\u4e00-\u9fff])\s+([\u4e00-\u9fff])', r'\1\2', text)
    text = re.sub(r'([\u4e00-\u9fff])\s+([\u4e00-\u9fff])', r'\1\2', text)
    # Also fix "- " within Chinese compounds like "自我- 反思"
    text = re.sub(r'([\u4e00-\u9fff])-\s+([\u4e00-\u9fff])', r'\1\2', text)
    return text

# ═══════════════════════════════════════════════════════════
# PHASE 3: Process content into structured sections
# ═══════════════════════════════════════════════════════════

output_blocks = []  # Each block is a string (heading or paragraph)

i = 0
while i < len(content_lines):
    line = content_lines[i].strip()

    # Skip empty lines
    if not line:
        i += 1
        continue

    # Skip running headers
    if is_running_header(line):
        i += 1
        continue

    # ── Detect headings ──

    # 序言 (standalone)
    if line == '序言' and i < 5:
        output_blocks.append('\n## 序言\n')
        i += 1
        continue

    # 引言 (standalone, after 序言 content)
    if line == '引言':
        output_blocks.append('\n## 引言\n')
        i += 1
        continue

    # 致谢 (standalone)
    if line == '致谢':
        output_blocks.append('\n## 致谢\n')
        i += 1
        continue

    # 注释 (standalone)
    if line == '注释':
        output_blocks.append('\n## 注释\n')
        i += 1
        continue

    # 缩略语表 (standalone)
    if line == '缩略语表':
        output_blocks.append('\n## 缩略语表\n')
        i += 1
        continue

    # ── Part headers ──
    # "第一部分" followed by subtitle on next non-empty line
    part_match = re.match(r'^第([一二三四五])部分$', line)
    if not part_match:
        # Also match "第4部分" style
        part_match2 = re.match(r'^第(\d)部分$', line)
        if part_match2:
            num_map = {'1':'一','2':'二','3':'三','4':'四','5':'五'}
            num = num_map.get(part_match2.group(1), part_match2.group(1))
            # Look for subtitle
            j = i + 1
            subtitle = ''
            while j < len(content_lines) and j < i + 4:
                next_l = content_lines[j].strip()
                if next_l and not is_running_header(next_l):
                    subtitle = next_l
                    j += 1
                    break
                j += 1
            if subtitle:
                output_blocks.append(f'\n## 第{num}部分：{clean_spaces(subtitle)}\n')
            else:
                output_blocks.append(f'\n## 第{num}部分\n')
            i = j
            continue

    if part_match:
        num = part_match.group(1)
        # Look for subtitle on next non-empty line(s)
        j = i + 1
        subtitle = ''
        while j < len(content_lines) and j < i + 4:
            next_l = content_lines[j].strip()
            if next_l and not is_running_header(next_l):
                subtitle = next_l
                j += 1
                break
            j += 1
        if subtitle:
            output_blocks.append(f'\n## 第{num}部分：{clean_spaces(subtitle)}\n')
        else:
            output_blocks.append(f'\n## 第{num}部分\n')
        i = j
        continue

    # ── Chapter headers: "X.Y" on its own line ──
    chapter_match = re.match(r'^([1-5])\.([1-9])$', line)
    if chapter_match:
        chapter_num = line
        # Collect title from next non-empty lines
        # Titles can span blank lines if the first part appears incomplete
        j = i + 1
        title_parts = []
        hit_blank_after_title = False
        while j < len(content_lines) and len(title_parts) < 6:
            next_l = content_lines[j].strip()
            if not next_l:
                if title_parts:
                    current_title = ''.join(title_parts)
                    # Allow crossing one blank line if:
                    # 1. Title ends with a continuation character, OR
                    # 2. Total title text is still short (likely incomplete)
                    incomplete_endings = ('了', '于', '从', '的', '与', '到', '在')
                    if current_title[-1:] in incomplete_endings or len(current_title) <= 18:
                        hit_blank_after_title = True
                        j += 1
                        continue
                    else:
                        break
                j += 1
                continue
            if is_running_header(next_l):
                j += 1
                continue
            # Stop if it looks like actual paragraph content (long line)
            if len(next_l) > 60 and len(title_parts) > 0:
                break
            # After crossing a blank line, be strict about what to accept
            if hit_blank_after_title and len(title_parts) > 0:
                # Reject if it looks like paragraph content:
                # starts with date, ends with sentence-final punctuation, or is long
                if (re.match(r'^\d{4}年', next_l) or
                    next_l.endswith('。') or next_l.endswith('？') or
                    next_l.endswith('！') or
                    len(next_l) > 20):
                    break
            title_parts.append(next_l)
            hit_blank_after_title = False
            j += 1
            # If we got enough title text, stop
            combined = ''.join(title_parts)
            if len(combined) > 25:
                break

        title = ''.join(title_parts)
        title = clean_spaces(title)
        output_blocks.append(f'\n### {chapter_num} {title}\n')
        i = j
        continue

    # ── Skip redundant standalone part subtitles ──
    if line in ('将官职衔', '将官职级', '童年与青少年时期', '团队生活', '命运的四颗星', '思考与感悟'):
        # Check if this was already captured as part of a part header
        # If the previous block is a part heading, skip this
        if output_blocks and output_blocks[-1].startswith('\n##'):
            i += 1
            continue
        # Otherwise, if "思考与感悟" appears standalone after part heading was missed
        i += 1
        continue

    # ── Skip "老兵永不死 . . ." standalone (section title within Part 5) ──
    if line.startswith('老兵永不死'):
        i += 1
        continue

    # ── Regular content paragraph ──
    paragraph = clean_spaces(line)
    output_blocks.append(paragraph)
    i += 1

# ═══════════════════════════════════════════════════════════
# PHASE 4: Build the praise section
# ═══════════════════════════════════════════════════════════

praise_text = ""
for line in praise_lines:
    s = line.strip()
    if s and s != '本书各界赞誉':
        praise_text += clean_spaces(s) + "\n\n"

# ═══════════════════════════════════════════════════════════
# PHASE 5: Assemble final document
# ═══════════════════════════════════════════════════════════

translation_note = """> 【译者说明】本书原著为英文版 *Four Stars of Destiny* (2024), 作者为印度第28任陆军参谋长曼诺杰·穆昆德·纳拉瓦内上将(Gen. Manoj Mukund Naravane)。本译文采用LinguaGacha + Gemini翻译引擎完成初译，经Claude Code审校整理。术语表参照中国军事科学院、新华社等权威来源。
"""

book_title = """# 命运的四颗星

**Four Stars of Destiny**

*曼诺杰·穆昆德·纳拉瓦内上将 著*

*印度第28任陆军参谋长*
"""

doc_parts = [
    translation_note,
    "",
    book_title,
    "---",
    "",
    "## 本书各界赞誉",
    "",
    praise_text,
    "---",
    "",
]

# Add main content - ensure headings are separated from paragraphs
for block in output_blocks:
    doc_parts.append(block)

full_text = '\n'.join(doc_parts)

# Final cleanup: remove excessive blank lines
full_text = re.sub(r'\n{4,}', '\n\n\n', full_text)

# Write
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write(full_text)

print(f"Output written to: {OUTPUT_FILE}")
print(f"Total characters: {len(full_text)}")

# Verify structure
headings = re.findall(r'^(#{1,3} .+)$', full_text, re.MULTILINE)
print(f"\nDocument structure ({len(headings)} headings):")
for h in headings:
    print(f"  {h}")
