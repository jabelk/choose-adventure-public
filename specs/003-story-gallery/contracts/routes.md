# Route Contracts: Story Gallery

All gallery routes are added inside `create_tier_router()` and inherit the tier prefix.

## New Routes

### GET /{tier}/gallery

**Purpose**: Display the gallery listing page for a tier.

**Response**: HTML page showing all completed stories for this tier as cards.

**Template context**:
- `tier` — TierConfig object
- `url_prefix` — tier URL prefix string
- `stories` — list of SavedStory objects, sorted newest first

**Behavior**:
- Loads all saved stories for the current tier from disk
- Sorts by `completed_at` descending
- Renders `gallery.html` template
- If no stories, shows empty state message

---

### GET /{tier}/gallery/{story_id}

**Purpose**: Redirect to the first scene of a saved story in the reader.

**Response**: 303 redirect to `/{tier}/gallery/{story_id}/0`

**Behavior**:
- Validates story_id exists and belongs to this tier
- If not found, redirects to `/{tier}/gallery`

---

### GET /{tier}/gallery/{story_id}/{scene_index}

**Purpose**: Display a specific scene of a saved story in read-only mode.

**Path parameters**:
- `story_id` — UUID of the saved story
- `scene_index` — 0-based integer index into path_history

**Response**: HTML page showing the scene text, image, and navigation.

**Template context**:
- `tier` — TierConfig object
- `url_prefix` — tier URL prefix string
- `story` — SavedStory object
- `scene` — SavedScene object at the given index
- `scene_index` — current index (int)
- `total_scenes` — length of path_history
- `has_next` — boolean, whether there's a next scene
- `has_prev` — boolean, whether there's a previous scene

**Behavior**:
- Loads the saved story from disk
- Validates tier matches
- Validates scene_index is within bounds of path_history
- If invalid, redirects to `/{tier}/gallery`

## Modified Routes

### POST /{tier}/story/choose/{scene_id}/{choice_id}

**Modification**: After generating an ending scene (`is_ending=true`), automatically save the completed story to disk via GalleryService.

## New Templates

### gallery.html
- Extends base.html
- Shows grid/list of story cards
- Each card: title, first scene image thumbnail, prompt excerpt, date
- Cards link to `/{tier}/gallery/{story_id}`
- Empty state when no stories

### reader.html
- Extends base.html
- Scene text and image display (similar to scene.html but read-only)
- Previous/Next navigation buttons
- "Back to Gallery" link
- Chapter indicator (e.g., "Chapter 2 of 5")

## Modified Templates

### home.html
- Add "Gallery" link in the header area or below the form
