# Feature Specification: Mid-Story Length Control

**Feature Branch**: `025-mid-story-length`
**Created**: 2026-02-08
**Status**: Draft
**Input**: User description: Mid-Story Length Control — "Keep going" button when a story is approaching its ending to extend the target depth. "Wrap it up" button to end early when a story is dragging. Adjusts target_depth on the fly and signals the AI to either extend or conclude within 1-2 more scenes. Both buttons appear on the scene page when appropriate — "Keep going" shows when depth >= target_depth - 2, "Wrap it up" shows when depth >= 2. Simple buttons, no settings or configuration needed.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Extend Story with "Keep Going" (Priority: P1)

A user is reading a story that is approaching its planned ending (within 2 scenes of the target depth). They are enjoying the story and want it to continue. They see a "Keep Going" button on the scene page, click it, and the story's target depth is extended so the AI generates more scenes instead of wrapping up.

**Why this priority**: This is the most impactful control — users often want stories to keep going when they're engaged. Without it, stories end abruptly when the target depth is reached.

**Independent Test**: Can be fully tested by starting a story, advancing to within 2 scenes of the target depth, clicking "Keep Going", and verifying the AI generates additional continuation scenes rather than rushing to an ending.

**Acceptance Scenarios**:

1. **Given** a story at depth 3 with target_depth 5, **When** the user clicks "Keep Going", **Then** the target_depth is increased and the next AI-generated scene does not force an ending.
2. **Given** a story at depth 4 with target_depth 5, **When** the user clicks "Keep Going", **Then** the target_depth is increased and the story continues with new choices.
3. **Given** a story at depth 1 with target_depth 5, **When** the user views the scene, **Then** the "Keep Going" button is NOT visible (too early in the story).

---

### User Story 2 - End Story Early with "Wrap It Up" (Priority: P2)

A user is reading a story that feels like it's dragging or they need to stop. After at least 2 scenes, they see a "Wrap It Up" button. Clicking it signals the AI to conclude the story within 1-2 more scenes, bringing it to a satisfying ending without cutting off abruptly.

**Why this priority**: Ending early is less common than extending but equally important for user satisfaction. A story that drags is worse than one that ends neatly.

**Independent Test**: Can be tested by starting a long story, advancing past scene 2, clicking "Wrap It Up", and verifying the next 1-2 scenes bring the story to a natural conclusion.

**Acceptance Scenarios**:

1. **Given** a story at depth 3 with target_depth 7, **When** the user clicks "Wrap It Up", **Then** the target_depth is reduced so the AI concludes the story within 1-2 more scenes.
2. **Given** a story at depth 1 with target_depth 5, **When** the user views the scene, **Then** the "Wrap It Up" button is NOT visible (too early to wrap up).
3. **Given** a story at depth 2 with target_depth 7, **When** the user clicks "Wrap It Up", **Then** the AI signals an ending is near and begins wrapping up the narrative.

---

### User Story 3 - Button Visibility Rules (Priority: P3)

Buttons appear only when contextually appropriate. "Keep Going" appears when the story is nearing its end (within 2 scenes of target depth). "Wrap It Up" appears after at least 2 scenes have been generated. Both buttons disappear on ending scenes. This prevents clutter and ensures users only see controls when they're relevant.

**Why this priority**: Correct visibility is a polish concern — the feature works without perfect visibility rules, but proper rules prevent confusion.

**Independent Test**: Can be tested by navigating through a story at various depths and verifying each button appears/disappears at the correct thresholds.

**Acceptance Scenarios**:

1. **Given** a story at depth 0, **When** the scene loads, **Then** neither button is visible.
2. **Given** a story at depth 2 with target_depth 7, **When** the scene loads, **Then** only "Wrap It Up" is visible.
3. **Given** a story at depth 5 with target_depth 7, **When** the scene loads, **Then** both "Keep Going" and "Wrap It Up" are visible.
4. **Given** a scene that is an ending, **When** the scene loads, **Then** neither button is visible.

---

### Edge Cases

- What happens when "Keep Going" is clicked multiple times? Each click extends the target depth further. There is no maximum limit — the user can keep extending indefinitely.
- What happens when "Wrap It Up" is clicked when depth equals target_depth - 1? The target depth is set to current depth + 1, ensuring exactly one more scene.
- What happens when "Wrap It Up" sets target_depth equal to current depth? The next scene generated will be flagged as the ending.
- What happens on a story started via "Surprise Me"? The buttons work identically — they operate on the story's target_depth regardless of how the story was started.
- What happens in gallery reader mode (reading a completed story)? The buttons do NOT appear — they only show during active story sessions.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST display a "Keep Going" button on the scene page when the current scene depth is greater than or equal to target_depth minus 2 and the scene is not an ending.
- **FR-002**: System MUST display a "Wrap It Up" button on the scene page when the current scene depth is greater than or equal to 2 and the scene is not an ending.
- **FR-003**: Clicking "Keep Going" MUST increase the story's target_depth by 3 scenes.
- **FR-004**: Clicking "Wrap It Up" MUST set the story's target_depth to the current depth plus 2 (ensuring 1-2 more scenes).
- **FR-005**: If "Wrap It Up" would set target_depth to less than or equal to the current depth, system MUST set target_depth to current depth plus 1 (guaranteeing at least one more scene).
- **FR-006**: After adjusting target_depth, the system MUST persist the new value so subsequent AI scene generation uses the updated target.
- **FR-007**: Neither button MUST appear on ending scenes.
- **FR-008**: Neither button MUST appear in the gallery reader (completed stories).
- **FR-009**: "Keep Going" MUST be clickable multiple times with cumulative effect (each click adds 3 more scenes).
- **FR-010**: After clicking either button, the user MUST be redirected back to the same scene they were viewing.

### Key Entities

- **Story target_depth**: The existing story attribute that controls when the AI begins wrapping up the narrative. This feature modifies it dynamically during an active story session.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can extend a story beyond its original target length with a single click.
- **SC-002**: Users can signal the AI to wrap up a story early with a single click.
- **SC-003**: Buttons appear only at contextually appropriate moments (not on the first scene, not on endings, not in gallery view).
- **SC-004**: Story length adjustments take effect immediately on the next AI-generated scene.

## Assumptions

- The existing story model already has a `target_depth` attribute that the AI uses to determine when to conclude the story.
- The "Keep Going" extension amount of 3 scenes provides a meaningful extension without being too much. Users can click multiple times for longer extensions.
- The "Wrap It Up" buffer of 2 scenes gives the AI enough room to craft a satisfying conclusion without dragging.
- The minimum depth threshold of 2 for "Wrap It Up" ensures users have experienced enough story to make a meaningful decision about ending early.
- The buttons are simple POST actions that redirect back to the current scene — no AJAX or dynamic UI needed.

## Scope

### In Scope

- "Keep Going" and "Wrap It Up" buttons on the active story scene page
- Dynamic adjustment of target_depth on the story session
- Visibility rules based on current depth, target depth, and scene type
- Persistence of updated target_depth across scene generations

### Out of Scope

- Configurable extension amounts (fixed at +3 for extend, +2 for wrap up)
- Visual indicators showing how many scenes remain
- Undo functionality for length adjustments
- Length control in gallery reader mode
