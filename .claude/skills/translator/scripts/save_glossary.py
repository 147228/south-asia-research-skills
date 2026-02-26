# -*- coding: utf-8 -*-
"""
save_glossary.py - 术语表生成/导出工具
用法: python save_glossary.py <output_file.json>

从标准输入或交互式输入构建 LinguaGacha 兼容的术语表 JSON。
也可作为模块导入使用。

术语表格式:
[
  {"src": "English Term", "dst": "中文译名", "info": "备注说明"},
  ...
]
"""

import sys
import json
from pathlib import Path


def create_glossary_from_dict(entries: list, output_path: str):
    """从字典列表创建术语表文件"""
    output_path = Path(output_path)
    output_path.write_text(
        json.dumps(entries, ensure_ascii=False, indent=2),
        encoding='utf-8'
    )
    print(f"术语表已保存: {output_path}")
    print(f"  条目数: {len(entries)}")


def merge_glossaries(files: list, output_path: str):
    """合并多个术语表"""
    all_entries = []
    seen = set()
    for f in files:
        data = json.loads(Path(f).read_text(encoding='utf-8'))
        for entry in data:
            key = entry.get('src', '')
            if key and key not in seen:
                all_entries.append(entry)
                seen.add(key)
    create_glossary_from_dict(all_entries, output_path)


def interactive_create(output_path: str):
    """交互式创建术语表"""
    entries = []
    print("输入术语（输入空行结束）:")
    print("格式: English Term | 中文译名 | 备注（可选）")
    while True:
        line = input("> ").strip()
        if not line:
            break
        parts = [p.strip() for p in line.split('|')]
        if len(parts) >= 2:
            entry = {"src": parts[0], "dst": parts[1]}
            if len(parts) >= 3:
                entry["info"] = parts[2]
            else:
                entry["info"] = ""
            entries.append(entry)
            print(f"  已添加: {parts[0]} → {parts[1]}")
        else:
            print("  格式错误，请使用: English Term | 中文译名 | 备注")

    if entries:
        create_glossary_from_dict(entries, output_path)
    else:
        print("未输入任何条目。")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        print("\n用法:")
        print("  python save_glossary.py <output.json>           # 交互式创建")
        print("  python save_glossary.py merge <out.json> <in1.json> <in2.json> ...  # 合并术语表")
        sys.exit(1)

    if sys.argv[1] == 'merge' and len(sys.argv) >= 4:
        merge_glossaries(sys.argv[3:], sys.argv[2])
    else:
        interactive_create(sys.argv[1])


if __name__ == '__main__':
    main()
