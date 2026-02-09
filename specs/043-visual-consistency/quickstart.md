# Quickstart: Character Visual Consistency

**Feature**: 043-visual-consistency
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
venv/bin/python -m pytest tests/ -v --ignore=tests/test_browser.py

# Run visual consistency tests only
venv/bin/python -m pytest tests/test_visual_consistency.py -v
```

## Key Files to Modify

1. **`app/models.py`** — Add `generated_reference_path: str = ""` field to `Story` model
2. **`app/routes.py`** — Add `_build_reference_images()` helper, update all `generate_image()` call sites to use it, add `_update_reference_after_generation()` wrapper, add reset-appearance route, pass reference indicator to template context
3. **`templates/story.html`** — Add reference indicator badge and reset-appearance button
4. **`static/css/style.css`** — Minimal styling for reference indicator badge
5. **`tests/test_visual_consistency.py`** — New test file

## Verification

After implementation, verify:

1. Start a story with a roster character who has a photo → complete 3 scenes → verify character appearance stays consistent
2. Start a story WITHOUT a roster character photo → verify scene 2+ images visually match scene 1
3. Check that the reference indicator badge appears on the story page when references are active
4. Tap "Reset appearance" mid-story → verify next scene generates without prior scene reference
5. Verify image generation still works when no roster characters are selected (reference chain bootstraps from scene 1)
6. Run full test suite — all tests pass, no regressions
