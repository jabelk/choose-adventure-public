# Quickstart: Core Story Engine

**Feature Branch**: `001-core-story-engine`
**Date**: 2026-02-07

## Prerequisites

- Python 3.11+
- Anthropic API key (for Claude text generation)
- OpenAI API key (for gpt-image-1 image generation)

## Setup

```bash
# Clone and enter project
cd choose-adventure

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Configure API keys
cp .env.example .env
# Edit .env and add your API keys:
#   ANTHROPIC_API_KEY=sk-ant-...
#   OPENAI_API_KEY=sk-...
```

## Run

```bash
# Start the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Open http://localhost:8000 in your browser.

## Usage

1. Enter a story prompt (e.g., "A knight discovers a hidden cave in the mountains")
2. Select story length: Short, Medium, or Long
3. Click "Start Adventure"
4. Read the scene, view the AI-generated image
5. Click one of the 2-4 choices to advance the story
6. Use "Go Back" to explore different branches
7. Reach an ending and start a new story

## Configuration

Environment variables (set in `.env`):

| Variable           | Required | Description                    |
|--------------------|----------|--------------------------------|
| ANTHROPIC_API_KEY  | yes      | Anthropic API key for Claude   |
| OPENAI_API_KEY     | yes      | OpenAI API key for gpt-image-1 |

## Deployment to NUC (later)

```bash
# On warp-nuc, same setup as above, then:
uvicorn app.main:app --host 0.0.0.0 --port 8000

# Access from any device on LAN:
# http://warp-nuc:8000 or http://<nuc-ip>:8000
```
