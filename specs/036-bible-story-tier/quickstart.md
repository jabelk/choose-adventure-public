# Quickstart: Bible Story Tier

## Prerequisites

- Existing choose-adventure app running (all dependencies already installed)
- Optional: API.Bible key from https://scripture.api.bible (free signup)

## New Dependency

```bash
# httpx is already in requirements.txt — no new pip dependencies needed
```

## Environment Setup

Add to `.env`:
```bash
# Bible API key (optional — enables verse text fetching for accuracy)
BIBLE_API_KEY=your-api-bible-key-here
```

## Files to Create

1. `app/services/bible.py` — BibleService for verse fetching
2. `app/bible_templates.py` — 75+ Bible story templates (separate file to keep tiers.py manageable)

## Files to Modify

1. `app/tiers.py` — Add `scripture_reference` and `section` fields to StoryTemplate, add `"bible"` TierConfig to TIERS dict
2. `app/story_options.py` — Add `bible` field to OptionGroup, update `choices_for_tier()`
3. `app/routes.py` — Add `_SURPRISE_FALLBACK_BIBLE` list, inject scripture reference into AI prompt, handle guided reference field
4. `templates/home.html` — Collapsible sections for Bible tier, guided reference field
5. `templates/landing.html` — Add Bible tier card description
6. `static/css/style.css` — Add `.theme-bible` and `.tier-card-bible` styles
7. `.env.example` — Add BIBLE_API_KEY entry

## Verification

```bash
# Start the server
venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8080

# Check Bible tier loads
curl http://localhost:8080/bible/

# Check landing page shows Bible tier
curl http://localhost:8080/

# Count templates
venv/bin/python -c "from app.tiers import TIERS; print(len(TIERS['bible'].templates))"
```
