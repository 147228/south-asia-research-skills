# -*- coding: utf-8 -*-
"""
run_linguagacha.py - LinguaGacha 翻译流水线控制脚本
用法:
  python run_linguagacha.py setup          # 首次配置
  python run_linguagacha.py create <input>  # 创建项目
  python run_linguagacha.py start           # 开始翻译
  python run_linguagacha.py status          # 查看进度
  python run_linguagacha.py export          # 导出翻译
  python run_linguagacha.py retry           # 重试失败项
"""

import sys
import os
import json
import sqlite3
import subprocess
import shutil
from pathlib import Path

# === 路径配置 ===
SKILLS_DIR = Path(__file__).parent.parent
BASE_DIR = SKILLS_DIR.parent.parent.parent  # 回到项目根目录
LG_DIR = BASE_DIR / "LinguaGacha" / "LinguaGacha"
LG_EXE = LG_DIR / "app.exe"
TEMPLATES_DIR = SKILLS_DIR / "templates"
GLOSSARIES_DIR = SKILLS_DIR / "glossaries"


def check_lg_installed():
    """检查 LinguaGacha 是否已安装"""
    if not LG_EXE.exists():
        print("LinguaGacha 未安装。")
        print(f"请下载 LinguaGacha 并解压到: {LG_DIR.parent}")
        print("下载地址: https://github.com/neavo/LinguaGacha/releases")
        return False
    return True


# === 领域关键词映射（用于智能选择术语表） ===
DOMAIN_KEYWORDS = {
    'microsoft_it_terminology.json': [
        'software', 'API', 'server', 'database', 'cloud', 'Windows', 'Azure',
        'Microsoft', 'Linux', 'Docker', 'Kubernetes', 'DevOps', 'SQL', 'HTTP',
        'TCP', 'DNS', 'SSL', 'firewall', 'virtual machine', 'deployment',
        'backend', 'frontend', 'framework', 'SDK', 'runtime', 'compiler',
        'GitHub', 'repository', 'pipeline', 'microservice', 'REST', 'JSON',
    ],
    'south_asia_military.json': [
        'India', 'Pakistan', 'Kashmir', 'Modi', 'military', 'border',
        'defence', 'defense', 'army', 'navy', 'air force', 'battalion',
        'brigade', 'division', 'corps', 'regiment', 'LAC', 'LoC',
        'Ladakh', 'Galwan', 'Doklam', 'Siachen', 'COAS', 'CDS',
        'nuclear', 'missile', 'ceasefire', 'insurgency', 'AFSPA',
        'Delhi', 'Islamabad', 'Sri Lanka', 'Bangladesh', 'Nepal',
    ],
}


def detect_domain(input_path):
    """扫描输入文本前100行，检测最匹配的领域术语表"""
    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            sample = ''.join(f.readline() for _ in range(100))
    except Exception:
        return None

    sample_lower = sample.lower()
    scores = {}
    for glossary_name, keywords in DOMAIN_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw.lower() in sample_lower)
        if score > 0:
            scores[glossary_name] = score

    if not scores:
        return None

    best = max(scores, key=scores.get)
    print(f"领域检测: {', '.join(f'{k}={v}' for k, v in sorted(scores.items(), key=lambda x: -x[1]))}")
    print(f"自动选择术语表: {best} (匹配 {scores[best]} 个关键词)")
    return best


def find_glossary(glossary_arg=None, input_path=None):
    """查找术语表（支持手动指定或智能检测）"""
    # 手动指定优先
    if glossary_arg:
        p = Path(glossary_arg)
        if p.exists():
            return p
        p2 = GLOSSARIES_DIR / glossary_arg
        if p2.exists():
            return p2
        print(f"术语表不存在: {glossary_arg}")
        return None

    # 智能检测：根据输入文本内容选择
    if input_path:
        detected = detect_domain(input_path)
        if detected:
            glossary_path = GLOSSARIES_DIR / detected
            if glossary_path.exists():
                return glossary_path
        else:
            print("未检测到匹配领域，不加载术语表")
            return None

    # 兜底：无输入文件时不自动加载
    return None


def setup_config(api_url=None, api_key=None, model_id=None, concurrency=20):
    """生成 LinguaGacha 配置文件"""
    template = TEMPLATES_DIR / "linguagacha_config.json"
    if template.exists():
        config = json.loads(template.read_text(encoding='utf-8'))
    else:
        config = {
            "version": "0.55.0",
            "source_language": "EN",
            "target_language": "ZH",
            "activate_model_id": "custom-model",
            "models": [{
                "id": "custom-model",
                "type": "CUSTOM_OPENAI",
                "name": "Custom Model",
                "api_format": "OpenAI",
                "api_url": "https://your-api-provider.com/v1",
                "api_key": "your-api-key",
                "model_id": "gemini-3-flash-preview",
                "request": {"extra_headers": {}, "extra_body": {},
                            "extra_headers_custom_enable": False,
                            "extra_body_custom_enable": False},
                "threshold": {"input_token_limit": 512, "output_token_limit": 16384,
                              "rpm_limit": 0, "concurrency_limit": 20},
                "thinking": {"level": "OFF"},
                "generation": {"temperature": 0.3, "temperature_custom_enable": True,
                               "top_p": 0.95, "top_p_custom_enable": False,
                               "presence_penalty": 0.0, "presence_penalty_custom_enable": False,
                               "frequency_penalty": 0.0, "frequency_penalty_custom_enable": False}
            }],
            "request_timeout": 120,
            "expert_mode": False,
            "proxy_url": "", "proxy_enable": False,
            "auto_glossary_enable": False,
            "glossary_default_preset": ""
        }

    # 覆盖参数
    model = config["models"][0]
    if api_url:
        model["api_url"] = api_url
    if api_key:
        model["api_key"] = api_key
    if model_id:
        model["model_id"] = model_id
    model["threshold"]["concurrency_limit"] = concurrency

    output = BASE_DIR / "linguagacha_config.json"
    output.write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"配置已保存: {output}")
    print(f"  API: {model['api_url']}")
    print(f"  模型: {model['model_id']}")
    print(f"  并发: {concurrency}")
    return output


def create_project(input_path, project_name=None, glossary=None):
    """创建 LinguaGacha 翻译项目"""
    if not check_lg_installed():
        return

    input_path = Path(input_path)
    if not input_path.exists():
        print(f"输入文件不存在: {input_path}")
        return

    # 准备输入目录
    lg_input = BASE_DIR / "lg_input"
    lg_input.mkdir(exist_ok=True)
    if input_path.is_file():
        shutil.copy2(input_path, lg_input / input_path.name)
    elif input_path.is_dir():
        for f in input_path.iterdir():
            if f.suffix in ('.txt', '.md', '.srt', '.ass'):
                shutil.copy2(f, lg_input / f.name)

    # 项目文件路径
    if not project_name:
        project_name = input_path.stem
    project_file = BASE_DIR / f"{project_name}.lg"

    # 构建命令
    config_path = BASE_DIR / "linguagacha_config.json"
    prompt_path = TEMPLATES_DIR / "academic_prompt.txt"

    cmd = [
        str(LG_EXE), "--cli", "--create",
        "--input", str(lg_input),
        "--project", str(project_file),
        "--config", str(config_path),
        "--source_language", "EN",
        "--target_language", "ZH",
    ]

    if glossary:
        glossary_path = find_glossary(glossary)
    else:
        glossary_path = find_glossary(input_path=input_path)

    if glossary_path:
        cmd.extend(["--glossary", str(glossary_path)])

    if prompt_path.exists():
        cmd.extend(["--custom_prompt_zh", str(prompt_path)])

    print(f"正在创建项目并启动翻译...")
    print(f"  项目: {project_file}")
    print(f"  命令: {' '.join(cmd[:6])}...")
    subprocess.run(cmd)


def check_status(project_file):
    """检查翻译进度"""
    project_file = Path(project_file)
    if not project_file.exists():
        print(f"项目文件不存在: {project_file}")
        return

    conn = sqlite3.connect(str(project_file))
    c = conn.cursor()

    c.execute('SELECT data FROM items')
    status_counts = {}
    total = 0
    for row in c.fetchall():
        data = json.loads(row[0])
        s = data.get('status', 'UNKNOWN')
        status_counts[s] = status_counts.get(s, 0) + 1
        total += 1

    conn.close()

    processed = status_counts.get('PROCESSED', 0)
    skipped = status_counts.get('LANGUAGE_SKIPPED', 0) + status_counts.get('RULE_SKIPPED', 0)
    pending = status_counts.get('PENDING', 0)
    error = status_counts.get('ERROR', 0)

    print(f"=== 翻译进度 ===")
    print(f"总条目: {total}")
    print(f"已翻译: {processed} ({processed/total*100:.1f}%)")
    print(f"已跳过: {skipped}")
    print(f"待处理: {pending}")
    print(f"失败: {error}")

    for s, cnt in sorted(status_counts.items(), key=lambda x: -x[1]):
        print(f"  {s}: {cnt}")


def export_translation(project_file, output_file=None):
    """从项目数据库导出翻译"""
    project_file = Path(project_file)
    if not project_file.exists():
        print(f"项目文件不存在: {project_file}")
        return

    conn = sqlite3.connect(str(project_file))
    c = conn.cursor()
    c.execute('SELECT data FROM items ORDER BY id')

    lines = []
    for row in c.fetchall():
        data = json.loads(row[0])
        status = data.get('status', '')
        src = data.get('src', '')
        dst = data.get('dst', '')
        if status == 'PROCESSED' and dst:
            lines.append(dst)
        elif status in ('LANGUAGE_SKIPPED', 'RULE_SKIPPED'):
            lines.append(src if src else '')
        else:
            lines.append(src if src else '')

    conn.close()

    output = '\n'.join(lines)
    if not output_file:
        output_file = project_file.with_suffix('.translated.txt')
    else:
        output_file = Path(output_file)

    output_file.write_text(output, encoding='utf-8')
    print(f"导出完成: {output_file}")
    print(f"  行数: {len(lines)}")
    print(f"  字符: {len(output):,}")


def continue_translation(project_file):
    """断点续翻"""
    if not check_lg_installed():
        return
    config_path = BASE_DIR / "linguagacha_config.json"
    prompt_path = TEMPLATES_DIR / "academic_prompt.txt"
    glossary_path = GLOSSARIES_DIR / "south_asia_military.json"

    cmd = [
        str(LG_EXE), "--cli",
        "--project", str(project_file),
        "--config", str(config_path),
        "--continue",
    ]
    if glossary_path.exists():
        cmd.extend(["--glossary", str(glossary_path)])
    if prompt_path.exists():
        cmd.extend(["--custom_prompt_zh", str(prompt_path)])

    print("断点续翻...")
    subprocess.run(cmd)


def retry_failed(project_file):
    """重试失败项"""
    if not check_lg_installed():
        return
    config_path = BASE_DIR / "linguagacha_config.json"
    prompt_path = TEMPLATES_DIR / "academic_prompt.txt"
    glossary_path = GLOSSARIES_DIR / "south_asia_military.json"

    cmd = [
        str(LG_EXE), "--cli",
        "--project", str(project_file),
        "--config", str(config_path),
        "--reset_failed",
    ]
    if glossary_path.exists():
        cmd.extend(["--glossary", str(glossary_path)])
    if prompt_path.exists():
        cmd.extend(["--custom_prompt_zh", str(prompt_path)])

    print("重试失败项...")
    subprocess.run(cmd)


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return

    action = sys.argv[1].lower()

    if action == 'setup':
        api_url = input("API URL (OpenAI兼容端点): ").strip()
        api_key = input("API Key: ").strip()
        model_id = input("Model ID [gemini-3-flash-preview]: ").strip() or "gemini-3-flash-preview"
        concurrency = int(input("并发数 [20]: ").strip() or "20")
        setup_config(api_url, api_key, model_id, concurrency)

    elif action == 'create':
        if len(sys.argv) < 3:
            print("用法: python run_linguagacha.py create <input_file_or_dir>")
            return
        create_project(sys.argv[2],
                        project_name=sys.argv[3] if len(sys.argv) > 3 else None)

    elif action == 'status':
        if len(sys.argv) < 3:
            # 查找最近的 .lg 文件
            lg_files = list(BASE_DIR.glob("*.lg"))
            if lg_files:
                check_status(max(lg_files, key=lambda f: f.stat().st_mtime))
            else:
                print("未找到项目文件。请指定路径。")
        else:
            check_status(sys.argv[2])

    elif action == 'export':
        if len(sys.argv) < 3:
            lg_files = list(BASE_DIR.glob("*.lg"))
            if lg_files:
                export_translation(max(lg_files, key=lambda f: f.stat().st_mtime))
            else:
                print("未找到项目文件。")
        else:
            export_translation(sys.argv[2],
                                sys.argv[3] if len(sys.argv) > 3 else None)

    elif action in ('continue', 'start'):
        if len(sys.argv) < 3:
            lg_files = list(BASE_DIR.glob("*.lg"))
            if lg_files:
                continue_translation(max(lg_files, key=lambda f: f.stat().st_mtime))
            else:
                print("未找到项目文件。")
        else:
            continue_translation(sys.argv[2])

    elif action == 'retry':
        if len(sys.argv) < 3:
            lg_files = list(BASE_DIR.glob("*.lg"))
            if lg_files:
                retry_failed(max(lg_files, key=lambda f: f.stat().st_mtime))
            else:
                print("未找到项目文件。")
        else:
            retry_failed(sys.argv[2])

    else:
        print(f"未知操作: {action}")
        print(__doc__)


if __name__ == '__main__':
    main()
