# Feature Specification: "Surprise Me" Button

**Feature Branch**: `024-surprise-me-button`
**Created**: 2026-02-07
**Status**: Draft
**Input**: User description: "Surprise Me" Button — One-tap random story starter on both tiers. Picks a random template (or generates a random prompt if no templates), random story flavor options, random art style. Zero decision fatigue — just hit the button and go. Prominent placement on the home page next to the Start Adventure button. On kids tier, uses kid-safe templates and defaults. On NSFW tier, uses NSFW templates with random kink selections. Should feel fun and instant — single click takes you straight into a story with no form filling needed.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - One-Tap Random Story Start (Priority: P1)

A user visits the home page of either tier and sees a prominent "Surprise Me" button. They click it once and are immediately taken into a new story — no form filling, no decisions. The system randomly selects a template (or generates a random prompt if none exist), picks random story flavor options appropriate for the tier, selects a random art style, and submits the story start automatically.

**Why this priority**: This is the core value proposition — zero decision fatigue, one tap to a story. Without this, the feature has no reason to exist.

**Independent Test**: Can be fully tested by clicking the "Surprise Me" button on the kids tier home page and verifying a story begins with randomly selected parameters. Delivers immediate value by eliminating the need to fill out any form fields.

**Acceptance Scenarios**:

1. **Given** the kids tier home page is loaded, **When** the user clicks the "Surprise Me" button, **Then** a new story begins immediately using a randomly selected kids template, random story flavor options, and a random art style.
2. **Given** the NSFW tier home page is loaded, **When** the user clicks the "Surprise Me" button, **Then** a new story begins immediately using a randomly selected NSFW template, random kink selections, random story flavor options, and a random art style.
3. **Given** either tier's home page is loaded, **When** the user clicks "Surprise Me" multiple times across sessions, **Then** different stories start each time (randomization produces variety).

---

### User Story 2 - Tier-Appropriate Random Selection (Priority: P2)

The random selection logic respects tier boundaries. On the kids tier, only kid-safe templates, gentle story options, and child-friendly art styles are used. On the NSFW tier, adult templates with random kink toggles are selected. The user never sees content from the wrong tier.

**Why this priority**: Content isolation is a core project principle. Without tier-appropriate randomization, the feature could violate content safety boundaries.

**Independent Test**: Can be tested by triggering surprise-me on the kids tier and verifying all selected parameters (template, options, art style) are from the kids-safe set, then doing the same on the NSFW tier and verifying adult content parameters are used.

**Acceptance Scenarios**:

1. **Given** the kids tier, **When** "Surprise Me" is clicked, **Then** the selected template is from the kids template list, story flavor options use kids-tier values, and the art style is child-appropriate.
2. **Given** the NSFW tier, **When** "Surprise Me" is clicked, **Then** the selected template is from the NSFW template list, random kink toggles are selected, and story flavor options use NSFW-tier values.
3. **Given** the kids tier, **When** "Surprise Me" is clicked, **Then** no NSFW kinks, adult conflict types, or mature art styles appear in the story parameters.

---

### User Story 3 - Prominent Button Placement (Priority: P3)

The "Surprise Me" button is placed prominently on the home page, visually distinct and easy to find. It should feel fun and inviting — not buried in the form or hidden behind a menu. It sits next to (or near) the existing "Start Adventure" button.

**Why this priority**: Discoverability matters for adoption, but the feature works even with a less prominent button. UX polish can be iterated.

**Independent Test**: Can be tested by loading the home page and verifying the "Surprise Me" button is visible without scrolling, visually distinct from other elements, and positioned near the "Start Adventure" button.

**Acceptance Scenarios**:

1. **Given** the home page is loaded on either tier, **When** the page renders, **Then** the "Surprise Me" button is visible in the primary action area near the "Start Adventure" button.
2. **Given** the home page on a mobile device, **When** the page renders, **Then** the "Surprise Me" button is visible and tappable without scrolling past the fold.

---

### Edge Cases

- What happens when no templates are defined for a tier? The system generates a random creative prompt instead.
- What happens when no art styles are available? The system uses the default/no-style option.
- What happens when no AI models are available? The "Surprise Me" button is disabled (same as the Start Adventure button).
- What happens when there is already a story in progress (resume banner visible)? The "Surprise Me" button still works — it starts a fresh story (same behavior as manually starting a new one).
- What happens when a profile is active? The "Surprise Me" flow does NOT auto-select a profile — it starts a clean story. Profiles require deliberate selection.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST display a "Surprise Me" button on the home page of both tiers.
- **FR-002**: Clicking "Surprise Me" MUST immediately start a new story with no additional user input required.
- **FR-003**: System MUST randomly select a template from the current tier's template list when templates exist.
- **FR-004**: If no templates exist for the tier, system MUST generate a random creative prompt suitable for the tier's content guidelines.
- **FR-005**: System MUST randomly select values for all story flavor options (protagonist gender, age, character type, cast size, writing style, story type) from the current tier's option set.
- **FR-006**: System MUST randomly select an art style from available art styles.
- **FR-007**: System MUST randomly select a story length from short/medium/long options.
- **FR-008**: On the NSFW tier, system MUST randomly select 0-2 kink toggles from the available kink options.
- **FR-009**: On the kids tier, system MUST NOT include any kink selections or adult-only options.
- **FR-010**: The "Surprise Me" button MUST be disabled when no AI models are available (matching existing Start Adventure behavior).
- **FR-011**: The "Surprise Me" action MUST use the same story start endpoint and flow as the manual form, just with randomly generated parameters.

### Key Entities

- **Random Story Parameters**: The randomly assembled set of template/prompt, story length, art style, story flavor options, and tier-specific extras (kinks for NSFW). Not persisted separately — fed directly into the existing story start flow.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can start a new story in a single click with zero form interaction.
- **SC-002**: Repeated "Surprise Me" clicks produce visibly different stories (different prompts, themes, styles).
- **SC-003**: Kids tier "Surprise Me" stories contain only age-appropriate content parameters.
- **SC-004**: The "Surprise Me" button is visible on both tier home pages without scrolling on standard viewport sizes.

## Assumptions

- The existing story start endpoint (`/story/start`) handles all required parameters and does not need modification — the "Surprise Me" feature assembles parameters client-side or server-side and submits to the same endpoint.
- Art styles are available via the existing `get_art_styles()` function.
- The randomization does not need to be cryptographically secure — simple pseudo-random selection is sufficient.
- The "Surprise Me" button does not need to remember or avoid repeating previous selections.

## Scope

### In Scope

- "Surprise Me" button on both tier home pages
- Random selection of template, story flavor options, art style, length, and kinks (NSFW only)
- Server-side endpoint to handle random parameter assembly and story start
- Visual styling of the button to feel fun and prominent

### Out of Scope

- Remembering or learning user preferences for "Surprise Me" selections
- A/B testing or analytics on random selections
- Custom weighting of random selections (all options equally likely)
- Integration with profiles or character roster in the random flow
