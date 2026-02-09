# Research: Story Recap / "Previously On..."

## R1: Scene Navigation Path Tracking

`StorySession.path_history: list[str]` stores the ordered list of scene IDs along the user's current navigation path. `StorySession.get_full_context()` returns the corresponding `Scene` objects in order — this is the same method used to build AI context for generating the next scene. Each `Scene` has `.content` (the narrative text), `.depth` (0-based scene number), and `.parent_scene_id`.

When the user goes back, `navigate_backward()` removes the last scene ID from `path_history`. When they choose a different branch, `navigate_forward()` appends the new scene. This means `path_history` always reflects the current navigation path, not all explored branches.

## R2: AI Text Generation for Recap

The `StoryService` in `app/services/story.py` has a `_call_provider(model, system, messages)` dispatcher that routes to Claude, GPT, Gemini, or Grok based on the story's configured model. Each provider method accepts a system prompt string and a messages list, returning raw text.

For recap generation, we can call the same provider with a recap-specific system prompt. The `tier_config.content_guidelines` parameter controls language/tone (kids vocabulary, NSFW permissiveness, Bible reverence), which should be included in the recap prompt.

**Decision**: Use the existing `StoryService._call_provider()` method for recap generation. No new service needed.
**Rationale**: Keeps the recap on the same model the story uses, ensuring consistent voice. Avoids introducing a new AI service class.
**Alternatives considered**: Dedicated RecapService (rejected — unnecessary abstraction for a simple text call).

## R3: Resume Detection

There is currently **no mechanism** to detect whether a user is resuming a story vs. actively playing. The `resume_story()` route at line 1539 of `routes.py` loads the session from disk and redirects to the current scene — indistinguishable from normal scene navigation from the scene view handler's perspective.

**Decision**: Add a query parameter `?resumed=1` to the redirect URL in the resume route. The scene view handler checks for this parameter. This avoids adding persistent state to the model for a transient signal.
**Rationale**: A query parameter is the simplest approach — no model changes, no session mutation, automatically clears on next navigation.
**Alternatives considered**: (a) `is_resume` field on StorySession (rejected — persists unnecessarily, must be manually cleared), (b) time-based detection comparing last activity timestamp (rejected — complex, unreliable).

## R4: Scene Page Template Context

The `view_scene` handler at lines 980-1030 of `routes.py` passes a rich context to `scene.html` via the `_ctx()` helper. Key variables: `story`, `scene`, `tier`, `url_prefix`, `bedtime_mode`, `has_reference_images`. Adding `recap_text`, `recap_expanded`, and `show_recap` is straightforward.

## R5: Async Recap Loading Strategy

The spec requires the scene page to load immediately without waiting for recap generation. Two approaches:

**Decision**: Server-side async with AJAX fetch. The scene page renders immediately with a placeholder. JavaScript fetches the recap from a dedicated endpoint. The endpoint returns cached text instantly or generates it on-demand.
**Rationale**: Consistent with existing patterns in the codebase (image polling, TTS loading). No page load delay. Cache check is fast.
**Alternatives considered**: (a) Pre-generate recap during scene transition (rejected — adds latency to choice submission), (b) WebSocket push (rejected — overengineered for this use case).

## R6: Recap Caching Strategy

**Decision**: Store cached recaps as a dict on the `StorySession` model: `recap_cache: dict[str, str]` mapping a cache key to recap text. The cache key is a hash of the `path_history` up to the current scene (e.g., `"|".join(path_history[:depth+1])`), so it invalidates automatically when the path changes (user goes back and takes a different branch).
**Rationale**: Session-scoped, no disk persistence needed. Invalidation is automatic via the path-based key. Zero new infrastructure.
**Alternatives considered**: (a) Per-scene-id cache without path awareness (rejected — stale after branch changes), (b) Disk-persisted cache (rejected — unnecessary for a convenience feature).

## R7: Recap Prompt Design

The recap prompt should:
1. Include all scene content along the current path
2. Request a 2-3 sentence summary (up to 4 for 10+ scene stories)
3. Include tier content guidelines for appropriate language
4. Instruct the AI to summarize events without spoiling choices

Example system prompt structure:
```
Summarize the story so far in 2-3 short sentences. {tier_guidelines}
Write in the same tone and voice as the story.
Do not mention choices or what might happen next.
```
