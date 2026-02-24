# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This repository contains two main systems:

1. **nanyanews-main**: An AI/Tech news aggregation and monitoring system (formerly "South Asia News Bot")
2. **Claude Code Skills**: Custom skills for Claude Code, including the xixi-tech-writer skill for tech article writing

## Project Structure

```
skills存放处/
├── nanyanews-main/              # News aggregation system
│   ├── main.py                  # Main entry point
│   ├── config.py                # Configuration (80+ RSS sources)
│   ├── crawler/                 # News crawler module
│   ├── models/                  # Database models
│   ├── utils/                   # Text processing utilities
│   ├── pusher/                  # Push notification module (Feishu)
│   ├── scheduler/               # Task scheduler
│   ├── web/                     # Flask web dashboard
│   └── news.db                  # SQLite database
│
├── .claude/skills/              # Claude Code skills
│   ├── xixi-tech-writer/        # Tech writing skill
│   │   ├── skill.md             # Skill definition
│   │   ├── scripts/             # Writing pipeline scripts
│   │   │   ├── news_controller.py    # Control nanyanews system
│   │   │   ├── topic_agents.py       # Multi-agent topic selection
│   │   │   ├── writing_agents.py     # Multi-agent writing
│   │   │   ├── title_generator.py    # Title generation
│   │   │   ├── quality_checker.py    # Quality review
│   │   │   └── config_agents.py      # Unified configuration
│   │   └── references/          # Style guides and examples
│   └── skill-creator/           # Skill creation guide
│
└── output/                      # All generated content
    └── YYYYMMDD/                # Date-based folders
        ├── topics/              # Topic analysis reports
        ├── articles/            # Generated articles
        ├── titles/              # Title proposals
        └── reviews/             # Quality reviews
```

## Common Commands

### nanyanews System

The news aggregation system is located at `nanyanews-main/`. All commands should be run from the **xixi-tech-writer scripts directory**:

```bash
cd ".claude\skills\xixi-tech-writer\scripts"

# Check system status
python news_controller.py status

# Crawl news from 80+ RSS sources (2-5 minutes)
python news_controller.py crawl

# Get topic analysis (recommended)
python news_controller.py analyze --save

# Quick topic list
python news_controller.py topics --save

# Start/stop background service
python news_controller.py start
python news_controller.py stop
```

**Running nanyanews directly** (less common):

```bash
cd nanyanews-main

# Run one-time crawl
python main.py --mode crawl

# Start web dashboard (http://localhost:5000)
python main.py --mode web --port 5000

# Start scheduler (background tasks)
python main.py --mode scheduler

# Full system (scheduler + web)
python main.py
```

### Multi-Agent Writing Pipeline

All scripts are in `.claude\skills\xixi-tech-writer\scripts\`:

```bash
# 1. Topic Selection (4 agents in parallel)
python topic_agents.py --save

# 2. Article Writing (3-stage pipeline: draft → style → polish)
python writing_agents.py --topic "选题标题" --source-file material.txt

# 3. Title Generation (4 styles in parallel, 20 titles)
python title_generator.py --article-file ../../output/20260106/articles/article_xxx.md --save

# 4. Quality Review (3-dimension check + auto-fix)
python quality_checker.py --article-file ../../output/20260106/articles/article_xxx.md --auto-fix --save
```

**Output locations**: All files save to `output/YYYYMMDD/` with date-based organization.

## Key Architecture Concepts

### nanyanews System Architecture

**Data Flow**:
1. **Crawler** (`crawler/news_crawler.py`) → Fetches from 80+ RSS feeds
2. **Text Processor** (`utils/text_processor.py`) → Filters AI/tech relevance, scores importance
3. **Database** (`models/news.py`) → Stores in SQLite with metadata
4. **Scheduler** (`scheduler/task_scheduler.py`) → Automated hourly crawls
5. **Web Dashboard** (`web/app.py`) → Flask interface for monitoring

**Important Scoring System**:
- `importance_score`: Weighted algorithm (relevance 30%, title importance 35%, timeliness 25%, quality 10%)
- `timeline_at`: Reliable timestamp field (prioritizes RSS `published_date`)
- `published_confidence`: Confidence level (≥0.5 means reliable time)

**Database Schema** (`news_items` table):
- Core fields: `url`, `title`, `content`, `source`
- Timing: `published_date`, `crawled_date`, `timeline_at`, `published_confidence`
- Analysis: `importance_score`, `category`, `keywords`, `matched_keywords`
- Status: `is_pushed`, `is_deleted`

### Multi-Agent Writing System

Uses **Anthropic SDK** to create collaborative agent systems:

**Topic Selection (topic_agents.py)**:
- 4 specialized agents analyze news in parallel:
  - Hotspot Tracker: Major releases, industry events
  - Tech Depth: Papers, open-source, breakthroughs
  - Business Insight: Funding, markets, business models
  - Practical Tools: Tool reviews, tutorials
- Coordinator agent synthesizes results
- Output: Ranked topics with writing angles

**Writing Pipeline (writing_agents.py)**:
- 3-stage sequential workflow:
  1. Draft Agent: Initial content structure
  2. Style Agent: Apply "硬核内容+可爱表达" voice
  3. Polish Agent: Final refinement
- Each agent builds on previous work

**Configuration**:
- All API keys and settings in `scripts/config_agents.py`
- Default model: Claude Sonnet 4.5
- Database path: `NANYANEWS_PATH / "news.db"`

### File Handling

**Key Paths** (defined in `news_controller.py`):
```python
SKILLS_BASE_DIR = Path(r"C:\Users\bisu5\Desktop\夕小瑶科技\skills存放处")
NANYANEWS_PATH = SKILLS_BASE_DIR / "nanyanews-main"
DATABASE_PATH = NANYANEWS_PATH / "news.db"
OUTPUT_DIR = SKILLS_BASE_DIR / "output"
```

**Database Location** (IMPORTANT):
- Correct path: `C:\Users\bisu5\Desktop\夕小瑶科技\skills存放处\nanyanews-main\news.db`
- System uses single unified database
- Old copy folders cleaned up to avoid confusion

**Output Organization**:
- All generated content goes to `output/YYYYMMDD/`
- Categories: `topics/`, `articles/`, `titles/`, `reviews/`
- Files include both `.md` (readable) and `.json` (structured data)

## Development Notes

### Working with nanyanews

**Adding News Sources**:
- Edit `config.py` → `NEWS_SOURCES['rss_feeds']` list
- Or edit `news_sources.json` (preferred, loaded automatically)

**Modifying Scoring Algorithm**:
- See `utils/text_processor.py` → `calculate_importance_score()`
- Keyword weights defined in `config.py` → `AI_TECH_KEYWORDS`

**Categories**:
- 12 main categories: llm, multimodal, agent, research, product, startup, hardware, safety, opensource, enterprise, coding, infrastructure
- Keywords defined in `config.py` → `CATEGORIES`

### Working with Multi-Agent System

**API Configuration**:
- Set `ANTHROPIC_API_KEY` in environment or `config_agents.py`
- Default model: `claude-sonnet-4-5-20250929` (1M context)

**Modifying Agent Behavior**:
- Topic selection prompts: `topic_agents.py` → Each agent class
- Writing style: `writing_agents.py` → System prompts reference `skill.md`
- Coordinator logic: Final synthesis step in each script

**Adding New Agent Types**:
1. Create new agent class inheriting from base pattern
2. Define system prompt with specific expertise
3. Add to parallel execution in main function

### Testing

**Check Database**:
```bash
# View news count
python -c "import sqlite3; conn = sqlite3.connect(r'C:\Users\bisu5\Desktop\夕小瑶科技\skills存放处\nanyanews-main\news.db'); print(f'Total: {conn.execute(\"SELECT COUNT(*) FROM news_items\").fetchone()[0]}'); conn.close()"

# Check recent news
cd nanyanews-main
python -c "from models.news import DatabaseManager; db = DatabaseManager('sqlite:///news.db'); print(f'Last 24h: {len(db.get_recent_news(24))}')"
```

**Test Crawler**:
```bash
cd nanyanews-main
python main.py --mode crawl
```

## Important Constraints

1. **No Direct Database Writes**: Always use `DatabaseManager` methods from `models/news.py`
2. **Encoding**: All files use UTF-8, Python files have `# -*- coding: utf-8 -*-`
3. **Windows Paths**: Use raw strings `r"C:\..."` or `Path()` objects
4. **RSS Feed Reliability**: Not all feeds provide `published_date`, filter by `published_confidence >= 0.5`
5. **API Rate Limits**: Multi-agent systems make parallel calls, monitor Anthropic usage
6. **Output Paths**: Always use `OUTPUT_DIR` constant, never hardcode paths

## Writing Style Guidelines

The xixi-tech-writer skill follows specific style rules (see `.claude/skills/xixi-tech-writer/skill.md`):

- **Tone**: Professional yet friendly ("炼丹" instead of "模型训练")
- **Structure**: Title (≤25 chars) → 2-paragraph intro → 2-5 H2 sections → Conclusion
- **Data**: Always quantify with exact numbers, units, and timestamps
- **Persona**: Conversational friend, use "？？？" for shock, "——" for explanation
- **Prohibitions**: No pure academic tone, no vague claims ("very fast" → "17 minutes"), no excessive hype

## Skills System

This repository uses Claude Code's skills feature:

- **xixi-tech-writer**: Tech article writing with news integration
- **skill-creator**: Guide for creating new skills

Skills are invoked in Claude Code conversations with `/skill-name` or through the Skill tool.
