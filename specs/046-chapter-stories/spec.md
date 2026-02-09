# Feature Specification: Chapter Stories

**Feature Branch**: `046-chapter-stories`
**Created**: 2026-02-08
**Status**: Draft
**Input**: User description: "Multi-session long-form stories with chapter breaks. Save progress between chapters. 20+ scenes organized into chapters of 4-5 scenes each. Chapter title cards. 'Continue Chapter 3' on home page."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Start and Play a Chapter Story (Priority: P1)

A user selects the new "Epic" story length option on the home page. The system generates a long-form story organized into chapters. Each chapter consists of 4-5 scenes with choices, and a chapter title card is displayed at the start of each new chapter. The story spans approximately 5 chapters (~20-25 scenes total). The user plays through chapter by chapter, with each chapter feeling like a self-contained narrative arc within the larger story.

**Why this priority**: This is the core feature — without multi-chapter story generation and chapter title cards, nothing else works.

**Independent Test**: Select "Epic" length, start a story, and verify the story generates chapter title cards at chapter boundaries, each chapter has 4-5 scenes, and the overall story progresses through multiple chapters with a coherent overarching narrative.

**Acceptance Scenarios**:

1. **Given** the home page, **When** the user selects "Epic" story length, **Then** a new length option appears with description indicating multi-chapter format (~5 chapters)
2. **Given** an epic story in progress, **When** the user completes 4-5 scenes, **Then** a chapter title card is displayed showing the next chapter's name/number before the next scene
3. **Given** an epic story in progress, **When** the user reaches the final chapter's ending, **Then** the story concludes naturally and is saved to the gallery as a complete multi-chapter story
4. **Given** any tier (kids, bible, nsfw), **When** the user starts an epic story, **Then** chapter content and tone match the tier's content guidelines

---

### User Story 2 - Save and Resume Between Chapters (Priority: P2)

A user playing a chapter story can close their browser at any point and return later to continue. The home page shows a "Continue Chapter N" prompt so the user knows where they left off and can pick up immediately. Progress is saved automatically at each scene.

**Why this priority**: Multi-session play is essential for 20+ scene stories — users won't finish in one sitting. Without save/resume, the "epic" length is impractical.

**Independent Test**: Start an epic story, play through 1-2 chapters, close the browser, reopen the home page, and verify a "Continue Chapter N" prompt appears that resumes the story at the correct scene.

**Acceptance Scenarios**:

1. **Given** an epic story in progress, **When** the user navigates away or closes the browser, **Then** progress is automatically saved
2. **Given** a saved chapter story, **When** the user visits the home page, **Then** a "Continue Chapter N" banner/button is displayed with the story title and current chapter number
3. **Given** the continue prompt, **When** the user clicks it, **Then** the story resumes at the exact scene where they left off
4. **Given** a saved chapter story, **When** the user starts a brand new story instead, **Then** the previous chapter story progress is preserved (not overwritten) and the continue prompt remains available

---

### User Story 3 - View Completed Chapter Stories in Gallery (Priority: P3)

Completed chapter stories appear in the gallery with all chapters visible. The reader view organizes scenes by chapter, and the gallery card indicates the story is a multi-chapter story. Users can navigate between chapters in the reader.

**Why this priority**: Gallery integration ensures chapter stories are archivable and re-readable, consistent with the project's Archival by Design principle.

**Independent Test**: Complete a full chapter story, navigate to the gallery, and verify the story displays with chapter organization in the reader, and the gallery card shows it's a multi-chapter story.

**Acceptance Scenarios**:

1. **Given** a completed chapter story, **When** viewing the gallery, **Then** the story card indicates it is a multi-chapter story (e.g., "5 Chapters")
2. **Given** a completed chapter story in the reader, **When** navigating scenes, **Then** chapter title cards appear between chapters just as they did during play
3. **Given** a completed chapter story in the reader, **When** the user wants to jump to a specific chapter, **Then** they can navigate directly to any chapter start

---

### Edge Cases

- What happens if the user abandons a chapter story mid-chapter (not at a chapter break)? Progress should still be saved at the last completed scene, resumable from that point.
- What happens if image generation fails during a chapter title card? The chapter title card should display without an image (text-only is acceptable).
- What happens if the user has an in-progress regular story AND an in-progress chapter story? Both should be independently resumable — the existing resume system handles regular stories, chapter stories use their own save slot.
- What happens if the AI generates a chapter ending too early (scene 2 of a chapter)? The system should guide the AI to maintain 4-5 scenes per chapter via prompt instructions.
- What happens if the user wants to quit a chapter story permanently? There should be a way to abandon the in-progress chapter story, clearing the continue prompt.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST add an "Epic" story length option (~5 chapters, ~20-25 scenes) alongside the existing short/medium/long options
- **FR-002**: System MUST generate chapter title cards at the transition between chapters, displaying the chapter number and a narrative chapter title
- **FR-003**: Each chapter MUST contain approximately 4-5 scenes with choices, forming a mini narrative arc within the larger story
- **FR-004**: The AI MUST be prompted to structure the story into chapters with an overarching narrative that progresses across chapters while each chapter has its own tension and resolution
- **FR-005**: System MUST automatically save story progress at each scene so the user can resume later
- **FR-006**: The home page MUST display a "Continue Chapter N" prompt when a chapter story is in progress, showing the story title and current chapter number
- **FR-007**: Users MUST be able to resume a chapter story from the continue prompt, returning to the exact scene where they left off
- **FR-008**: The continue prompt MUST NOT interfere with the existing story resume functionality for regular-length stories
- **FR-009**: Completed chapter stories MUST be saved to the gallery with chapter metadata preserved
- **FR-010**: The gallery reader MUST display chapter title cards between chapters, matching the play experience
- **FR-011**: The gallery card MUST indicate when a story is a multi-chapter story (e.g., showing chapter count)
- **FR-012**: Chapter stories MUST work across all tiers (kids, bible, nsfw) with tier-appropriate content and styling
- **FR-013**: Users MUST be able to abandon an in-progress chapter story to clear the continue prompt
- **FR-014**: The chapter title card MUST be visually distinct from regular story scenes — it is a transitional screen, not a playable scene

### Key Entities

- **Chapter**: A grouping of 4-5 consecutive scenes within an epic story, with a chapter number and narrative title. Not a separate data entity — represented by metadata on scenes and title card markers.
- **Chapter Title Card**: A special non-interactive scene displayed between chapters, showing the chapter number and title. Serves as a visual break between narrative arcs.
- **Epic Story**: A story using the "Epic" length setting, consisting of approximately 5 chapters (~20-25 scenes). Uses the same story entities but with higher target depth and chapter metadata.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can start an "Epic" length story and play through 5 chapters with chapter title cards appearing between each chapter
- **SC-002**: Users can close the browser mid-story and return to a "Continue Chapter N" prompt on the home page that resumes at the correct position, with 100% of progress preserved
- **SC-003**: Completed chapter stories display in the gallery with chapter organization, and the reader shows chapter breaks matching the play experience
- **SC-004**: Chapter stories work identically across all 3 tiers (kids, bible, nsfw) with tier-appropriate content and visual styling
- **SC-005**: The existing short/medium/long story flows continue to work without any changes — no regressions

## Assumptions

- The "Epic" length maps to a target depth of approximately 20-25 scenes (5 chapters x 4-5 scenes)
- Chapter titles are AI-generated as part of the story generation, not user-specified
- Chapter title cards do not count as playable scenes — they are transitional display elements
- The existing story progress save system can be extended to support chapter story bookmarks without a new storage mechanism
- One chapter story in progress per tier is sufficient (same constraint as existing regular story resume)
- Cover art generation (spec 045) applies to chapter stories the same as regular stories
