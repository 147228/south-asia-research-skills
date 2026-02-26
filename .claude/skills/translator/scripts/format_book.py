# -*- coding: utf-8 -*-
"""
format_book.py - 通用书籍/文档 Markdown 格式化工具
用法: python format_book.py <input_file> [output_file]

功能：
- 清理翻译文本中的页码、页眉页脚
- 识别并格式化标题结构（部/章/节）
- 清理中文间多余空格
- 生成结构化 Markdown 文档
"""

import sys
import re
from pathlib import Path


def clean_spaces(text):
    """Remove stray spaces within Chinese text."""
    text = re.sub(r'([\u4e00-\u9fff])\s+([\u4e00-\u9fff])', r'\1\2', text)
    text = re.sub(r'([\u4e00-\u9fff])\s+([\u4e00-\u9fff])', r'\1\2', text)
    text = re.sub(r'([\u4e00-\u9fff])-\s+([\u4e00-\u9fff])', r'\1\2', text)
    return text


def is_page_number(line):
    """判断是否是独立页码行"""
    s = line.strip()
    if not s:
        return False
    # 独立阿拉伯数字页码
    if re.match(r'^\d{1,4}$', s):
        return True
    # 独立罗马数字页码
    if re.match(r'^[xivXIV]+$', s):
        return True
    return False


def detect_heading(line):
    """
    检测标题行，返回 (level, text) 或 None。
    支持多种常见标题格式：
    - "Chapter X: ..." / "CHAPTER X"
    - "Part X: ..." / "PART X"
    - "第X章 ..." / "第X部分 ..."
    - 全大写短行（可能是节标题）
    """
    s = line.strip()
    if not s or len(s) > 100:
        return None

    # "Part X" / "PART X" / "第X部分"
    if re.match(r'^(PART|Part)\s+[IVXLC\d]+', s):
        return (2, s)
    if re.match(r'^第[一二三四五六七八九十\d]+部分', s):
        return (2, s)

    # "Chapter X" / "CHAPTER X" / "第X章"
    if re.match(r'^(CHAPTER|Chapter)\s+\d+', s):
        return (3, s)
    if re.match(r'^第[一二三四五六七八九十百\d]+章', s):
        return (3, s)

    # 数字编号章节 "1.1" "2.3" 等独立行
    if re.match(r'^\d+\.\d+$', s):
        return (3, s)

    # 全大写英文短行（可能是节标题）
    if s.isupper() and len(s) < 60 and len(s.split()) <= 10:
        return (2, s)

    return None


def format_document(input_path, output_path=None, book_title=None, author=None, translator_note=None):
    """主格式化函数"""
    text = Path(input_path).read_text(encoding='utf-8')
    lines = text.split('\n')
    lines = [line.rstrip() for line in lines]

    output_blocks = []

    # 添加书籍元信息（如提供）
    if book_title:
        output_blocks.append(f'# {book_title}\n')
    if author:
        output_blocks.append(f'*{author}*\n')
    if translator_note:
        output_blocks.append(f'> {translator_note}\n')
    if book_title or author or translator_note:
        output_blocks.append('---\n')

    i = 0
    while i < len(lines):
        line = lines[i].strip()

        # 跳过空行
        if not line:
            i += 1
            continue

        # 跳过独立页码
        if is_page_number(line):
            i += 1
            continue

        # 检测标题
        heading = detect_heading(line)
        if heading:
            level, text = heading
            prefix = '#' * level
            output_blocks.append(f'\n{prefix} {clean_spaces(text)}\n')
            i += 1
            continue

        # 普通段落
        paragraph = clean_spaces(line)
        output_blocks.append(paragraph)
        i += 1

    full_text = '\n'.join(output_blocks)

    # 清理多余空行
    full_text = re.sub(r'\n{4,}', '\n\n\n', full_text)

    # 输出
    if not output_path:
        output_path = Path(input_path).with_suffix('.formatted.md')
    else:
        output_path = Path(output_path)

    output_path.write_text(full_text, encoding='utf-8')
    print(f"格式化完成: {output_path}")
    print(f"  总字符: {len(full_text):,}")

    # 显示文档结构
    headings = re.findall(r'^(#{1,3} .+)$', full_text, re.MULTILINE)
    print(f"\n文档结构 ({len(headings)} 个标题):")
    for h in headings:
        print(f"  {h}")


def main():
    if len(sys.argv) < 2:
        print("用法: python format_book.py <input_file> [output_file]")
        print("  将翻译文本格式化为结构化 Markdown")
        print("  自动清理页码、页眉，识别标题结构")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) >= 3 else None
    format_document(input_path, output_path)


if __name__ == '__main__':
    main()
