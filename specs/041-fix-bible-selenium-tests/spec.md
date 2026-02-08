# Spec: Fix Bible Template Selection + Selenium Browser Tests

## Problem Statement

Bible tier templates are broken: clicking a template card (e.g., "Moses") fills the prompt field with the full story text, but `bible_reference_mode=on` is hardcoded in the form, causing `validate_reference()` to reject the prompt since it's not a book name like "Exodus 1-14".

Additionally, the project has no browser-level tests that exercise JavaScript interactions (template selection, form filling, accordion toggles). Existing tests use FastAPI's TestClient which doesn't execute JS.

## User Stories

### US1: Bible Template Selection Works Correctly
**As a** parent or child browsing Bible stories,
**I want** to click a Bible template card and have the story start correctly,
**So that** I don't get a validation error when selecting a pre-made Bible story.

**Acceptance Criteria:**
- Clicking a Bible template card fills the prompt with the scripture reference (e.g., "Genesis 3"), not the full story text
- Form submission passes `validate_reference()` and starts the story
- Deselecting a template clears the prompt field
- Manual reference entry still works as before

### US2: Selenium Browser Tests
**As a** developer,
**I want** automated browser tests that exercise JavaScript-dependent UI interactions,
**So that** template selection, form groups, and accordion behavior are regression-tested.

**Acceptance Criteria:**
- Tests run via `pytest -m browser` separately from unit tests
- Tests cover kids tier: page load, template select/deselect, story start
- Tests cover Bible tier: page load, template fills reference, manual reference, invalid reference error, accordion sections
- Tests use headless Chrome and a live server (not TestClient)
- Existing tests are unaffected
