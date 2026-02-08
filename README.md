# Choose Your Own Adventure

Interactive choose-your-own-adventure web app powered by AI. Generate stories with images, make choices, and explore branching narratives.

## Features

- **AI-Powered Stories**: Claude and GPT generate unique stories based on your prompts
- **Story Templates**: Pre-built story starters for quick adventures
- **Image Generation**: AI-generated illustrations for every scene
- **Branching Narratives**: Make choices that shape the story
- **Multiple Tiers**: Kids Adventures (ages 3-6) and Bible Stories (ages 3-8)
- **Character System**: Create and reuse characters across stories
- **Family Mode**: Add family members to appear in stories
- **Read Aloud**: Text-to-speech narration with multiple voices
- **Gallery**: Save and revisit completed stories
- **Story Export**: Export stories as HTML or PDF
- **Coloring Pages**: Generate printable coloring pages from story scenes
- **Sequel Mode**: Continue completed stories with new chapters
- **Surprise Me**: One-tap random story generation
- **Mobile PWA**: Install as a mobile app with offline support

## Tech Stack

- Python 3.11+ with FastAPI
- Jinja2 templates
- Claude API (Anthropic) for story generation
- OpenAI API for image generation (gpt-image-1)
- Google Gemini API (optional, for additional model support)

## Setup

1. Clone the repository
2. Create a virtual environment and install dependencies:

```bash
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

3. Copy `.env.example` to `.env` and add your API keys:

```
ANTHROPIC_API_KEY=your-key-here
OPENAI_API_KEY=your-key-here
```

4. Run the server:

```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8080
```

5. Open http://localhost:8080 in your browser

## Tiers

- **Kids Adventures** (`/kids/`): Age-appropriate stories for children ages 3-6
- **Bible Stories** (`/bible/`): Interactive Bible stories for children ages 3-8

## License

MIT
