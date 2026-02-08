# Research: Coloring Page Export

## Decision 1: Image Generation Approach

**Decision**: Reuse existing `ImageService` with a new `generate_coloring_page()` method that wraps the prompt with a coloring page style override.

**Rationale**: The existing `generate_image()` already handles multi-model support, retries, content refusal fallbacks, and file saving. A coloring page is just a different prompt style — same API call, same infrastructure.

**Alternatives considered**:
- Post-processing (convert color image to line art via image processing library) — rejected because it produces inferior results compared to generating line art directly, and adds a dependency.
- New service class — rejected because it's the same operation with a different prompt prefix.

## Decision 2: Coloring Page Storage

**Decision**: Save coloring pages as `static/images/{scene_id}_coloring.png` alongside original scene images.

**Rationale**: Follows the existing naming convention (`{scene_id}_extra_0.png`, `{scene_id}_extra_1.png` for picture book mode). No new directories needed. Files are automatically served via FastAPI's static file mounting.

**Alternatives considered**:
- Separate `static/coloring/` directory — rejected as unnecessary directory proliferation.
- Don't persist (generate fresh each time) — rejected because image API calls are slow and costly; caching on disk avoids redundant regeneration.

## Decision 3: Caching Strategy

**Decision**: Check if `{scene_id}_coloring.png` exists on disk before generating. If file exists, return it immediately. If not, generate and save.

**Rationale**: The spec says "not cached or persisted between sessions" but this is better interpreted as "no complex caching layer." Simple file-exists check avoids paying for duplicate API calls for the same scene's coloring page. The file is a natural cache.

**Alternatives considered**:
- No caching (regenerate every time) — rejected because image API calls cost money and take 10-20 seconds. Once generated, there's no reason to regenerate.
- In-memory cache — rejected as unnecessary when the file on disk IS the cache.

## Decision 4: Route Structure

**Decision**: Two GET endpoints under the existing gallery reader URL pattern:
- `GET /gallery/{story_id}/{scene_id}/coloring` — returns JSON with the coloring page URL (or generates it first)
- `GET /gallery/{story_id}/{scene_id}/coloring/pdf` — returns PDF download

**Rationale**: Both routes need to be declared before the catch-all `/{scene_id}` route (same issue fixed in 027-sequel-mode). Using GET makes the endpoints linkable and cacheable. The `/coloring` endpoint returns JSON so the JavaScript can update the UI without a full page reload.

**Alternatives considered**:
- POST for generation — rejected because generation is idempotent (same prompt → same style, and we cache results).
- Single endpoint with format query param — rejected for simplicity; two clear URLs are easier to understand.

## Decision 5: Client-Side UX Pattern

**Decision**: JavaScript fetch to `/coloring` endpoint on button click. Show inline coloring page below the original image with download buttons. No modal.

**Rationale**: Inline display is simpler than a modal and follows the existing pattern for extra images in picture book mode. The coloring page appears in context with the scene it was generated from. Download buttons (PNG, PDF) appear alongside the image.

**Alternatives considered**:
- Full page reload — rejected because it loses scroll position and feels clunky.
- Modal overlay — rejected as over-engineered for a single image display.
