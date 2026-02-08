# Feature Specification: Story Templates

**Feature Branch**: `015-story-templates`
**Created**: 2026-02-07
**Status**: Draft
**Input**: User description: "story templates"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Browse and Start from a Template (Priority: P1)

A user opens the home page and sees a collection of pre-built story templates displayed as clickable cards above the free-form prompt area. Each template card shows a title, a short description, and an icon or emoji. The user taps a template card and the story form is pre-filled with the template's prompt text, suggested story length, and any other defaults. The user can modify the pre-filled values or start the story immediately.

**Why this priority**: This is the core value of the feature — reducing the "blank page" problem. Many users (especially kids) struggle to come up with a story prompt from scratch. Templates provide instant inspiration and a one-tap start experience.

**Independent Test**: Can be fully tested by loading the home page, clicking a template card, verifying form fields are pre-filled, and submitting to start a story.

**Acceptance Scenarios**:

1. **Given** a user is on the home page, **When** they view the page, **Then** they see a section of template cards above the free-form prompt area.
2. **Given** a user sees template cards, **When** they click a template card, **Then** the prompt textarea is filled with the template's prompt text, the story length selector is set to the template's suggested length, and any other template defaults are applied.
3. **Given** a user has selected a template and the form is pre-filled, **When** they modify the prompt text, **Then** the changes are preserved and submitted with their edits.
4. **Given** a user has selected a template, **When** they click "Begin Your Adventure", **Then** the story starts with the template's pre-filled values (or user's modifications).

---

### User Story 2 - Tier-Specific Template Collections (Priority: P2)

Each content tier (kids, adult) has its own curated set of templates that match the tier's audience, tone, and content guidelines. The kids tier shows age-appropriate templates (fairy tales, animal adventures, space exploration) while the adult tier shows mature-themed templates (noir detective, horror survival, political thriller). Templates are not shared across tiers.

**Why this priority**: Content isolation is a core project principle. Templates must respect tier boundaries to maintain the safety guarantees of the kids tier.

**Independent Test**: Load the kids home page and verify only kid-friendly templates appear. Load the adult home page and verify only adult templates appear. Confirm no cross-tier template leakage.

**Acceptance Scenarios**:

1. **Given** a user is on the kids home page, **When** they view the templates section, **Then** all templates shown are age-appropriate for children ages 3-6.
2. **Given** a user is on the adult home page, **When** they view the templates section, **Then** templates shown include mature themes suitable for adults.
3. **Given** templates exist for both tiers, **When** comparing the two sets, **Then** there is no overlap — each tier has its own distinct collection.

---

### User Story 3 - Template Replaces Suggestion Chips (Priority: P3)

The existing suggestion chips (hardcoded prompt ideas at the bottom of the form) are replaced by the template system. Templates serve the same purpose — providing inspiration — but with a richer presentation (title, description, icon) and the ability to pre-fill more than just the prompt text. This declutters the UI by consolidating two similar features into one.

**Why this priority**: This is a cleanup/polish item. The app works fine with both chips and templates, but having two sources of prompt inspiration is confusing. Consolidating them simplifies the UI.

**Independent Test**: Load the home page and verify suggestion chips are no longer displayed. Verify templates serve as the sole source of pre-built story ideas.

**Acceptance Scenarios**:

1. **Given** templates are implemented, **When** a user views the home page, **Then** the old suggestion chips section is no longer visible.
2. **Given** a user who previously relied on suggestion chips, **When** they use the templates instead, **Then** they can achieve the same outcome (starting a story from a pre-built idea) with equal or less effort.

---

### Edge Cases

- What happens when a template specifies a story length but the user changes it before starting? The user's selection takes precedence.
- What happens when a template specifies a model that is not currently available (e.g., API key missing)? The system falls back to the default available model, same as the current behavior for manual model selection.
- What happens if the template collection is empty for a tier? The home page displays only the free-form prompt area without a templates section, functioning identically to the current experience.
- What happens if a user selects a template, then manually clears the prompt textarea? The system treats it as an empty prompt and shows the existing validation error ("Please enter a prompt").
- What happens on very narrow mobile screens (320px)? Template cards stack vertically in a single column and remain tappable.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST display a collection of story template cards on each tier's home page, above the free-form prompt area.
- **FR-002**: Each template card MUST display a title, a short description (1-2 sentences), and a visual indicator (emoji or icon).
- **FR-003**: System MUST pre-fill the story prompt textarea when a user selects a template card.
- **FR-004**: System MUST pre-fill the story length selector when a template specifies a suggested length.
- **FR-005**: Users MUST be able to modify any pre-filled form values before starting the story.
- **FR-006**: System MUST maintain separate template collections per content tier with no cross-tier access.
- **FR-007**: The kids tier MUST include at least 6 templates covering diverse genres (e.g., animal adventure, fairy tale, space exploration, underwater quest, forest mystery, superhero origin).
- **FR-008**: The adult tier MUST include at least 6 templates covering diverse genres (e.g., noir detective, horror survival, sci-fi thriller, fantasy epic, political intrigue, post-apocalyptic journey).
- **FR-009**: System MUST remove the existing suggestion chips from the home page, replacing their function with the template cards.
- **FR-010**: Template cards MUST be responsive — displaying in a grid on desktop (2-3 columns) and stacking to a single column on mobile.
- **FR-011**: System MUST visually highlight the currently selected template card until the user deselects it or selects a different one.
- **FR-012**: Users MUST be able to deselect a template and return to a blank form by clicking the selected template again or a "Clear" action.
- **FR-013**: Templates MUST be stored as static configuration data within the application (no database or external service required).

### Key Entities

- **Story Template**: A pre-built story starter with a title, description, emoji/icon, prompt text, suggested story length, and tier association. Each template belongs to exactly one content tier.
- **Template Collection**: An ordered list of story templates for a given tier. Displayed on the tier's home page.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can start a story from a template with 2 or fewer interactions (tap template, tap start button).
- **SC-002**: Each content tier displays at least 6 unique templates on the home page.
- **SC-003**: Template selection and form pre-fill completes instantly (no perceptible delay to user).
- **SC-004**: All template cards are fully visible and tappable on screens as narrow as 320px without horizontal scrolling.
- **SC-005**: No kid-inappropriate content appears in the kids tier template collection.
- **SC-006**: The home page loads in the same time or faster than before (no additional network requests for template data).

## Assumptions

- Templates are defined as static data in the application configuration, similar to how suggestion chips are currently defined in tier configuration. No admin UI or dynamic management is needed.
- Template prompt text is a starting suggestion — users are always free to edit it before starting.
- The template's suggested length is a default, not a constraint. Users can change it.
- Templates do not specify a preferred AI model or image model — those remain user-selected.
- The number of templates per tier (starting at 6) may grow over time but does not need pagination for the foreseeable future (under 20 templates per tier).
- Removing suggestion chips is a clean replacement — no migration or backward compatibility needed since chips were purely presentational.

## Out of Scope

- User-created custom templates (would require storage layer, CRUD operations)
- Template categories or filtering (unnecessary at 6-12 templates per tier)
- Template popularity tracking or recommendations
- AI-generated template suggestions
- Template sharing across users
