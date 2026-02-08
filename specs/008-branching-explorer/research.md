# Research: Story Branching Explorer

## Decision 1: Tree Visualization Approach

**Decision**: Use D3.js v7 vendored locally (`static/js/d3.v7.min.js`) for the tree map visualization. Use `d3.tree()` for layout and `d3.linkHorizontal()` for edges. SVG rendering with click-to-navigate handlers.

**Rationale**: D3's tree layout algorithm (Reingold-Tilford) handles node positioning automatically. One vendored file (~280KB), no build tools, no npm. Works entirely offline on LAN. The tree data is passed as JSON embedded in the page by Jinja2. Current path highlighting is computed by walking from the current node to root.

**Alternatives considered**:
- Pure CSS/HTML nested lists: Wrong tool — renders an indented list, not a visual tree map with spatial layout and connecting lines.
- Server-side SVG in Jinja2: Too much manual layout math. Still needs JS for interactivity.
- Canvas: No DOM nodes for click handling. Hit-testing complexity for zero benefit at 10-30 nodes.
- Treant.js: Depends on Raphael.js + optional jQuery (2-3 deps). Last updated ~2016-2017.

## Decision 2: Tree Data Structure for Frontend

**Decision**: Build a nested dict/JSON tree on the server from the flat `scenes` dict using `parent_scene_id` relationships. Each node has `id`, `title` (chapter label), `is_ending`, `is_current`, `depth`, `choice_text` (the choice that led here), and `children` (list of child nodes). Pass as `{{ tree_data | tojson }}` in templates.

**Rationale**: D3's `d3.hierarchy()` expects nested parent-child data. The existing `scenes` dict already has `parent_scene_id` on each scene, so building the tree is a simple grouping operation. A helper function in Python (or a Jinja2 global) can do this conversion.

**Alternatives considered**:
- Flat adjacency list on frontend: Would require client-side tree construction. More JS code for no benefit.

## Decision 3: Branching Behavior — Path History Changes

**Decision**: When the user goes back and picks a different choice, truncate `path_history` to the current scene (the choice point), then extend it with the new branch. The old branch's scenes remain in the `scenes` dict (preserved via `parent_scene_id` and `Choice.next_scene_id`). The `path_history` only tracks the "current reading position" path from root to the active leaf.

**Rationale**: The existing data model already stores all scenes in a flat dict. `path_history` is the only linear structure — it just needs to be rewritable when switching branches. When the user clicks a node in the tree map, `path_history` is rebuilt by walking from root to the clicked node via `parent_scene_id`. No data model changes needed.

**Alternatives considered**:
- Storing all branch paths explicitly: Over-engineered. The tree structure is implicit in the parent-child relationships. `path_history` just tracks "where you are now."

## Decision 4: Gallery Reader Navigation with Branches

**Decision**: Change the gallery reader from index-based (`/gallery/{id}/{scene_index}`) to scene-ID-based (`/gallery/{id}/{scene_id}`) navigation. The existing index-based scheme assumes a linear path. With branches, any scene can be accessed by ID. The tree map shows all scenes; clicking navigates to that scene's reader page.

**Rationale**: Index-based navigation is inherently linear — index 3 means "the 4th scene in the path." With branches, there's no single linear ordering. Scene IDs are unique and already used everywhere in the active story flow. The gallery reader should mirror this.

**Alternatives considered**:
- Keep index-based + add branch parameter: Adds complexity to URL scheme for no benefit.
- Show branches as separate "paths" with index navigation within each: Loses the tree visualization benefit.

## Decision 5: Explored Choice Visual Indicator

**Decision**: On the scene page, add a small indicator next to each choice button showing whether that choice has already been explored (i.e., `choice.next_scene_id` is not None). Use a simple text marker like "explored" or a checkmark icon via CSS. Unexplored choices have no indicator.

**Rationale**: FR-003 requires visual distinction. The data already exists — `Choice.next_scene_id` is set when a choice has been taken. No new fields needed. A CSS class toggle is the simplest approach.

**Alternatives considered**:
- Disable explored choices: Bad UX — users should be able to re-visit explored branches.
- Different button colors: Could be confusing. A subtle text indicator is clearer.

## Decision 6: Tree Map Placement in Scene Page

**Decision**: Add a collapsible tree map panel to the scene page, toggled by a "Story Map" button in the nav bar. The tree map appears above or below the scene content. It's collapsed by default to avoid cluttering the reading experience. In the gallery reader, it's always visible above the scene.

**Rationale**: The tree map is a navigation aid, not the primary content. Making it collapsible respects the reading experience while keeping it accessible. In the gallery, readers are more likely to browse/explore, so it's always visible.

**Alternatives considered**:
- Separate dedicated map page: Adds a round-trip. Inline is faster.
- Sidebar: Doesn't work well on mobile. Above/below content is responsive-friendly.

## Decision 7: Context Building for Branch Scenes (FR-012)

**Decision**: When generating a scene for a new branch, `get_full_context()` should return the path from root to the current choice point (the scene where the user is selecting a different choice). This is the `path_history` at the moment of branching (already truncated to the choice point). The AI sees only the story context leading to this fork, not content from other branches.

**Rationale**: The existing `get_full_context()` reads from `path_history`. When the user goes back, `navigate_backward()` pops entries from `path_history`. When they select a new choice, `path_history` has already been trimmed. So `get_full_context()` naturally returns the correct branch context without changes.

**Alternatives considered**:
- Explicit branch-aware context builder: Unnecessary — the existing mechanism already works correctly once `path_history` is properly maintained.
