# Route Contracts: Story Branching Explorer

## New Routes

### POST `/{tier}/story/navigate/{scene_id}` (new)

**Purpose**: Navigate the active story to any explored scene in the tree. Used by the tree map click handler.

**Request**: No body. The `scene_id` is in the URL path.

**Behavior**:
1. Look up `scene_id` in `story_session.scenes`
2. If not found, redirect to current scene
3. Rebuild `path_history` by walking from root to `scene_id` via `parent_scene_id` chain
4. Update `story.current_scene_id` to `scene_id`
5. Update session and save progress

**Response**: Redirect to `/{tier}/story/scene/{scene_id}` (303).

### GET `/{tier}/story/tree` (new)

**Purpose**: Return the story tree as JSON for the tree map component. Called via fetch from the client-side tree map.

**Response**: JSON with nested tree structure:
```json
{
  "tree": {
    "id": "scene-uuid",
    "label": "Ch. 1",
    "is_ending": false,
    "is_current": true,
    "on_path": true,
    "choice_text": "",
    "children": [...]
  },
  "current_id": "scene-uuid"
}
```

**Behavior**:
1. Get the story session
2. Build nested tree from `scenes` dict using `parent_scene_id`
3. Mark `is_current` and `on_path` based on `path_history`
4. Return JSON

## Modified Routes

### POST `/{tier}/story/choose/{scene_id}/{choice_id}` (existing)

**Changes**: Already works for branching. When a choice has `next_scene_id` set, it navigates to the existing scene instead of generating. When a choice has no `next_scene_id`, it generates a new scene. No code changes needed.

**Important**: The `get_full_context()` call uses `path_history`, which at the time of choosing will be the path from root to the current choice point. This naturally provides the correct narrative context for the new branch (FR-012).

### GET `/{tier}/story/scene/{scene_id}` (existing)

**Changes**: Pass additional context to the template:
1. `explored_choices`: A set of choice IDs that have `next_scene_id` set (for FR-003 visual indicators)
2. `has_branches`: Boolean — whether the story has more than one leaf (for showing/hiding the tree map toggle)
3. `tree_data`: The nested tree JSON (for inline tree map rendering)

### GET `/{tier}/gallery/{story_id}/{scene_index}` → GET `/{tier}/gallery/{story_id}/{scene_id}` (changed)

**Changes**: Replace integer `scene_index` with string `scene_id` for direct scene access.

**Old behavior**: Look up scene by index into `path_history`.
**New behavior**: Look up scene by ID in `scenes` dict. Pass tree data to template.

**Behavior**:
1. Get the saved story by `story_id`
2. Look up `scene_id` in `saved.scenes`
3. If not found, redirect to gallery
4. Build tree data from the saved story's scenes
5. Pass tree data, current scene, and navigation context to the reader template

### GET `/{tier}/gallery/{story_id}` (existing)

**Changes**: Redirect to the first scene by ID (root scene) instead of index 0.

**Old**: Redirect to `/{tier}/gallery/{story_id}/0`
**New**: Redirect to `/{tier}/gallery/{story_id}/{root_scene_id}`

## Template Changes

### scene.html

- Add "Story Map" toggle button in the nav bar (only when `has_branches` is true or story has 2+ scenes)
- Add collapsible tree map container that renders when toggled
- Add explored indicator on choice buttons (checkmark or "explored" label when `choice.choice_id in explored_choices`)
- Include D3.js script and tree rendering code in the scripts block

### reader.html

- Replace linear prev/next navigation with tree map
- Add tree map container (always visible)
- Change navigation links from index-based to scene-ID-based
- Include D3.js script and tree rendering code

### base.html

- Add D3.js script tag (vendored local file)

## Client-Side Contracts

### Tree Map Component (static/js/tree-map.js)

New JavaScript file for tree map rendering logic:

- `renderTreeMap(containerId, treeData, currentId, urlPrefix, mode)` — main render function
  - `mode`: `"active"` (scene page, click navigates via POST) or `"gallery"` (reader, click navigates via GET)
- Uses D3.js `d3.tree()` for layout, `d3.linkHorizontal()` for edges
- SVG rendering with click handlers on nodes
- Path highlighting: current node is bold/colored, nodes on current path are semi-highlighted
- Responsive: container is scrollable, SVG sized to fit content

### Explored Choice Indicator

Pure CSS — no JavaScript needed. The server passes `explored_choices` set to the template, and explored choice buttons get an extra CSS class.
