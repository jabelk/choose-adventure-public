# Feature Specification: Cover Art Generator

**Feature Branch**: `045-cover-art-generator`
**Created**: 2026-02-08
**Status**: Draft
**Input**: User description: "AI-generated book cover for each completed story in the gallery. Stylized title, illustration, author name. Generated on story completion, displayed as gallery thumbnail."

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Cover Art on Story Completion (Priority: P1)

When a story reaches its ending and is saved to the gallery, the system automatically generates a book-cover-style image that represents the story's theme. The cover art becomes the gallery thumbnail, replacing the generic first-scene image. This makes the gallery feel like a real bookshelf of stories the user has created.

**Why this priority**: The core value of this feature — every completed story gets a polished, book-like visual identity in the gallery.

**Independent Test**: Complete a story in any tier, navigate to the gallery, and verify the story card shows a cover art image (not the first scene image). The cover should visually reflect the story's theme, genre, and tone.

**Acceptance Scenarios**:

1. **Given** a story reaches its ending scene, **When** the story is saved to the gallery, **Then** a cover art image is generated asynchronously and stored with the saved story
2. **Given** a completed story with cover art, **When** the user views the gallery, **Then** the story card shows the cover art as its thumbnail
3. **Given** a story using a specific art style (e.g., watercolor, anime), **When** cover art is generated, **Then** the cover image matches that art style
4. **Given** cover art generation fails (API error, content refusal), **When** the user views the gallery, **Then** the first scene's image is shown as a fallback thumbnail
5. **Given** the cover art is still generating, **When** the user views the gallery, **Then** the first scene image is shown temporarily and the cover replaces it once ready

---

### User Story 2 — Tier-Appropriate Cover Styling (Priority: P2)

Each tier's covers match the audience and aesthetic. Kids tier covers look like colorful children's book covers with the child's name as author ("by Emma, age 5"). Bible tier covers have a reverent, storybook-Bible feel. NSFW tier covers have a mature, stylized aesthetic. The cover prompt adapts to the tier's visual language.

**Why this priority**: Ensures the gallery feels polished and cohesive within each tier, reinforcing the audience-specific experience.

**Independent Test**: Complete stories across kids, bible, and NSFW tiers. Verify each tier's gallery shows covers with visually distinct, audience-appropriate styling.

**Acceptance Scenarios**:

1. **Given** a kids tier story completes, **When** cover art is generated, **Then** the cover uses bright, child-friendly illustration style
2. **Given** a bible tier story completes, **When** cover art is generated, **Then** the cover uses a warm, reverent illustration style
3. **Given** an NSFW tier story completes, **When** cover art is generated, **Then** the cover uses a mature, stylized aesthetic appropriate to the content
4. **Given** a user has an active profile with a name (e.g., "Emma, age 5"), **When** cover art prompt is built, **Then** the author attribution reflects the profile name

---

### User Story 3 — Regenerate Cover Art (Priority: P3)

If a user doesn't like the generated cover, they can regenerate it from the gallery detail view. This gives users agency over their story's visual identity without requiring them to redo the whole story.

**Why this priority**: Nice-to-have polish that improves user satisfaction but isn't essential for the core experience.

**Independent Test**: View a completed story in the gallery, click a "Regenerate Cover" button, and verify a new cover image is generated and replaces the old one.

**Acceptance Scenarios**:

1. **Given** a completed story with cover art in the gallery, **When** the user clicks "Regenerate Cover", **Then** a new cover image is generated and replaces the previous one
2. **Given** a cover regeneration is in progress, **When** the user views the gallery, **Then** the previous cover is shown until the new one is ready

---

### Edge Cases

- What happens when the story has no scene images at all (all failed)? The gallery card shows a placeholder/generic cover.
- What happens when the image model used for the story is no longer available? Fall back to the default image model for the tier.
- What happens with very short story titles (1-2 words) or very long titles (20+ words)? The cover prompt handles both gracefully — short titles get prominent placement, long titles are summarized.
- What happens with existing gallery stories that were saved before this feature? They continue showing first-scene images; covers are only generated for newly completed stories.
- What happens if the user completes the story but the gallery save itself fails? No cover is generated — cover generation is dependent on successful gallery save.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST generate a cover art image when a story is saved to the gallery upon completion
- **FR-002**: System MUST generate cover art asynchronously so the gallery save is not blocked or delayed
- **FR-003**: The cover art prompt MUST incorporate the story's title, theme/genre (derived from the original prompt), and overall tone
- **FR-004**: The cover art prompt MUST respect the story's selected art style, if one was chosen
- **FR-005**: The cover art MUST be generated using the same image model the story used
- **FR-006**: System MUST store the cover art image URL on the saved story record
- **FR-007**: The gallery MUST display cover art as the story thumbnail when available, falling back to the first scene image when cover art is not available or still generating
- **FR-008**: Cover art prompts MUST be tier-appropriate — kids tier uses child-friendly illustration style, bible tier uses reverent storybook style, NSFW tier uses mature stylized aesthetic
- **FR-009**: Cover art prompts MUST include author attribution context — profile name if available (e.g., "by Emma, age 5" for kids), omitted if no profile is active
- **FR-010**: System MUST handle cover art generation failures gracefully with no user-visible error — the gallery simply shows the first scene image as fallback
- **FR-011**: Users MUST be able to regenerate cover art for a completed story from the gallery
- **FR-012**: Cover art image prompts MUST NOT include any text, words, or lettering (text overlay is unreliable in AI image generation; the title/author appear in the gallery card HTML, not burned into the image)

### Key Entities

- **Cover Art Image**: A generated image associated with a SavedStory. Attributes: image URL, generation status (pending/complete/failed), the prompt used to generate it. Stored alongside the existing SavedStory record.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of newly completed stories saved to the gallery trigger cover art generation
- **SC-002**: Gallery page loads within the same timeframe as before this feature (cover art is pre-generated, not on-demand)
- **SC-003**: Cover art is visually distinct from scene images — it reads as a "book cover" rather than a scene illustration
- **SC-004**: Gallery cards with cover art are visually identifiable as having a cohesive, polished thumbnail
- **SC-005**: Cover art generation failure does not prevent or delay the story from appearing in the gallery

## Assumptions

- Title and author text will be rendered in the gallery card HTML (overlaid via CSS), not burned into the AI-generated image. AI image generators are unreliable at rendering text.
- The cover art prompt will be built from the story's original prompt, title, and tier context — not from individual scene content (keeps it simple and fast).
- Existing gallery stories saved before this feature will not retroactively receive cover art unless the user explicitly regenerates.
- Author attribution is derived from the active memory-mode profile at the time of story completion. If no profile is active, no author name is shown.
