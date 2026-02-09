# Quickstart: Enhanced Character Creation & Relationship Depth

**Feature**: 042-character-depth
**Date**: 2026-02-08

## Prerequisites

- Python 3.11+ with virtual environment at `venv/`
- Existing project dependencies installed (`venv/bin/pip install -r requirements.txt`)
- No new pip dependencies required

## Development

```bash
# Start the dev server
venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8080

# Run tests
venv/bin/python -m pytest tests/test_character_roster.py -v

# Run all tests
venv/bin/python -m pytest tests/ -v --ignore=tests/test_browser.py
```

## Key Files to Modify

1. **`app/models.py`** — Add `attributes`, `relationship_stage`, `story_count`, `last_story_date` to `RosterCharacter`
2. **`app/story_options.py`** — Add `CHARACTER_ATTRIBUTES` dict, `RELATIONSHIP_STAGES`, `RELATIONSHIP_PROMPTS`, 7 new `KINK_TOGGLES`
3. **`app/services/character.py`** — Add `advance_relationship()` method, attribute validation, `compose_description()`
4. **`app/routes.py`** — Accept `attr_*` form fields on create/update, call `advance_relationship()` after `save_story()`, inject relationship context
5. **`templates/characters.html`** — Add pill selector sections grouped by physical/personality/style, relationship display
6. **`templates/home.html`** — Add inline pill selectors in character section of story start form
7. **`static/js/character-attributes.js`** — New file: pill selector initialization, description composition preview
8. **`static/css/style.css`** — Pill selector styles (extend `.kink-pill` pattern)
9. **`static/js/character-picker.js`** — Add relationship stage badge to picker cards
10. **`tests/test_character_roster.py`** — Add tests for structured attributes, relationship tracking

## Verification

After implementation, verify:

1. Navigate to `/nsfw/characters` → Create character with pill selectors → verify composed description saved
2. Edit character → verify pills pre-selected from saved attributes
3. Start story with character → verify attributes appear in AI narration
4. Complete a story → verify relationship stage advances on character page
5. Start another story with same character → verify relationship context in AI prompt
6. Check `/kids/characters` → verify NSFW-only attributes (body type, bust size, archetype) are hidden
7. Check `/nsfw/` story start form → verify 11+ kink toggles appear
8. On mobile → verify all pill selectors have 44px+ tap targets, no horizontal scroll
