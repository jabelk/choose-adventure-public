# Tasks: Fix Bible Template Selection + Selenium Browser Tests

**Input**: Design documents from `/specs/041-fix-bible-selenium-tests/`
**Prerequisites**: plan.md (required), spec.md (required)

---

## Phase 1: Fix Bible Template Selection Bug

- [x] T001 Add `data-scripture-reference="{{ tpl.scripture_reference }}"` attribute to Bible template cards in `templates/home.html:90`
- [x] T002 Add scripture reference override in `selectTemplate()` in `static/js/app.js:44-48` — when card has `data-scripture-reference` and `bible_reference_mode` hidden field exists, set prompt to scripture reference instead of story text

---

## Phase 2: Selenium Test Dependencies

- [x] T003 Add `selenium>=4.15.0` and `webdriver-manager>=4.0.0` to `requirements.txt`
- [x] T004 Install new dependencies: `venv/bin/pip install -r requirements.txt`

---

## Phase 3: Test Infrastructure

- [x] T005 Register `browser` marker in `pyproject.toml` (created new file)
- [x] T006 Add `live_server` fixture to `tests/conftest.py` — start uvicorn on random port via subprocess, wait for ready, yield URL, kill on teardown
- [x] T007 Add `browser` fixture to `tests/conftest.py` — headless Chrome/Brave via Selenium's built-in SeleniumManager (no webdriver-manager needed at runtime)

---

## Phase 4: Browser Tests

- [x] T008 Create `tests/test_browser.py` with kids tier tests: home page loads, template selection, template deselection, start story
- [x] T009 Add Bible tier tests to `tests/test_browser.py`: home page loads, template selection fills reference, manual reference entry, invalid reference rejected, accordion sections

---

## Phase 5: Verification

- [x] T010 Run `venv/bin/python -m pytest tests/test_browser.py -m browser -v` — all 9 tests pass
- [x] T011 Run existing tests `venv/bin/python -m pytest tests/ -v --ignore=tests/test_browser.py` — 410 pass, 3 pre-existing failures (unrelated character roster tests)

---

## Dependencies & Execution Order

- Phase 1 (T001-T002): No dependencies — can start immediately ✅ DONE
- Phase 2 (T003-T004): No dependencies — T003 done, T004 pending
- Phase 3 (T005-T007): Depends on Phase 2
- Phase 4 (T008-T009): Depends on Phase 3
- Phase 5 (T010-T011): Depends on Phase 4
