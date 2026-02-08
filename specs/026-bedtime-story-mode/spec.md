# Feature Specification: Bedtime Story Mode

**Feature Branch**: `026-bedtime-story-mode`
**Created**: 2026-02-08
**Status**: Draft
**Input**: User description: Bedtime Story Mode — Toggle that makes stories calming, shorter, always ends with the character going to sleep or settling in. Auto-dims the UI with a warm night-mode color scheme. Maybe a 5-minute wind-down timer. Content guidelines shift to gentle, soothing, no tension. Kids tier only.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Bedtime Story Toggle (Priority: P1)

A parent is putting their child to bed and wants a calming story. On the kids home page, they check a "Bedtime Mode" toggle before starting a story. The system generates a gentle, soothing story with no tension or conflict that always ends with the character settling in for sleep. Stories are shorter than usual (2-3 scenes).

**Why this priority**: This is the core feature — without the toggle and modified content guidelines, there is no bedtime story mode. Everything else builds on top of this.

**Independent Test**: Can be fully tested by checking the bedtime toggle, starting a story, and verifying the generated scenes are calming, shorter, and end with a sleep-themed conclusion.

**Acceptance Scenarios**:

1. **Given** the kids home page, **When** the user checks the "Bedtime Mode" toggle and starts a story, **Then** the story uses bedtime-specific content guidelines (gentle, soothing, no tension) and a shorter target depth of 3 scenes.
2. **Given** a bedtime mode story in progress, **When** the AI generates the final scene, **Then** the ending involves the character settling in for sleep, getting cozy, or drifting off peacefully.
3. **Given** the kids home page with Bedtime Mode on, **When** the user clicks "Surprise Me", **Then** the surprise story also uses bedtime content guidelines and the shorter target depth.
4. **Given** the NSFW tier home page, **When** the user views the page, **Then** no bedtime mode toggle is visible.

---

### User Story 2 - Bedtime Night Theme (Priority: P2)

When bedtime mode is active, the UI switches to a warm, dimmed color scheme with muted tones — dark navy or deep purple background, soft amber/gold accents, reduced brightness. This creates a cozy, sleep-inducing atmosphere and reduces screen glare in a dark bedroom.

**Why this priority**: The visual theme is a strong UX enhancer that makes the bedtime experience feel distinctly different from regular stories, but the feature works without it (stories are still calming even with the default theme).

**Independent Test**: Can be tested by enabling bedtime mode and verifying the page renders with the bedtime color scheme instead of the default kids theme.

**Acceptance Scenarios**:

1. **Given** a story started with bedtime mode enabled, **When** a scene page loads, **Then** the page uses the bedtime night theme (warm, dimmed colors) instead of the default kids theme.
2. **Given** a story started without bedtime mode, **When** a scene page loads, **Then** the page uses the normal kids theme.
3. **Given** a bedtime mode story, **When** the user navigates to the home page via the back link, **Then** the home page returns to the normal kids theme.

---

### User Story 3 - Wind-Down Timer (Priority: P3)

A subtle countdown timer appears on bedtime mode scenes showing how long the story has been running. After 5 minutes, the timer gently pulses to suggest it's time to wrap up. This helps parents manage screen time before bed without abruptly interrupting the story.

**Why this priority**: The timer is a nice-to-have polish feature. It provides gentle time awareness but is not essential to the core bedtime story experience.

**Independent Test**: Can be tested by starting a bedtime story and verifying a timer appears, counts up, and visually indicates when 5 minutes have elapsed.

**Acceptance Scenarios**:

1. **Given** a bedtime mode story, **When** a scene page loads, **Then** a small timer is visible showing elapsed story time.
2. **Given** a bedtime mode story running for more than 5 minutes, **When** the timer reaches 5 minutes, **Then** the timer visually changes (gentle pulse or color shift) to indicate wind-down time.
3. **Given** a non-bedtime story, **When** a scene page loads, **Then** no timer is displayed.

---

### Edge Cases

- What happens when bedtime mode is toggled on with a long story length selected? The system overrides the length to "short" (target depth 3) regardless of what the user selected, since bedtime stories should always be brief.
- What happens when "Keep Going" is clicked during a bedtime story? The button still works (extends by 3), but the calming content guidelines remain active. The story stays soothing even if extended.
- What happens when a bedtime story is saved to the gallery? It is saved like any other story. When read from the gallery, the bedtime night theme is NOT applied (gallery reader uses its own styling).
- What happens if the user starts a bedtime story and then goes back to home? The home page shows the normal kids theme. Bedtime theme only applies to active bedtime story scenes.
- What happens with TTS during bedtime mode? TTS works normally with the existing kids voice settings. The bedtime content guidelines produce calmer text, which naturally sounds more soothing when read aloud.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST display a "Bedtime Mode" toggle on the kids tier home page only.
- **FR-002**: When bedtime mode is enabled, the system MUST use bedtime-specific content guidelines instructing the AI to generate gentle, soothing stories with no tension or conflict, ending with the character settling in for sleep.
- **FR-003**: When bedtime mode is enabled, the system MUST override the story length to "short" (target depth 3) regardless of the user's length selection.
- **FR-004**: When bedtime mode is enabled, the system MUST use a bedtime image style prompt emphasizing soft, warm, cozy, nighttime imagery.
- **FR-005**: The bedtime mode setting MUST be stored on the story so that subsequent scene generations maintain the calming guidelines throughout the session.
- **FR-006**: When bedtime mode is enabled, scene pages MUST render with a warm, dimmed night theme (dark background, soft amber accents, reduced visual brightness).
- **FR-007**: The bedtime night theme MUST only apply to active story scene pages during a bedtime mode session — not to the home page, gallery, or gallery reader.
- **FR-008**: A wind-down timer MUST appear on bedtime mode scene pages, showing elapsed time since the story started.
- **FR-009**: The wind-down timer MUST visually indicate when 5 minutes have elapsed (gentle pulse or color change).
- **FR-010**: The "Surprise Me" button MUST respect bedtime mode — if the toggle is on, the surprise story uses bedtime content guidelines and short length.
- **FR-011**: The bedtime mode toggle MUST NOT appear on the NSFW tier.
- **FR-012**: Bedtime mode stories MUST work with all existing features (TTS, Keep Going, Wrap It Up, custom choices) without breaking them.

### Key Entities

- **Bedtime mode flag**: A boolean attribute on the story indicating whether bedtime content guidelines and theme are active for this session. Persisted with the story data.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Parents can start a calming bedtime story with a single toggle and one click.
- **SC-002**: Bedtime stories consistently end with a sleep-themed conclusion within 3 scenes.
- **SC-003**: The bedtime night theme creates a visually distinct, dimmed experience compared to the normal kids theme.
- **SC-004**: The wind-down timer accurately tracks elapsed story time and signals at the 5-minute mark.

## Assumptions

- The bedtime content guidelines are additive — they are appended to the existing kids content guidelines rather than replacing them. This ensures kid-safe rules remain in effect.
- A target depth of 3 (same as "short") is appropriate for bedtime stories. Parents can still use "Keep Going" if the child wants more.
- The bedtime night theme is a CSS variation applied via a class on the body element, similar to how the kids/adult themes work.
- The wind-down timer is a simple client-side countdown that starts when the first scene loads. It does not require server-side time tracking.
- The bedtime image style overrides the normal kids image style to produce warmer, softer imagery (moonlight, stars, cozy blankets, nighttime scenes).

## Scope

### In Scope

- Bedtime mode toggle on kids home page
- Bedtime-specific content guidelines for the AI
- Bedtime-specific image style for scene illustrations
- Bedtime night theme (CSS color scheme) on scene pages
- Wind-down timer on bedtime mode scene pages
- Override story length to short when bedtime mode is active
- Bedtime mode flag persisted on story model
- Surprise Me respects bedtime mode

### Out of Scope

- Bedtime mode on NSFW tier
- Scheduled bedtime (auto-activating at a set time)
- Sleep sounds or ambient audio (separate backlog feature)
- Bedtime story templates (could be added later as a follow-up)
- Auto-dimming device screen brightness (beyond CSS control)
