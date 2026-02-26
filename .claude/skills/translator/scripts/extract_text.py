# -*- coding: utf-8 -*-
"""
extract_text.py - 从 docx/pdf/txt/epub 文件中提取纯文本
用法: python extract_text.py <input_file> [output_file]
"""

import sys
import re
from pathlib import Path


def extract_from_docx(file_path: Path) -> str:
    """从 .docx 文件提取文本"""
    try:
        from docx import Document
        doc = Document(str(file_path))
        paragraphs = [p.text for p in doc.paragraphs]
        return '\n'.join(paragraphs)
    except ImportError:
        # 备用方案：用 zipfile 直接解析
        import zipfile
        from xml.etree import ElementTree
        ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
        with zipfile.ZipFile(str(file_path)) as z:
            xml_content = z.read('word/document.xml')
        tree = ElementTree.fromstring(xml_content)
        paragraphs = []
        for para in tree.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p'):
            texts = [node.text for node in para.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t') if node.text]
            if texts:
                paragraphs.append(''.join(texts))
        return '\n'.join(paragraphs)


def extract_from_pdf(file_path: Path) -> str:
    """从 .pdf 文件提取文本（需要 PyMuPDF）"""
    try:
        import fitz  # PyMuPDF
        doc = fitz.open(str(file_path))
        text_parts = []
        for page in doc:
            text_parts.append(page.get_text())
        return '\n'.join(text_parts)
    except ImportError:
        print("错误：需要安装 PyMuPDF: pip install PyMuPDF")
        sys.exit(1)


def extract_from_txt(file_path: Path) -> str:
    """读取 .txt 文件"""
    encodings = ['utf-8', 'gbk', 'gb2312', 'latin-1']
    for enc in encodings:
        try:
            return file_path.read_text(encoding=enc)
        except (UnicodeDecodeError, UnicodeError):
            continue
    raise ValueError(f"无法识别文件编码: {file_path}")


def extract_from_epub(file_path: Path) -> str:
    """从 .epub 文件提取文本"""
    try:
        import ebooklib
        from ebooklib import epub
        from bs4 import BeautifulSoup

        book = epub.read_epub(str(file_path), options={'ignore_ncx': True})
        text_parts = []
        for item in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
            soup = BeautifulSoup(item.get_content(), 'html.parser')
            text = soup.get_text(separator='\n')
            text = text.strip()
            if text:
                text_parts.append(text)
        return '\n\n'.join(text_parts)
    except ImportError:
        print("错误：需要安装 ebooklib 和 beautifulsoup4: pip install ebooklib beautifulsoup4")
        sys.exit(1)


def clean_text(text: str) -> str:
    """清理提取的文本"""
    # 移除 InDesign 页面标记
    text = re.sub(r'[\w\s]+\.indd\s+\d+.*?\n?', '', text)
    # 移除时间戳
    text = re.sub(r'\d{1,2}/\d{1,2}/\d{4}\s+\d{1,2}:\d{2}:\d{2}\s+[AP]M\n?', '', text)
    # 压缩多余空行
    text = re.sub(r'\n{4,}', '\n\n\n', text)
    return text.strip()


def main():
    if len(sys.argv) < 2:
        print("用法: python extract_text.py <input_file> [output_file]")
        print("支持格式: .docx, .pdf, .txt, .epub")
        sys.exit(1)

    input_path = Path(sys.argv[1])
    if not input_path.exists():
        print(f"文件不存在: {input_path}")
        sys.exit(1)

    ext = input_path.suffix.lower()
    extractors = {
        '.docx': extract_from_docx,
        '.pdf': extract_from_pdf,
        '.txt': extract_from_txt,
        '.epub': extract_from_epub,
    }

    if ext not in extractors:
        print(f"不支持的格式: {ext}，支持: {', '.join(extractors.keys())}")
        sys.exit(1)

    print(f"正在提取: {input_path} ({ext})")
    text = extractors[ext](input_path)
    text = clean_text(text)

    # 输出路径
    if len(sys.argv) >= 3:
        output_path = Path(sys.argv[2])
    else:
        output_path = input_path.with_suffix('.clean.txt')

    output_path.write_text(text, encoding='utf-8')
    words = len(text.split())
    chars = len(text)
    print(f"提取完成: {output_path}")
    print(f"  字符数: {chars:,}")
    print(f"  词数: {words:,}")
    print(f"  行数: {len(text.splitlines()):,}")


if __name__ == '__main__':
    main()
