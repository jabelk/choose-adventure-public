# Research: Story Sequel Mode

## Decision 1: Sequel Context Strategy

**Decision**: Pass only the last scene's content as sequel context, not the full story history.

**Rationale**: The AI models have context limits. A full story with 5-7 scenes could be 3000-5000 tokens of context. The last scene alone captures the ending state, characters in their final situation, and the emotional tone — which is all the AI needs to write a meaningful continuation.

**Alternatives considered**:
- Full story history: Too much context, wastes tokens, could confuse the AI with mid-story plot points that were resolved.
- Last 2-3 scenes: Slightly better context but diminishing returns — the ending scene is the critical one.
- Summary of the full story: Would require an extra AI call to summarize, adding latency and complexity.

## Decision 2: Field Carryover from SavedStory

**Decision**: Fix `gallery.save_story()` to persist all Story fields to SavedStory, then copy those fields when creating a sequel.

**Rationale**: The current `save_story()` drops several fields: `art_style`, `protagonist_gender`, `protagonist_age`, `character_type`, `num_characters`, `writing_style`, `conflict_type`, `roster_character_ids`, `bedtime_mode`, `parent_story_id`. These fields exist on the `SavedStory` model with defaults but are never set during save. Fixing this is a prerequisite for sequel mode and also a standalone bug fix that benefits gallery display.

**Fields to carry over in sequel**: `character_name`, `character_description`, `kinks`, `conflict_type`, `writing_style`, `art_style`, `model`, `image_model`, `roster_character_ids`, `protagonist_gender`, `protagonist_age`, `character_type`, `num_characters`.

**Fields NOT carried over**: `bedtime_mode` (session toggle), `video_mode` (session toggle), `profile_id` (profiles are for new stories), `reference_photo_paths` (tied to upload session).

## Decision 3: Route Design for P1 vs P2

**Decision**: For P1 (MVP), the "Continue Story" button directly POSTs to create the sequel. For P2, the button becomes a link to a GET customization page, which then POSTs to create the sequel.

**Rationale**: P1 should be one click — instant gratification. P2 adds a customization step but is independently implementable by changing the button target. The POST route for actually creating the sequel is the same in both cases.

**Route layout**:
- P1: `POST /gallery/{story_id}/continue` — creates sequel immediately with inherited settings
- P2: `GET /gallery/{story_id}/continue` — shows customization form pre-filled with original settings
- P2: `POST /gallery/{story_id}/continue` — creates sequel with (possibly modified) settings from form

## Decision 4: Forward Reference Updates (P3)

**Decision**: When a sequel is saved to the gallery via `save_story()`, check if `parent_story_id` is set and update the parent story's JSON file to add the sequel's ID to its `sequel_story_ids` list.

**Rationale**: Forward references (parent knows about its sequels) enable the "Continued in: [title]" link on the reader page. Without this, we'd need to scan all stories to find sequels, which is O(n) per page load.

**Alternatives considered**:
- Scan all stories at gallery list time: Simple but slow for large galleries.
- Separate index file: Over-engineered for a single-user hobby app.
- Only backward references (sequel → parent): Simpler but can't show "Continued in" on the original.

## Decision 5: Sequel Prompt Injection into AI Context

**Decision**: Construct a sequel-specific system prompt that includes: (1) the original ending scene content, (2) an optional user-provided sequel direction hint, and (3) an instruction to continue the narrative.

**Rationale**: The AI needs clear instructions to write a continuation rather than starting fresh. The prompt structure:

```
SEQUEL CONTEXT:
This is a sequel to a previous story. Here is how the previous story ended:

---
[Last scene content]
---

[Optional: The user wants the sequel to go in this direction: "[sequel prompt]"]

Continue the narrative from this point. Start a new chapter in the same world with the same characters. Reference events from the ending above but introduce a new plot thread.
```

This goes into `content_guidelines` alongside the tier guidelines, character blocks, and kink prompts — same pattern as all other guideline additions.
