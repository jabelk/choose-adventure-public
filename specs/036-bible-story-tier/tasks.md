# Tasks: Bible Story Tier

**Input**: Design documents from `/specs/036-bible-story-tier/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/routes.md, quickstart.md

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Extend existing dataclasses and add configuration needed by all Bible tier work

- [x] T001 Add `scripture_reference: str = ""` and `section: str = ""` fields to the StoryTemplate dataclass in `app/tiers.py`
- [x] T002 Add `BIBLE_API_KEY` setting to `app/config.py` (loaded from env, default empty string)
- [x] T003 [P] Add `bible` field (list of OptionChoice) to OptionGroup dataclass and update `choices_for_tier()` to return `self.bible` when `tier == "bible"` in `app/story_options.py`
- [x] T004 [P] Define Bible-specific writing style options in the `writing_style` OptionGroup in `app/story_options.py`: "Storyteller Narrator", "You Are The Hero", "Extra Simple Words"

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core services and content guidelines that MUST be complete before any user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T005 Create `app/services/bible.py` with BibleService class: `fetch_verses(scripture_reference: str) -> str` method that calls the YouVersion Platform API (NIrV translation ID 110) using BIBLE_API_KEY from config, returns verse text or empty string on failure
- [x] T006 Add `validate_reference(user_input: str) -> bool` method to BibleService in `app/services/bible.py` that checks if input matches a known Bible book name with optional chapter:verse pattern
- [x] T007 Add `parse_reference(user_input: str) -> str` method to BibleService in `app/services/bible.py` that converts user input (e.g., "Genesis 6:1-22") to YouVersion API passage ID format
- [x] T008 Define `BIBLE_CONTENT_GUIDELINES` constant in `app/tiers.py` — content guidelines instructing the AI to: follow actual biblical narrative, quote from NIrV translation, include book/chapter references in every scene, generate choices that explore perspective/emotion rather than altering events, handle sensitive content (violence, judgment, sacrifice) with age-appropriate sensitivity for ages 3-8
- [x] T009 [P] Add `_SURPRISE_FALLBACK_BIBLE` list to `app/routes.py` with 6-8 popular Bible story prompts for the surprise/random button

**Checkpoint**: Foundation ready — BibleService, content guidelines, and story options are in place

---

## Phase 3: User Story 1 — Browse and Start a Bible Story (Priority: P1) 🎯 MVP

**Goal**: A parent or child can navigate to /bible/, see an organized library of Bible stories, pick one, and start an interactive adventure faithful to scripture

**Independent Test**: Navigate to /bible/, browse the organized library, select any template, verify the story starts with a biblically faithful scene and appropriate illustration style

### Implementation for User Story 1

- [x] T010 [US1] Add the `"bible"` TierConfig entry to the `TIERS` dict in `app/tiers.py` with: name="bible", prefix="bible", display_name="Bible Stories", is_public=True, theme_class="theme-bible", content_guidelines=BIBLE_CONTENT_GUIDELINES, image_style="warm reverent children's Bible illustration...", default_model="claude", default_image_model="gpt-image-1", tts_default_voice="fable", tts_autoplay_default=True, tts_voices and tts_instructions for Bible narration. Templates initially set to an empty list (populated in US3).
- [x] T011 [US1] Create `app/bible_templates.py` with an initial set of 10-15 Bible story StoryTemplate entries (mix of OT and NT) using scripture_reference and section fields — enough to verify browsing and starting works. Include stories like Creation, Noah, David and Goliath, Jonah, Birth of Jesus, Good Samaritan.
- [x] T012 [US1] Import templates from `app/bible_templates.py` into the `"bible"` TierConfig in `app/tiers.py` by setting `templates=BIBLE_TEMPLATES`
- [x] T013 [US1] Add `{% elif t.name == 'bible' %}` block to `templates/landing.html` with Bible Stories description and appropriate emoji/imagery for the tier card
- [x] T014 [US1] Add collapsible section rendering to `templates/home.html` — when `tier.name == "bible"`, group templates by their `section` field into collapsible accordion sections (Old Testament / New Testament headers with book sub-groups). Use CSS + vanilla JS for expand/collapse.
- [x] T015 [US1] Add collapsible accordion CSS styles to `static/css/style.css` — styles for `.bible-section`, `.bible-section-header`, `.bible-section-content`, expand/collapse toggle icon, smooth transition animation
- [x] T016 [US1] Add guided reference field to `templates/home.html` — for the Bible tier, show a "Request a Bible Story" input field where users type a book/passage reference (e.g., "Ruth 1-4", "Psalm 23") instead of a free-text prompt
- [x] T017 [US1] Handle guided reference in story start route in `app/routes.py` — when Bible tier receives a guided reference: validate via BibleService.validate_reference(), fetch verse text via BibleService.fetch_verses(), build a scripturally constrained story prompt, inject scripture_reference into content_guidelines
- [x] T018 [US1] Add validation error handling for invalid Bible references in `app/routes.py` — if validate_reference() returns False, return a friendly error message suggesting the user try a known book name or browse the template library

**Checkpoint**: Bible tier is accessible at /bible/, appears on landing page, templates display in collapsible sections, guided reference field works, stories start with biblically faithful content

---

## Phase 4: User Story 2 — Biblically Accurate Interactive Choices (Priority: P1)

**Goal**: During Bible stories, choices explore feelings and perspectives while the narrative always follows the actual biblical account. Scenes include NIrV scripture quotes and book/chapter references.

**Independent Test**: Play through a well-known Bible story (e.g., David and Goliath), verify choices explore perspective rather than altering events, verify NIrV quotes appear, verify source passage is referenced

### Implementation for User Story 2

- [x] T019 [US2] Inject scripture_reference from the selected template into the AI system prompt in `app/routes.py` — when starting a Bible tier story, prepend the scripture reference to content_guidelines so the AI targets the correct passage
- [x] T020 [US2] Integrate BibleService.fetch_verses() into story start flow in `app/routes.py` — fetch NIrV verse text for the template's scripture_reference and append it to the system prompt as reference material for the AI
- [x] T021 [US2] Verify and refine BIBLE_CONTENT_GUIDELINES in `app/tiers.py` — ensure guidelines explicitly instruct: (1) weave NIrV quotes naturally into narration, (2) include "from [Book Chapter]" references, (3) choices ask "What would you do?", "How do you think [character] felt?", not "What should happen next?", (4) always steer back to scriptural narrative regardless of choice
- [x] T022 [US2] Add scripture display to story scenes — ensure template rendering in `templates/home.html` shows the scripture_reference on each template card (e.g., "Genesis 6-9" badge) so users know the source passage

**Checkpoint**: Bible stories include NIrV quotes, reference source passages, and choices explore perspective without altering biblical events

---

## Phase 5: User Story 3 — Extensive Library Spanning the Full Bible (Priority: P2)

**Goal**: The library contains 75+ story templates covering major narratives from Genesis through Revelation, organized by testament and book

**Independent Test**: Count templates and verify coverage across both testaments with representation from at least 15 OT books and 8 NT books

### Implementation for User Story 3

- [x] T023 [P] [US3] Add Old Testament — Genesis templates (6-8 stories) to `app/bible_templates.py`: Creation, Adam and Eve, Cain and Abel, Noah's Ark, Tower of Babel, Abraham's Call, Isaac and Rebekah, Jacob and Esau
- [x] T024 [P] [US3] Add Old Testament — Exodus through Deuteronomy templates (6-8 stories) to `app/bible_templates.py`: Baby Moses, Burning Bush, Ten Plagues, Parting the Red Sea, Ten Commandments, Manna from Heaven, Balaam's Donkey, Joshua and Jericho
- [x] T025 [P] [US3] Add Old Testament — Judges through Ruth templates (4-5 stories) to `app/bible_templates.py`: Deborah, Gideon, Samson, Ruth and Naomi
- [x] T026 [P] [US3] Add Old Testament — 1 Samuel through 2 Kings templates (6-8 stories) to `app/bible_templates.py`: Hannah's Prayer, Samuel Hears God, David and Goliath, David and Jonathan, Solomon's Wisdom, Elijah on Mount Carmel, Elisha and Naaman, Josiah Finds the Scroll
- [x] T027 [P] [US3] Add Old Testament — Ezra through Esther templates (3-4 stories) to `app/bible_templates.py`: Rebuilding the Temple, Nehemiah's Wall, Esther Saves Her People
- [x] T028 [P] [US3] Add Old Testament — Job through Psalms templates (2-3 stories) to `app/bible_templates.py`: Job's Faith, Psalm 23 (The Good Shepherd), Psalm 139 (Fearfully and Wonderfully Made)
- [x] T029 [P] [US3] Add Old Testament — Prophets templates (5-6 stories) to `app/bible_templates.py`: Isaiah's Vision, Jeremiah's Call, Ezekiel's Dry Bones, Daniel in the Lions' Den, Daniel's Friends and the Fiery Furnace, Jonah and the Big Fish
- [x] T030 [P] [US3] Add New Testament — Birth and Early Life of Jesus templates (4-5 stories) to `app/bible_templates.py`: Angel Visits Mary, Birth of Jesus, Shepherds and Angels, Wise Men, Boy Jesus at the Temple
- [x] T031 [P] [US3] Add New Testament — Miracles of Jesus templates (5-6 stories) to `app/bible_templates.py`: Water into Wine, Calming the Storm, Feeding the 5000, Walking on Water, Healing the Blind Man, Raising Lazarus
- [x] T032 [P] [US3] Add New Testament — Parables of Jesus templates (5-6 stories) to `app/bible_templates.py`: Good Samaritan, Prodigal Son, Lost Sheep, Mustard Seed, Wise and Foolish Builders, Ten Virgins
- [x] T033 [P] [US3] Add New Testament — Holy Week and Resurrection templates (4-5 stories) to `app/bible_templates.py`: Triumphal Entry, Last Supper, Garden of Gethsemane, Crucifixion and Resurrection, Road to Emmaus
- [x] T034 [P] [US3] Add New Testament — Acts and Early Church templates (4-5 stories) to `app/bible_templates.py`: Pentecost, Peter's Vision, Conversion of Paul, Paul and Silas in Prison, Paul's Shipwreck
- [x] T035 [P] [US3] Add New Testament — Epistles and Revelation templates (2-3 stories) to `app/bible_templates.py`: Armor of God (Ephesians 6), Love Chapter (1 Corinthians 13), John's Vision of Heaven (Revelation 21-22)
- [x] T036 [US3] Verify template count reaches 75+ and all templates have valid scripture_reference and section fields in `app/bible_templates.py` — run a quick script to count and validate
- [x] T037 [US3] Remove the initial 10-15 placeholder templates from T011 if they duplicate entries from T023-T035, and ensure `BIBLE_TEMPLATES` list in `app/bible_templates.py` is properly ordered by canonical book order

**Checkpoint**: 75+ templates available, covering Genesis through Revelation, organized by section with scripture references

---

## Phase 6: User Story 4 — Bible Tier Visual Theme and Identity (Priority: P2)

**Goal**: The Bible tier has a warm, reverent visual theme distinct from kids and adult tiers, with appropriate TTS settings

**Independent Test**: Navigate to /bible/ and visually confirm the theme looks distinct from /kids/ with warm, reverent styling. Test TTS with a Bible narration voice.

### Implementation for User Story 4

- [x] T038 [P] [US4] Add `.theme-bible` CSS custom properties to `static/css/style.css` — warm, reverent color palette (deep gold/amber, cream/parchment backgrounds, dark brown text), distinct from bright kids theme and dark adult theme
- [x] T039 [P] [US4] Add `.tier-card-bible` styles to `static/css/style.css` for the landing page card — warm gradient or parchment-style background, appropriate icon/emoji
- [x] T040 [US4] Add Bible tier branding to `templates/home.html` — ensure the tier header shows "Bible Stories" with appropriate styling when tier is bible, using the theme-bible class on the body tag
- [x] T041 [US4] Verify TTS configuration in the bible TierConfig in `app/tiers.py` — ensure tts_default_voice="fable", tts_voices includes storyteller-appropriate options, tts_instructions say "Read this like a warm, reverent Bible story for young children"

**Checkpoint**: Bible tier has a visually distinct warm/reverent theme and appropriate TTS narration voice

---

## Phase 7: User Story 5 — Kids Tier Bible Sampler (Priority: P3)

**Goal**: The 6 existing Bible templates in the kids tier remain functional, with a visible link pointing users to the full Bible tier

**Independent Test**: Verify the 6 Bible templates still appear in the kids tier and that a link to /bible/ is visible

### Implementation for User Story 5

- [x] T042 [US5] Add a cross-link banner or note to `templates/home.html` — when displaying kids tier and Bible templates are visible, show a subtle "Explore our full Bible story library →" link pointing to /bible/
- [x] T043 [US5] Verify the 6 existing Bible story templates in the kids tier still work unchanged — confirm they appear in the template grid and can start stories normally (manual verification)

**Checkpoint**: Kids tier Bible sampler intact, cross-link to full Bible tier visible

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Final validation, cleanup, and cross-cutting improvements

- [x] T044 [P] Verify all existing features work within Bible tier — test gallery, export, resume, branching explorer, read aloud, family mode at /bible/ paths
- [x] T045 [P] Verify session cookie isolation — confirm Bible tier cookies are scoped to /bible/ and don't interfere with kids or nsfw tier sessions
- [x] T046 Run full quickstart.md verification steps from `specs/036-bible-story-tier/quickstart.md` — start server, check /bible/ loads, check landing page, count templates
- [x] T047 Test guided reference field end-to-end — enter a Bible reference (e.g., "Psalm 23"), verify BibleService fetches verses, story starts with accurate content
- [x] T048 Test edge case: invalid Bible reference — enter nonsense text in guided field, verify friendly error message appears
- [x] T049 Test edge case: Bible API unreachable — temporarily unset BIBLE_API_KEY, verify stories still generate using AI training data (graceful fallback)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Phase 1 completion — BLOCKS all user stories
- **US1 Browse & Start (Phase 3)**: Depends on Phase 2 — this is the MVP
- **US2 Biblical Accuracy (Phase 4)**: Depends on Phase 3 (needs working story start flow to inject scripture)
- **US3 Full Library (Phase 5)**: Depends on Phase 3 (needs template rendering working). Can run in parallel with US2 and US4.
- **US4 Visual Theme (Phase 6)**: Can start after Phase 2. Can run in parallel with US2, US3, US5.
- **US5 Kids Sampler (Phase 7)**: Can start after Phase 3 (needs Bible tier to exist for cross-link). Can run in parallel with US3, US4.
- **Polish (Phase 8)**: Depends on all user stories being complete

### User Story Dependencies

- **US1 (P1)**: Can start after Foundational (Phase 2) — No dependencies on other stories
- **US2 (P1)**: Depends on US1 being functional (needs story start flow to inject scripture)
- **US3 (P2)**: Depends on US1 template rendering — templates from T023-T035 are parallel within the phase
- **US4 (P2)**: Independent of other stories — only needs Phase 2 foundation
- **US5 (P3)**: Depends on US1 (Bible tier must exist for cross-link)

### Within Each User Story

- Models/data before services
- Services before routes
- Routes before templates
- Core implementation before integration

### Parallel Opportunities

- **Phase 1**: T003 and T004 can run in parallel (both modify story_options.py but different sections)
- **Phase 2**: T009 can run in parallel with T005-T008 (different files)
- **Phase 5**: ALL template tasks T023-T035 can run in parallel (all write to same file but different sections — in practice, best done sequentially in one session but can be split across agents)
- **Phase 6**: T038 and T039 can run in parallel (same file but different sections)
- **Cross-phase**: US3 (templates), US4 (theme), and US5 (sampler) can proceed in parallel once US1 is complete

---

## Parallel Example: User Story 3 (Template Library)

```bash
# All template groups can be written in parallel (different Bible sections):
Task: "Add OT Genesis templates in app/bible_templates.py"      # T023
Task: "Add OT Exodus templates in app/bible_templates.py"       # T024
Task: "Add OT Judges-Ruth templates in app/bible_templates.py"  # T025
Task: "Add OT Samuel-Kings templates in app/bible_templates.py" # T026
Task: "Add NT Miracles templates in app/bible_templates.py"     # T031
Task: "Add NT Parables templates in app/bible_templates.py"     # T032
# ... etc.
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T004)
2. Complete Phase 2: Foundational (T005-T009)
3. Complete Phase 3: User Story 1 (T010-T018)
4. **STOP and VALIDATE**: Bible tier loads at /bible/, templates display in sections, guided reference works, stories start
5. Deploy/demo if ready — functional Bible tier with ~15 stories

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add US1 (Browse & Start) → Test independently → Deploy (MVP with ~15 stories!)
3. Add US2 (Biblical Accuracy) → Scripture quotes and references in every scene
4. Add US3 (Full Library) → Expand to 75+ stories → Deploy full library
5. Add US4 (Visual Theme) → Polish the look and feel
6. Add US5 (Kids Sampler) → Cross-link from kids tier
7. Polish → Verify all features, edge cases, fallbacks

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- The 75+ templates in Phase 5 are the largest single effort — mostly data authoring, not code
- BibleService uses YouVersion Platform API with NIrV translation (ID 110) — key already in .env
