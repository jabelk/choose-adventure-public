# Tasks: Story Export

**Input**: Design documents from `/specs/009-story-export/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: No tests requested in the feature specification. Manual testing via quickstart.md.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Install fpdf2 dependency and create the export service module

- [X] T001 Install fpdf2 dependency via `venv/bin/pip install fpdf2` and verify import
- [X] T002 Create app/services/export.py with helper functions: `_read_image_as_base64(image_url)` to resolve image paths from `static/images/` and return base64 data URIs, and `_get_placeholder_svg()` to return a small inline SVG placeholder for missing images

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared export logic that BOTH user stories depend on — scene ordering and image resolution

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T003 Add `_order_scenes_by_branch(saved_story)` function to app/services/export.py — returns a list of (scene, branch_label) tuples ordered as: main path first (using path_history), then alternate branches depth-first, each labeled with the choice point they diverge from (e.g., "Branch from Ch. 2: 'Enter the cave'")
- [X] T004 Add `_build_scene_data(saved_story)` function to app/services/export.py — for each scene, reads image from disk, encodes as base64 data URI (or placeholder if missing), returns list of dicts with scene info + base64 image + branch label

**Checkpoint**: Foundation ready — scene ordering and image embedding available for both export formats

---

## Phase 3: User Story 1 — Export as Self-Contained HTML (Priority: P1) 🎯 MVP

**Goal**: Users can download a completed story as a single HTML file with embedded images and interactive tree navigation that works offline.

**Independent Test**: Export a branched story as HTML, open the file in a browser with no server, verify all text/images/navigation work. (Quickstart steps 2-4)

### Implementation for User Story 1

- [X] T005 [US1] Create templates/export.html — self-contained HTML template with: inline CSS (story styling), story metadata header (title, prompt, date), one `<div>` per scene (hidden by default, shown via JS), inline tree navigation panel (simple HTML list with click handlers), inline `<script>` for show/hide navigation — no external dependencies
- [X] T006 [US1] Add `export_html(saved_story)` function to app/services/export.py — builds scene data with base64 images, builds tree structure, renders templates/export.html via Jinja2 env, returns the complete HTML string
- [X] T007 [US1] Add `GET /{tier}/gallery/{story_id}/export/html` route to app/routes.py — loads saved story, calls export_html(), returns Response with content_type="text/html" and Content-Disposition attachment header with filename "{title}.html"
- [X] T008 [US1] Add "Export HTML" button to templates/gallery.html on each story card — link to `/{tier}/gallery/{story_id}/export/html`
- [X] T009 [US1] Add "Export HTML" button to templates/reader.html in the reader nav area — link to `/{tier}/gallery/{story_id}/export/html`
- [X] T010 [P] [US1] Add export button CSS styles to static/css/style.css — `.btn-export` styling for gallery card and reader export buttons, fits with existing theme

**Checkpoint**: HTML export fully functional — users can download and read stories offline with branch navigation

---

## Phase 4: User Story 2 — Export as PDF (Priority: P2)

**Goal**: Users can download a completed story as a PDF document with images, branch-organized layout, and tree overview.

**Independent Test**: Export a branched story as PDF, open in a PDF reader, verify all scenes present with images and branch labels. (Quickstart steps 5-6)

### Implementation for User Story 2

- [X] T011 [US2] Add `export_pdf(saved_story)` function to app/services/export.py — uses fpdf2 to build PDF: title page with metadata, text-based branch overview, then scenes in branch order (main path first) with embedded images, page breaks between scenes, placeholder for missing images
- [X] T012 [US2] Add `GET /{tier}/gallery/{story_id}/export/pdf` route to app/routes.py — loads saved story, calls export_pdf(), returns Response with content_type="application/pdf" and Content-Disposition attachment header with filename "{title}.pdf"
- [X] T013 [US2] Add "Export PDF" button to templates/gallery.html on each story card — link to `/{tier}/gallery/{story_id}/export/pdf`, next to the HTML export button
- [X] T014 [US2] Add "Export PDF" button to templates/reader.html in the reader nav area — link to `/{tier}/gallery/{story_id}/export/pdf`, next to the HTML export button

**Checkpoint**: PDF export fully functional — users can download printable story documents

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Edge cases, backward compatibility, and end-to-end validation

- [X] T015 Verify export works with linear stories (pre-branching, no branches) — test HTML and PDF export show single-path story with no errors (FR-010)
- [X] T016 Verify export handles missing images gracefully — delete an image file, export as HTML and PDF, confirm placeholder appears instead of broken reference (FR-008)
- [X] T017 Run full quickstart.md validation (all 8 steps) to confirm end-to-end functionality

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion — BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational phase (T003, T004)
- **User Story 2 (Phase 4)**: Depends on Foundational phase (T003, T004) and Setup (T001 for fpdf2)
- **Polish (Phase 5)**: Depends on both user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) — no dependencies on US2
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) — no dependencies on US1, but shares export buttons in templates

### Within Each User Story

- Service functions before routes (routes call service)
- Routes before template changes (templates link to routes)
- CSS can be done in parallel with service/route work

### Parallel Opportunities

- T005 (template) and T006 (service) can be developed concurrently, though T006 renders T005
- T008 and T009 can run in parallel (different template files)
- T010 can run in parallel with T006/T007 (different file: style.css)
- T013 and T014 can run in parallel (different template files)

---

## Parallel Example: User Story 1

```bash
# Service + template can be designed in parallel:
Task: "Create export.html template in templates/export.html"        # T005
Task: "Add export button CSS to static/css/style.css"               # T010

# Then sequential (service renders template, route calls service):
Task: "Add export_html() to app/services/export.py"                 # T006
Task: "Add HTML export route to app/routes.py"                      # T007

# Then template buttons (depend on route existing):
Task: "Add Export HTML button to templates/gallery.html"            # T008
Task: "Add Export HTML button to templates/reader.html"             # T009
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (install fpdf2, create export service)
2. Complete Phase 2: Foundational (scene ordering, image embedding)
3. Complete Phase 3: User Story 1 (HTML export)
4. **STOP and VALIDATE**: Test HTML export end-to-end
5. Story export is functional — HTML covers the interactive use case

### Incremental Delivery

1. Setup + Foundational → Image embedding and scene ordering ready
2. Add User Story 1 → HTML export → Self-contained offline reading
3. Add User Story 2 → PDF export → Printable archival documents
4. Each format adds value without breaking the other

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- fpdf2 is the only new pip dependency — pure Python, no system-level requirements
- Images are read from `static/images/{scene_id}.png` and base64-encoded at export time
- HTML export uses a Jinja2 template with inline everything (CSS, JS, images) — no external deps
- PDF uses fpdf2's built-in text wrapping and image embedding
- Commit after each phase completion
- Stop at any checkpoint to validate independently
