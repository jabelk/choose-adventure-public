# Feature Specification: Enhanced Character Creation & Relationship Depth

**Feature Branch**: `042-character-depth`
**Created**: 2026-02-08
**Status**: Draft
**Input**: User description: "Structured character creator with mobile-friendly dropdowns/buttons for physical attributes, personality, and style. Relationship tracker across stories. Expanded kink toggles."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Structured Character Creator (Priority: P1)

A user creating a new character in the NSFW roster taps through mobile-friendly pill selectors and button groups to define the character's appearance (hair color, hair length, eye color, skin tone, body type, bust size, height), personality (temperament, energy, archetype), and style (clothing style, aesthetic vibe). The selections are composed into a rich text description automatically, replacing the need to type a paragraph. The user can still override with free-text if they want more nuance.

**Why this priority**: The current free-text description field requires users to think of what to write and type on mobile keyboards, which is friction-heavy. Structured inputs make character creation fast, consistent, and fun — directly improving the quality of every story and agent mode session that uses the character.

**Independent Test**: Navigate to /nsfw/characters, tap "Create Character", fill in name, tap through attribute selectors (hair: blonde, body: athletic, personality: playful, etc.), save. Verify the character appears in the roster with a composed description. Start a story with that character and verify the AI uses the structured attributes in narration and image generation.

**Acceptance Scenarios**:

1. **Given** a user is on the character creation page, **When** they enter a name and tap attribute pills for hair color (blonde), body type (athletic), bust size (D), height (tall), temperament (playful), archetype (girl next door), **Then** a composed description is generated and saved with the character.
2. **Given** a user has created a character with structured attributes, **When** they start a story with that character, **Then** the AI narration and image prompts reflect the selected attributes accurately.
3. **Given** a user is on mobile, **When** they interact with the attribute selectors, **Then** all selectors are tap-friendly pill buttons (no dropdowns that require scrolling), and the form is usable without a keyboard.
4. **Given** a user wants more control, **When** they type additional text in a free-text override field, **Then** the override text is appended to the composed description.
5. **Given** a user is editing an existing character, **When** they view the edit form, **Then** all previously selected attributes are pre-selected in the pill buttons.

---

### User Story 2 - Quick Character Builder on Story Start (Priority: P1)

When starting a new story or agent mode chat, the "Character" section on the start form offers the same structured attribute selectors as the roster creation page (in addition to the existing roster picker and manual name/description fields). A user who doesn't have saved characters can quickly tap through attributes to define a one-off character without leaving the story start flow.

**Why this priority**: Many users jump straight to starting a story without visiting the roster page first. Offering structured inputs inline eliminates friction and ensures every story has a well-defined character.

**Independent Test**: Navigate to /nsfw/, expand the Character section, tap attribute pills to define a character, start a story. Verify the character attributes appear in the AI narration and image prompts.

**Acceptance Scenarios**:

1. **Given** a user is on the story start form, **When** they expand the Character section, **Then** they see structured attribute selectors (same options as roster creation) alongside the existing roster picker and manual fields.
2. **Given** a user selects attributes via pills on the start form, **When** they submit the form, **Then** the composed description is injected into the story prompt.
3. **Given** a user selects a roster character AND also taps attribute pills, **When** they submit, **Then** the roster character takes priority and the inline attributes are ignored.

---

### User Story 3 - Relationship Tracker (Priority: P2)

A user who plays multiple stories with the same roster character sees their relationship evolve across sessions. The relationship stage (strangers, acquaintances, flirting, dating, intimate, committed) is tracked per character and auto-advances based on story completion. When starting a new story with a character, the AI knows the relationship history and adjusts tone accordingly — a first encounter feels different from a tenth date.

**Why this priority**: Adds depth and continuity that makes characters feel like persistent companions rather than disposable story props. Builds on the existing roster system.

**Independent Test**: Create a character, complete 2-3 stories with them. Verify the relationship stage advances on the character detail page. Start a new story and verify the AI references prior history.

**Acceptance Scenarios**:

1. **Given** a user has completed a story with a roster character, **When** they view that character's detail page, **Then** they see the current relationship stage and story count.
2. **Given** a character's relationship stage is "flirting", **When** the user starts a new story with that character, **Then** the AI prompt includes relationship context (e.g., "You and [character] have been flirting — there's clear chemistry").
3. **Given** a user completes a story with a character at "acquaintances" stage, **When** the story ends, **Then** the relationship stage auto-advances to the next level.
4. **Given** a user wants to manually adjust the relationship stage, **When** they visit the character detail page, **Then** they can tap a stage selector to set it manually.

---

### User Story 4 - Expanded Kink Toggles (Priority: P3)

The story start form offers additional kink/theme toggles beyond the current four (MTF transformation, breast expansion, seduction, body sculpting). New toggles include: role reversal, power dynamics, clothing destruction, size difference, dominance/submission, hypnosis, and bimboification. Each toggle has story prompt and image prompt additions that shape the AI's output.

**Why this priority**: More variety in content themes. Quick wins since the kink toggle infrastructure already exists — this is primarily data authoring.

**Independent Test**: Navigate to /nsfw/, verify new kink toggles appear as pills. Select one or more, start a story, verify the AI incorporates the selected themes.

**Acceptance Scenarios**:

1. **Given** a user is on the NSFW story start form, **When** they scroll to the kink toggles section, **Then** they see at least 10 toggle options (existing 4 + new additions).
2. **Given** a user selects the "power dynamics" toggle, **When** they start a story, **Then** the AI narration includes power dynamic themes and the image prompts reflect the aesthetic.
3. **Given** a user selects multiple kink toggles, **When** they start a story, **Then** all selected themes are blended coherently in the AI output.

---

### Edge Cases

- What happens when a user saves a character with no attributes selected (only a name)? The description defaults to empty, same as current behavior.
- What happens when the structured attribute options are updated in a future release and existing characters have outdated attribute values? The composed description is stored as text, so old characters remain valid. Attribute selections are stored separately for edit form pre-population.
- What happens when a character's relationship stage is at the maximum level? It stays at the maximum; no further auto-advancement.
- What happens when a story is abandoned (not completed) — does the relationship still advance? No, relationship only advances on story completion.
- What happens on the kids or Bible tier? Structured creator is available (age-appropriate attributes only: hair color, eye color, height — no bust size, no body type). Relationship tracker and kink toggles are NSFW-only.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide structured attribute selectors for character physical appearance: hair color (8+ options), hair length (4 options), eye color (6+ options), skin tone (6+ options), body type (5+ options, NSFW only), bust size (5+ options, NSFW only), height (4 options).
- **FR-002**: System MUST provide structured attribute selectors for character personality: temperament (6+ options), energy (4+ options), archetype (6+ options, NSFW only).
- **FR-003**: System MUST provide structured attribute selectors for character style: clothing style (6+ options), aesthetic vibe (4+ options).
- **FR-004**: System MUST compose selected attributes into a natural-language description suitable for AI story and image prompts.
- **FR-005**: System MUST allow free-text override that appends to or replaces the composed description.
- **FR-006**: System MUST store both the structured attribute selections (for form re-population) and the composed text description (for prompt injection) per character.
- **FR-007**: System MUST display structured attribute selectors as mobile-friendly tap targets (pill buttons or segmented controls), not dropdown menus.
- **FR-008**: System MUST offer the same structured attribute selectors on both the character roster creation page and the story/agent start form's character section.
- **FR-009**: System MUST track relationship stage per roster character with at least 6 progression levels.
- **FR-010**: System MUST auto-advance relationship stage when a story with that character is completed.
- **FR-011**: System MUST inject relationship context into AI prompts when starting a story with a character that has relationship history.
- **FR-012**: System MUST allow manual relationship stage adjustment on the character detail page.
- **FR-013**: System MUST display relationship stage and story count on the character detail/edit page.
- **FR-014**: System MUST provide at least 7 additional kink/theme toggles beyond the existing 4, each with story prompt and image prompt additions.
- **FR-015**: System MUST restrict bust size, body type, archetype, and kink toggles to the NSFW tier only. Kids and Bible tiers show only age-appropriate attribute options.

### Key Entities

- **Character Attributes**: Structured key-value pairs representing physical, personality, and style selections for a character. Stored alongside the existing character data.
- **Relationship Stage**: A progression level (strangers, acquaintances, flirting, dating, intimate, committed) tracked per roster character. Includes story count and last interaction date.
- **Kink Toggle**: A theme toggle with display name, story prompt addition, and image prompt addition. Extends the existing toggle system.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can create a fully-described character in under 30 seconds using only tap interactions (no typing required beyond the name field).
- **SC-002**: Characters created via structured attributes produce AI-generated images that consistently reflect the selected hair color, body type, and style across scenes.
- **SC-003**: Relationship stage is visible on the character page and updates after each completed story.
- **SC-004**: All structured attribute selectors are usable on mobile screens (minimum 44px tap targets, no horizontal scrolling required).
- **SC-005**: At least 11 kink/theme toggles are available on the NSFW story start form.
- **SC-006**: Existing characters and stories continue to work unchanged after this feature is deployed (backward compatibility).

## Assumptions

- Structured attribute options are hardcoded lists (same pattern as existing kink toggles and story options), not user-configurable.
- The composed description is generated client-side for instant preview, then validated/regenerated server-side on save.
- Relationship auto-advancement uses simple heuristics (story completed = advance one stage) rather than AI content analysis, to keep it deterministic and fast.
- The kids/Bible tier gets a simplified version of the structured creator (hair color, eye color, height only — no NSFW attributes).
