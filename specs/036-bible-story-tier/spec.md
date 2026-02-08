# Feature Specification: Bible Story Tier

**Feature Branch**: `036-bible-story-tier`
**Created**: 2026-02-08
**Status**: Draft
**Input**: User description: "A dedicated Bible story tier at /bible/ with an extensive library of 75+ stories spanning Genesis to Revelation. Separate public tier alongside Kids Adventures. Content guidelines enforce biblical accuracy — stories must follow actual scripture narrative, quote from NIrV (New International Reader's Version), and include book/chapter references. Interactive choose-your-own-adventure constrained to biblically accurate outcomes. Image style is warm, reverent children's Bible illustration. Stories organized by testament and book. Keep the 6 existing Bible templates in the kids tier as a sampler."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Browse and Start a Bible Story (Priority: P1)

A parent or child opens the Bible Story tier and sees a library of stories organized by testament and book. They can browse through Old Testament and New Testament sections, pick a story like "David and Goliath" or "The Good Samaritan," and immediately start an interactive adventure based on that Bible passage. The story prompt sets the scene faithfully to the scripture, and the opening image has a warm, reverent children's Bible illustration style.

**Why this priority**: This is the core value proposition — an extensive, well-organized Bible story library that's instantly playable. Without this, nothing else matters.

**Independent Test**: Can be tested by navigating to /bible/, browsing the organized library, selecting any template, and verifying the story starts with a biblically faithful scene and appropriate illustration style.

**Acceptance Scenarios**:

1. **Given** the landing page at /, **When** a user views the public tiers, **Then** "Bible Stories" appears alongside "Kids Adventures" as a selectable tier
2. **Given** the Bible tier home page at /bible/, **When** a user views the template library, **Then** stories are organized into collapsible Old Testament and New Testament sections with book sub-groups, ordered by canonical book order
3. **Given** any Bible story template, **When** a user taps it to start, **Then** the story begins with a scene faithful to the referenced scripture passage
4. **Given** the Bible tier, **When** a story is generating, **Then** images use warm, reverent children's Bible illustration style
5. **Given** the Bible tier home page, **When** a user types a Bible reference (e.g., "Ruth 1-4") into the guided prompt field, **Then** the system builds a scripturally constrained story prompt and starts a story for that passage

---

### User Story 2 - Biblically Accurate Interactive Choices (Priority: P1)

During a Bible story, the child encounters choice points that let them engage with the narrative — "What would you do if you were Daniel?" or "How do you think Moses felt?" — but the story always follows the actual biblical narrative arc. Choices explore perspective, emotion, and reflection rather than altering the scriptural outcome. Each scene naturally weaves in NIrV scripture quotes and includes the book/chapter reference.

**Why this priority**: This is what differentiates Bible stories from generic kids stories. The choices must engage the child while remaining faithful to scripture. Without this constraint, the AI could generate theologically inaccurate content.

**Independent Test**: Can be tested by playing through a well-known Bible story (e.g., David and Goliath) and verifying that regardless of choices made, the story follows the biblical narrative, includes NIrV quotes, and references the source passage.

**Acceptance Scenarios**:

1. **Given** a Bible story in progress, **When** the AI generates choices, **Then** choices explore feelings, perspectives, or "what would you do?" moments rather than altering biblical events
2. **Given** any scene in a Bible story, **When** the story text is generated, **Then** it includes at least one naturally woven NIrV scripture quote
3. **Given** any scene in a Bible story, **When** the story text is generated, **Then** the scene references the relevant book and chapter (e.g., "from Genesis 6")
4. **Given** a Bible story played to completion, **When** reviewing the full story, **Then** the narrative arc matches the actual biblical account

---

### User Story 3 - Extensive Library Spanning the Full Bible (Priority: P2)

The library contains 75+ story templates covering major narratives from Genesis through Revelation. Old Testament stories include Creation, the Patriarchs, the Exodus, Judges, Kings, Prophets, and wisdom literature narratives. New Testament stories include the life of Jesus (birth, miracles, parables, death, resurrection), the early church in Acts, and key moments from the epistles and Revelation. Each template includes the scripture reference so families can follow along in their own Bible.

**Why this priority**: The library size is what makes this a dedicated tier rather than just a few templates. Families should be able to use this for months without running out of stories. However, the tier works with even a subset of stories.

**Independent Test**: Can be tested by counting templates and verifying coverage across both testaments, with representation from major books (Genesis, Exodus, Judges, 1 Samuel, Daniel, Jonah, Matthew, Mark, Luke, John, Acts, Revelation at minimum).

**Acceptance Scenarios**:

1. **Given** the Bible tier template library, **When** counting all available templates, **Then** there are at least 75 templates
2. **Given** the Old Testament section, **When** reviewing coverage, **Then** stories span from Genesis through the prophets with representation from at least 15 books
3. **Given** the New Testament section, **When** reviewing coverage, **Then** stories cover Jesus' life, parables, Acts, and Revelation with representation from at least 8 books
4. **Given** any template, **When** viewing its details, **Then** it displays the scripture reference (e.g., "Genesis 6-9", "1 Samuel 17", "Luke 15:1-7")

---

### User Story 4 - Bible Tier Visual Theme and Identity (Priority: P2)

The Bible tier has its own distinct visual theme — warm, reverent, age-appropriate — that feels different from the bright, playful kids tier. The theme should evoke the feeling of opening a beloved children's storybook Bible. The tier has its own TTS voice settings appropriate for Bible story narration.

**Why this priority**: Visual identity helps families mentally associate the tier with "Bible time" and distinguishes it from the general kids tier. Important for the experience but not blocking core functionality.

**Independent Test**: Can be tested by navigating to /bible/ and visually confirming the theme looks distinct from /kids/, with warm, reverent styling.

**Acceptance Scenarios**:

1. **Given** the Bible tier pages, **When** viewing any page, **Then** the visual theme is warm and reverent, distinct from the kids tier's bright playful theme
2. **Given** the Bible tier, **When** a story is read aloud via TTS, **Then** the voice and tone are appropriate for Bible story narration
3. **Given** the Bible tier, **When** viewing the home page, **Then** the tier is clearly identified as "Bible Stories" with appropriate branding

---

### User Story 5 - Kids Tier Bible Sampler (Priority: P3)

The 6 existing Bible story templates in the kids tier remain as a sampler/teaser. They work exactly as they do today, unchanged. Families who discover Bible stories through the kids tier can navigate to the full Bible tier for the complete library.

**Why this priority**: The sampler already exists and works. This story is about preservation and cross-linking, not new functionality.

**Independent Test**: Can be tested by verifying the 6 Bible templates still appear in the kids tier and that a visible link or reference points users to the full Bible tier.

**Acceptance Scenarios**:

1. **Given** the kids tier home page, **When** viewing templates, **Then** the 6 existing Bible story templates are still present and functional
2. **Given** the kids tier Bible templates, **When** a user sees them, **Then** there is a visible indication that a full Bible story library exists at /bible/

---

### Edge Cases

- What happens when an AI model generates content that contradicts scripture? The content guidelines must be strong enough to prevent this, and the choices must be structured to keep the narrative on track.
- What happens when a child makes a choice that would lead away from the biblical narrative? The AI must gently redirect — the next scene should acknowledge the child's choice but steer back to the scriptural account.
- What happens with stories that contain violence or mature themes (e.g., David and Goliath, the Flood, crucifixion)? Content guidelines must handle these with age-appropriate sensitivity — present truthfully but gently, without graphic detail, appropriate for ages 3-8.
- How are stories with difficult theology handled (e.g., God's judgment, sacrifice)? Present in the language of a children's storybook Bible — simple, honest, faith-affirming, without oversimplifying or avoiding the topic.
- What happens when a user enters an invalid or non-existent Bible reference in the guided prompt field? The system should provide a friendly error message and suggest trying a known book name or browsing the template library instead.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST register a new "bible" tier with its own URL prefix (/bible/), content guidelines, image style, and TTS configuration
- **FR-002**: The Bible tier MUST appear on the public landing page alongside "Kids Adventures"
- **FR-003**: Content guidelines MUST instruct the AI to follow actual biblical narrative, quote from the NIrV translation, and include book/chapter references in every scene
- **FR-004**: Content guidelines MUST instruct the AI to generate choices that explore perspective and emotion ("What would you do?") rather than altering biblical events
- **FR-005**: Content guidelines MUST handle sensitive biblical content (violence, judgment, sacrifice) with age-appropriate sensitivity for ages 3-8
- **FR-006**: Each story template MUST include a scripture_reference field identifying the Bible passage (e.g., "Genesis 6-9", "1 Samuel 17"). The reference MUST be displayed on the template card and gallery AND injected into the AI system prompt so the model targets the correct passage.
- **FR-007**: The template library MUST be organized into collapsible Old Testament and New Testament sections, with book sub-groups within each testament. Sections expand/collapse to let users navigate the full 75+ template library without overwhelming scroll. Stories are ordered by canonical book order within each section.
- **FR-008**: The Bible tier MUST include at least 75 story templates spanning Genesis through Revelation
- **FR-009**: The image style for the Bible tier MUST produce warm, reverent children's Bible illustrations
- **FR-010**: The Bible tier MUST have its own visual CSS theme distinct from the kids and adult tiers
- **FR-011**: The Bible tier MUST have its own TTS voice configuration appropriate for Bible story narration
- **FR-012**: The 6 existing Bible story templates in the kids tier MUST remain unchanged
- **FR-013**: The kids tier MUST include a visible link or reference pointing users to the full Bible tier
- **FR-014**: Session cookies for the Bible tier MUST be isolated from other tiers (scoped to /bible/)
- **FR-015**: The Bible tier MUST support all existing story features (gallery, export, resume, branching explorer, read aloud, family mode, etc.)
- **FR-016**: The Bible tier MUST NOT include a free-text story prompt. Instead, it MUST offer a guided "request a Bible story" field where users enter a book/passage reference (e.g., "Ruth 1-4", "Psalm 23") and the system builds a scripturally constrained prompt from it.
- **FR-017**: The guided prompt field MUST validate that the input resembles a Bible book/passage reference and MUST use the same content guidelines and scripture-accuracy constraints as the pre-built templates.

### Key Entities

- **Bible Tier Config**: A new TierConfig entry with name "bible", prefix "bible", content guidelines emphasizing biblical accuracy and NIrV quotes, warm illustration image style, and Bible-appropriate TTS settings
- **Story Template (extended)**: Existing StoryTemplate dataclass extended with an optional scripture_reference field (e.g., "Genesis 1-2", "Matthew 14:22-33") that identifies the Bible passage
- **Template Organization**: Templates grouped by testament (Old/New) and ordered by canonical book order within each testament

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Bible tier is accessible at /bible/ and appears on the landing page as a public tier
- **SC-002**: At least 75 story templates are available, covering both Old and New Testaments
- **SC-003**: Every generated Bible story scene includes at least one NIrV scripture quote and a book/chapter reference
- **SC-004**: Playing through any Bible story to completion results in a narrative that follows the actual biblical account
- **SC-005**: The Bible tier visual theme is visually distinct from both the kids and adult tiers
- **SC-006**: All existing story features (gallery, export, TTS, family mode, etc.) work within the Bible tier without modification
- **SC-007**: The 6 existing Bible templates in the kids tier remain functional and unchanged

## Clarifications

### Session 2026-02-08

- Q: How should the scripture reference be used during story generation? → A: Display + prompt injection — shown to user on template card/gallery AND included in AI system prompt so the model knows the exact passage to follow.
- Q: How should the home page handle 75+ templates? → A: Sectioned + collapsed — Old Testament and New Testament headers that expand/collapse, showing book sub-groups when opened. Allows browsing the full library without overwhelming scroll.
- Q: Should the Bible tier include a free prompt option or only pre-built templates? → A: Templates + guided prompt — no free-text; users pick from the curated library OR type a book/passage reference (e.g., "Ruth 1-4", "Psalm 23") and the system builds a scripturally constrained prompt from it.

## Assumptions

- The existing tier system (TierConfig, router factory pattern) supports adding a third tier without architectural changes — the constitution confirms "New tiers SHOULD be addable without modifying existing tier interfaces"
- The StoryTemplate dataclass can be extended with an optional scripture_reference field without breaking existing templates (kids and nsfw templates will simply have this field unset)
- NIrV verse text will be fetched from the YouVersion Platform API (NIrV translation ID 110) and injected into the AI prompt for accuracy. Falls back to AI training data if API is unreachable.
- The AI models (Claude, GPT, Gemini, Grok) have sufficient knowledge of Bible content to generate accurate narratives from scripture references in the prompt
- 75+ templates is a one-time authoring effort at spec time; templates are hardcoded in the tier config like the existing kids and nsfw templates
- "Organized by testament and book" refers to the visual presentation on the home page, potentially using section headers in the template rendering
