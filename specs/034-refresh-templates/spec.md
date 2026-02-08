# Feature Specification: Refresh Templates Button

**Feature Branch**: `034-refresh-templates`
**Created**: 2026-02-07
**Status**: Draft
**Input**: User description: "Refresh Templates Button — Add a 'refresh' or 'shuffle' button on the home page that regenerates the set of story templates shown. Instead of always seeing the same templates, users can tap refresh to get a new random selection. Useful when the kids want variety without scrolling through a long static list. Both tiers."

## User Scenarios & Testing

### User Story 1 - Shuffle Visible Templates (Priority: P1)

A user on either the kids or adult tier visits the home page and sees the usual set of story template cards. They want to see different options without scrolling through a long static list. They tap a "Shuffle" button near the template section, and the displayed templates are replaced with a different random selection from the full pool. The page does not reload — the templates visually swap in place.

**Why this priority**: This is the core feature — without the shuffle action, there is no feature. It delivers the primary value of variety and discovery.

**Independent Test**: Can be fully tested by loading the home page, clicking the shuffle button, and verifying that the displayed template set changes.

**Acceptance Scenarios**:

1. **Given** a user is on the home page with templates displayed, **When** they tap the "Shuffle" button, **Then** the visible template cards are replaced with a different random selection from the full template pool.
2. **Given** the template pool has more templates than the display limit, **When** shuffle is tapped, **Then** the new selection does not duplicate the previously shown set (unless the pool is too small to avoid overlap).
3. **Given** the template pool is small enough that all templates fit on screen at once, **When** shuffle is tapped, **Then** the displayed templates are reordered randomly.

---

### User Story 2 - Expanded Template Pool (Priority: P2)

To make the shuffle button meaningful, each tier has a larger pool of templates than the number shown at once. The home page displays a fixed number of templates (e.g., 6) drawn randomly from a larger pool (e.g., 12-20 per tier). On each page load, the initial selection is also random.

**Why this priority**: Without a pool larger than the display count, the shuffle button has little value. This story provides the content that makes shuffling worthwhile.

**Independent Test**: Can be tested by loading the home page multiple times and verifying that the initial template selection varies between loads.

**Acceptance Scenarios**:

1. **Given** a tier has more templates in its pool than the display limit, **When** the home page loads, **Then** a random subset of templates is shown.
2. **Given** a user refreshes the page, **When** the page reloads, **Then** there is a reasonable chance of seeing a different set of templates than the previous load.

---

### Edge Cases

- What happens when a tier has fewer templates than the display limit? All templates are shown, and the shuffle button reorders them randomly.
- What happens when a user taps shuffle rapidly multiple times? Each tap produces a new random selection; no debounce needed since this is a lightweight client-side operation.
- What happens when templates are selected via shuffle and the user picks one? The selected template populates the form fields exactly as it does today — shuffle does not affect template selection behavior.

## Requirements

### Functional Requirements

- **FR-001**: System MUST display a "Shuffle" button near the template section on the home page for both tiers.
- **FR-002**: Tapping the shuffle button MUST replace the visible template cards with a different random selection from the full template pool without a page reload.
- **FR-003**: Each tier MUST have a pool of at least 12 templates to draw from.
- **FR-004**: The home page MUST display a fixed number of templates (6) selected randomly from the pool on each page load.
- **FR-005**: The shuffle button MUST be visually consistent with the existing home page design and clearly labeled with its purpose.
- **FR-006**: Selecting a template after a shuffle MUST populate the story start form identically to selecting a template shown on initial load.
- **FR-007**: The shuffle action MUST work entirely on the client side (no server round-trip required).

## Success Criteria

### Measurable Outcomes

- **SC-001**: Users can access a new set of templates in under 1 second by tapping the shuffle button.
- **SC-002**: Each tier offers at least 12 story templates in its pool, with 6 shown at a time.
- **SC-003**: 100% of template interactions (select, auto-fill form) continue to work correctly after a shuffle.
- **SC-004**: The shuffle button is visible and accessible on both kids and adult tier home pages.

## Assumptions

- The display limit of 6 templates at a time is a reasonable default that balances variety with visual density on the page.
- A pool of 12-20 templates per tier provides enough variety for meaningful shuffles without requiring excessive content creation.
- Client-side shuffling is preferred over server-side to avoid unnecessary network requests and keep the interaction instant.
- The full template pool is embedded in the page on load (not fetched on demand), keeping the architecture simple.
