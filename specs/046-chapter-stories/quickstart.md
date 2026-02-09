# Quickstart: Chapter Stories

**Feature**: 046-chapter-stories
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

1. **`app/models.py`** — Add `EPIC` to `StoryLength` enum, add `chapter_number` and `chapter_title` fields to `Scene` and `SavedScene`
2. **`app/services/story.py`** — Add chapter-aware pacing to `SYSTEM_PROMPT`, include `chapter_title` in JSON output format, detect chapter boundaries in `generate_scene()`
3. **`app/services/gallery.py`** — Add `save_chapter_progress()` / `load_chapter_progress()` / `delete_chapter_progress()` methods (or parameterize existing methods with suffix)
4. **`app/routes.py`** — Pass chapter metadata when generating scenes, chapter resume/abandon endpoints, chapter progress save on each scene
5. **`templates/home.html`** — Add "Epic" radio button, chapter story resume banner
6. **`templates/scene.html`** — Chapter title card rendering above scene content
7. **`templates/gallery.html`** — Chapter count on story cards for epic stories
8. **`templates/reader.html`** — Chapter title cards in reader, chapter jump navigation
9. **`static/css/style.css`** — Chapter title card styling

## Verification

After implementation, verify:

1. Select "Epic" length on home page → verify new option appears with "~5 chapters" description
2. Start an epic story → verify Chapter 1 title card appears on the first scene
3. Play through 5 scenes → verify Chapter 2 title card appears at scene 6
4. Close browser mid-chapter → reopen home page → verify "Continue Chapter N" banner appears
5. Click continue → verify story resumes at exact scene
6. Start a regular (short) story while epic is in progress → verify both resume banners show
7. Abandon chapter story → verify banner disappears
8. Complete a full epic story → verify gallery shows "5 Chapters" on card
9. Open completed epic in reader → verify chapter title cards display between chapters
10. Verify existing short/medium/long stories work unchanged — no regressions
11. Run full test suite — all tests pass
