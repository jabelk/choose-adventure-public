# Research: Chapter Stories

## R1. How existing depth/pacing system works

**Decision**: Extend, don't replace. The existing `depth` field and `target_depth` pacing system naturally support longer stories.

**Rationale**: Scene generation already uses `remaining = target_depth - current_depth` to determine pacing. The AI is told "Current chapter: N of M" and given pacing instructions. Setting `target_depth=25` makes the AI generate 25 scenes with the same logic. Context truncation (`_summarize_long_context()`) already handles long story histories.

**Alternatives considered**: New pacing system with chapter-level tracking — rejected because the existing system works perfectly for variable lengths.

## R2. Chapter boundary detection

**Decision**: Use `depth % scenes_per_chapter == 0` where `scenes_per_chapter=5` for epic stories. Chapter 1 starts at depth 0, Chapter 2 at depth 5, etc.

**Rationale**: Simple arithmetic, no state tracking needed. Works for any number of chapters. The constant `5` can be derived from `target_depth // num_chapters`.

**Alternatives considered**: AI self-reports chapter transitions — rejected because AI output is unpredictable and we need deterministic chapter boundaries for the UI.

## R3. Chapter title generation

**Decision**: Ask the AI to include a `chapter_title` field in its JSON response when the scene is the first of a new chapter. The route handler sets `is_chapter_start=True` in the prompt context when `depth % 5 == 0`.

**Rationale**: The AI already generates a `title` for each scene. Adding `chapter_title` only at chapter boundaries keeps the output format simple. The prompt says "This is the start of Chapter N. Include a chapter_title."

**Alternatives considered**: Pre-generate all chapter titles at story start — rejected because the AI hasn't written the story yet and can't title future chapters meaningfully.

## R4. Progress save coexistence

**Decision**: Separate file for chapter stories: `data/progress/{tier}_chapter.json`. Reuse the same `GalleryService` methods with a `suffix` parameter.

**Rationale**: The existing `save_progress(tier_name)` writes to `{tier_name}.json`. Adding `save_progress(tier_name, suffix="_chapter")` writes to `{tier_name}_chapter.json`. Minimal code change, no migration needed.

**Alternatives considered**: Single progress file with array of saves — more complex, requires migration of existing single-file format.

## R5. AI context window management for 25-scene stories

**Decision**: Rely on existing `_summarize_long_context()` in `story.py`. It keeps the last 2 scenes verbatim and summarizes earlier scenes when context exceeds 4,000 characters.

**Rationale**: Already proven to work for 7-scene long stories. Will work the same for 25 scenes — just more summarization. The recap system (spec 044) also provides story-so-far context.

**Alternatives considered**: Chapter-level context (only send current chapter's scenes) — rejected because the AI needs overarching plot awareness.

## R6. Template changes for chapter title cards

**Decision**: Add a chapter title card section in `scene.html` and `reader.html` that renders ABOVE the scene content when `scene.chapter_number` and `scene.chapter_title` are set. Styled as a full-width banner with chapter number and title.

**Rationale**: Non-invasive template change. Falls through cleanly when fields are None (regular stories). Consistent between play and gallery reader.

## R7. Interaction with existing features

**Decision**: Chapter stories are compatible with all existing features:
- **Cover art** (045): Works — generated on story completion as usual
- **Story recap** (044): Works — recap summarizes all scenes regardless of chapter structure
- **Keep Going / Wrap Up** (025): Works — these adjust `target_depth`, which is just a number
- **Art style**: Works — stored on Story, applied to all scene images
- **Bedtime mode**: Works — compatible with any story length
- **Picture book mode**: Works — extra images generated per scene as usual
- **Video mode**: Works — video generated per scene as usual

No feature conflicts identified.
