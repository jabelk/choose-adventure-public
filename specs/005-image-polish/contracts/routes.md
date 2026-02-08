# Route Contracts: Image Retry & Polish

## New Routes

### POST `/{tier}/story/image/{scene_id}/retry`

**Purpose**: Retry a failed image or regenerate an existing one.

**Request**: No body (triggered by button click via fetch).

**Behavior**:
1. Load the story session from the in-memory store
2. Find the scene and its Image object
3. If image status is GENERATING, return `{"status": "generating"}` (no-op)
4. Reset image: status → PENDING, url → None, error → None
5. Start a new background generation task
6. Save progress to disk
7. Return `{"status": "generating"}`

**Response**: JSON `{"status": "generating"}` on success, `{"status": "failed"}` if scene not found.

**Error handling**: If no session or scene found, return `{"status": "failed"}`.

## Modified Routes

### GET `/{tier}/story/image/{scene_id}` (existing)

**No changes needed.** Already returns the current image status as JSON. The polling client already handles all three states (complete, generating, failed).

### GET `/{tier}/story/scene/{scene_id}` (existing)

**No changes needed.** The template changes (scene.html) handle the new UI states. The route just passes the scene data to the template as before.

## Client-Side Contracts

### `retryImage(sceneId)` (new JS function)

**Purpose**: Called when user clicks Retry or Regenerate button.

**Behavior**:
1. POST to `/{tier}/story/image/{sceneId}/retry`
2. On success response, show generating placeholder
3. Start polling with `pollImageStatus(sceneId)`

### `pollImageStatus(sceneId)` (modified JS function)

**Changes**:
- On failure, call `showFailedState(container, sceneId)` instead of `showFallback(container)`
- `showFailedState` renders error message + retry button
- Retry button calls `retryImage(sceneId)`
