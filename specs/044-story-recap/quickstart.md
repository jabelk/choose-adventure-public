# Quickstart: Story Recap / "Previously On..."

**Feature**: 044-story-recap
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

# Run recap tests only
venv/bin/python -m pytest tests/test_recap.py -v
```

## Key Files to Modify

1. **`app/models.py`** — Add `recap_cache: dict[str, str] = Field(default_factory=dict)` to `StorySession`
2. **`app/routes.py`** — Add `GET /{tier}/story/recap/{scene_id}` endpoint, add `?resumed=1` to resume redirect, pass recap context to template
3. **`app/services/story.py`** — Add `generate_recap()` method using existing `_call_provider()`
4. **`templates/scene.html`** — Add collapsible "Story so far" section with async loading
5. **`static/js/app.js`** — Add recap fetch + toggle logic
6. **`static/css/style.css`** — Styling for recap section
7. **`tests/test_recap.py`** — New test file

## Verification

After implementation, verify:

1. Start a story, progress 3+ scenes → verify "Story so far" toggle appears collapsed on scene pages
2. Leave the app, resume from gallery/home → verify recap section appears expanded with AI summary
3. Click the toggle to expand/collapse → verify smooth toggle behavior
4. Navigate to next scene → verify recap is collapsed again (active play)
5. Go back and take a different branch → verify recap updates for the new path
6. Disconnect AI (remove API key) → verify page loads normally, recap shows graceful fallback
7. Run full test suite — all tests pass, no regressions
