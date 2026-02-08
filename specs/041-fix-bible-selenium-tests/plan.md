# Plan: Fix Bible Template Selection + Selenium Browser Tests

## Part 1: Fix Bible Template Selection Bug

### Root Cause
1. `home.html:90` — Bible template cards have `data-prompt="{{ tpl.prompt }}"` (full story text)
2. `app.js:44` — `selectTemplate()` sets `prompt.value = card.dataset.prompt` (copies full story text)
3. `home.html:144` — Hidden field `<input type="hidden" name="bible_reference_mode" value="on">` is always on for Bible tier
4. `routes.py:315-326` — When `bible_reference_mode == "on"`, server calls `bible_service.validate_reference(prompt)` which rejects anything not starting with a recognized Bible book name

### Fix
Use `scripture_reference` as the prompt for Bible templates, so the reference mode validation passes and verse-fetching works correctly.

**`templates/home.html`** — Add `data-scripture-reference` attribute to Bible template cards:
```html
<div class="template-card" ... data-scripture-reference="{{ tpl.scripture_reference }}">
```

**`static/js/app.js`** — In `selectTemplate()`, after setting `prompt.value`, check for scripture reference:
```javascript
var scriptureRef = card.dataset.scriptureReference;
if (scriptureRef) {
    var bibleMode = document.querySelector('input[name="bible_reference_mode"]');
    if (bibleMode) {
        prompt.value = scriptureRef;
    }
}
```

Template click sets prompt to "Genesis 3" → `validate_reference()` passes → server fetches actual verses → story is generated from scripture.

On deselect (already handled): prompt is cleared to `''`, user can type their own reference.

### Files Modified
- `templates/home.html:90` — Add `data-scripture-reference` attribute
- `static/js/app.js:44-48` — Add scripture reference override in `selectTemplate()`

## Part 2: Selenium Browser Tests

### Dependencies
Add to `requirements.txt`:
```
selenium>=4.15.0
webdriver-manager>=4.0.0
```

### Test Infrastructure

**`tests/conftest.py`** — Add browser fixtures (alongside existing TestClient fixtures):
- `live_server` fixture: Start uvicorn on a random port via subprocess, wait for ready, yield URL, kill on teardown
- `browser` fixture: Create headless Chrome WebDriver via webdriver-manager, yield driver, quit on teardown
- Mark browser tests with `@pytest.mark.browser` so they can be run separately via `pytest -m browser`

**`pyproject.toml`** — Register the `browser` marker

### Test File: `tests/test_browser.py`

Test cases:
1. **Kids tier — home page loads** — Navigate to `/kids/`, verify page title and template cards visible
2. **Kids tier — template selection** — Click a template card, verify prompt textarea is filled, verify card gets `.selected` class
3. **Kids tier — template deselection** — Click selected card again, verify prompt is cleared
4. **Kids tier — start story** — Select template, submit form, verify redirect to scene page
5. **Bible tier — home page loads** — Navigate to `/bible/`, verify Bible section headers visible
6. **Bible tier — template selection fills reference** — Click a Bible template card, verify prompt input contains scripture reference (not full story text), verify `bible_reference_mode` hidden field is still "on"
7. **Bible tier — manual reference entry** — Type "Genesis 1" in prompt, submit, verify no validation error
8. **Bible tier — invalid reference rejected** — Type "not a bible ref" in prompt, submit, verify error message shown
9. **Bible tier — accordion sections** — Click a collapsed `<details>` section, verify it opens and shows template cards

### Execution Pattern
Browser tests use a live server (not TestClient) because they need real JavaScript execution. The server will mock AI services via environment variables or a test config.

## Verification
1. Run `venv/bin/python -m pytest tests/test_browser.py -m browser -v` — all Selenium tests pass
2. Manual: navigate to `/bible/`, click a template, verify prompt shows scripture reference, submit works
3. Run existing tests: `venv/bin/python -m pytest tests/ -v --ignore=tests/test_browser.py` — no regressions
