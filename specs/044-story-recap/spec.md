# Feature Specification: Story Recap / "Previously On..."

**Feature Branch**: `044-story-recap`
**Created**: 2026-02-08
**Status**: Draft
**Input**: User description: "Story Recap / 'Previously On...' — AI-generated summary of the story so far, shown when resuming or continuing longer stories. Works across all tiers."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - "Story So Far" Recap Section (Priority: P1)

A single collapsible "Story so far" section appears on scene pages at scene 2 or later. On resume (returning to a story after leaving), the section starts **expanded** so the user immediately sees the recap. During active play, the section starts **collapsed** so it doesn't interrupt the flow — but users can expand it anytime to refresh their memory.

This is especially valuable for kids who started a story yesterday and come back today — they immediately remember what happened without re-reading every scene. It also helps during longer stories (5+ scenes) where earlier plot points become relevant again.

**Why this priority**: This is the core feature. A single UI element that adapts its initial state (expanded vs. collapsed) covers both the resume use case and the mid-story reference use case without cluttering the page with two separate recap widgets.

**Independent Test**: Start a story, progress through 3+ scenes, leave the app. Return and resume the story. Verify the recap section appears expanded with a 2-3 sentence summary. Then start a new scene from an active story and verify the recap section is present but collapsed.

**Acceptance Scenarios**:

1. **Given** a story at scene 2 or later, **When** the user resumes the story from the gallery or home page, **Then** the "Story so far" section appears **expanded** at the top of the scene page with a 2-3 sentence summary
2. **Given** a story at scene 2 or later during active play, **When** the user navigates to the next scene, **Then** the "Story so far" section appears **collapsed** (toggle visible, content hidden)
3. **Given** a story at scene 1 (the very first scene), **When** the user views the scene, **Then** no recap section is shown (nothing to recap yet)
4. **Given** a collapsed recap section, **When** the user taps/clicks the toggle, **Then** it expands to show the recap text (loaded from cache or generated within 2 seconds)
5. **Given** an expanded recap section, **When** the user taps/clicks the toggle, **Then** it collapses and hides the recap text
6. **Given** a story with a recap already generated for a specific scene, **When** the user returns to that scene again, **Then** the cached recap is shown immediately without regenerating it

---

### User Story 3 - Tier-Appropriate Recap Language (Priority: P3)

Recaps adapt their language and tone to match the tier. Kids tier recaps use simple vocabulary suitable for ages 3-6. NSFW tier recaps maintain the story's tone and can reference mature content. Bible tier recaps incorporate reverent, age-appropriate language. This ensures the recap feels like a natural part of the story experience rather than a jarring system message.

**Why this priority**: Polish feature. The recap is functional without tier-specific language tuning, but matching the tier's voice makes it feel more integrated and delightful.

**Independent Test**: Start stories in each tier (kids, nsfw, bible), progress through 3+ scenes, and verify the recap language matches the tier's content style and vocabulary level.

**Acceptance Scenarios**:

1. **Given** a kids tier story at scene 3+, **When** a recap is generated, **Then** it uses simple words and short sentences appropriate for ages 3-6
2. **Given** an NSFW tier story at scene 3+, **When** a recap is generated, **Then** it preserves the story's tone and maturity level
3. **Given** a Bible tier story at scene 3+, **When** a recap is generated, **Then** it uses warm, reverent language matching the tier's voice

---

### Edge Cases

- What happens when the AI text model is unreachable? The recap section should show a gracefully degraded state (e.g., hidden or "Recap unavailable") rather than blocking the page or showing an error.
- What happens when a story has only 1 scene? No recap is shown — there isn't enough content to summarize.
- What happens when a story branches and the user goes back to explore a different path? The recap should summarize the current path (scenes along the active navigation history), not all branches.
- What happens when the recap generation takes too long? The scene page should load immediately with the recap loading asynchronously. The page is never blocked waiting for a recap.
- What happens when the cached recap becomes stale (user went back and took a different path)? The cache should be invalidated when the navigation path changes, and a fresh recap generated.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST generate a 2-3 sentence summary of the story so far using the story's configured text model
- **FR-002**: System MUST display a single collapsible "Story so far" section on scene pages at scene 2 or later
- **FR-003**: System MUST auto-expand the recap section when the user is resuming a story (returning after leaving), and keep it collapsed during active play
- **FR-004**: System MUST cache generated recaps per scene so they are not regenerated on every page load
- **FR-005**: System MUST load the scene page immediately without waiting for recap generation — recaps load asynchronously
- **FR-006**: System MUST allow users to dismiss/collapse the recap so it does not obstruct the current scene content
- **FR-007**: System MUST adapt recap language to match the tier's content guidelines and vocabulary level
- **FR-008**: System MUST summarize only the scenes along the current navigation path, not all explored branches
- **FR-009**: System MUST gracefully handle AI model unavailability without blocking the scene page
- **FR-010**: System MUST invalidate cached recaps when the user's navigation path changes (e.g., going back and taking a different branch)
- **FR-011**: System MUST work across all tiers (kids, nsfw, bible)

### Key Entities

- **Story Recap**: A short AI-generated text summary of the story's events up to a specific scene. Attributes: the recap text, the scene it was generated for, the path of scene IDs it summarizes
- **Recap Cache**: Per-scene storage of generated recaps to avoid redundant AI calls. Keyed by scene ID and the navigation path taken to reach that scene

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users resuming a story see a meaningful recap within 3 seconds of the page loading
- **SC-002**: Cached recaps display instantly (under 500ms perceived load time) on subsequent visits to the same scene
- **SC-003**: Recap generation adds no delay to the scene page's initial render — the page loads at the same speed with or without the recap feature
- **SC-004**: Recaps accurately reflect the events of the story along the current path without spoiling upcoming choices
- **SC-005**: The feature works identically across all three tiers (kids, nsfw, bible) with tier-appropriate language

## Clarifications

### Session 2026-02-08

- Q: Should the resume recap (US1) and the "Story so far" toggle (US2) be the same UI element or two separate ones? → A: Single collapsible section — auto-expanded on resume, collapsed by default during active play.
- Q: What is the minimum scene depth for showing the recap section? → A: Scene 2+ (show whenever there's at least 1 prior scene to recap).

## Assumptions

- The story's configured text model is available for recap generation (same model used for story content)
- Scene content is accessible in memory during the active session for building the recap prompt
- Recap caching is session-scoped (in-memory) — recaps don't need to persist across server restarts
- A 2-3 sentence recap is sufficient for stories up to ~20 scenes; longer stories may need slightly longer recaps (up to 4 sentences)
- The recap is a convenience feature, not a critical one — graceful degradation is acceptable
