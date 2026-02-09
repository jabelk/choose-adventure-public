# Quickstart: Cover Art Generator

**Feature**: 045-cover-art-generator
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
```

## Key Files to Modify

1. **`app/models.py`** — Add `cover_art_url` and `cover_art_status` fields to `SavedStory`
2. **`app/services/gallery.py`** — Add `generate_cover_art()` async method, update `save_story()` to set initial status
3. **`app/routes.py`** — Add `asyncio.create_task()` after each `gallery_service.save_story()` call, add regenerate-cover endpoint
4. **`templates/gallery.html`** — Show cover art as thumbnail with CSS title/author overlay
5. **`templates/reader.html`** — Add "Regenerate Cover" button
6. **`static/css/style.css`** — Cover art card styling

## Verification

After implementation, verify:

1. Complete a story in kids tier → verify gallery shows a cover art thumbnail (not first scene image)
2. Complete a story in bible tier → verify cover has reverent styling
3. Complete a story in NSFW tier → verify cover has mature aesthetic
4. Complete a story with a selected art style → verify cover matches that style
5. Kill the API key mid-generation → verify gallery still shows first scene image as fallback
6. Click "Regenerate Cover" on a gallery story → verify new cover is generated
7. Load an existing gallery story saved before this feature → verify it shows first scene image (no crash)
8. Run full test suite — all tests pass, no regressions
