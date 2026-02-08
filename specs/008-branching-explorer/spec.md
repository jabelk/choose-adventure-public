# Feature Specification: Story Branching Explorer

**Feature Branch**: `008-branching-explorer`
**Created**: 2026-02-07
**Status**: Draft
**Input**: User description: "Story Branching Explorer - Visualize the story tree as a branching diagram, revisit alternate paths, and explore 'what if' branches from any choice point."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Explore Alternate Branches During Active Play (Priority: P1)

While reading a story, the user decides they want to see what would have happened if they had made a different choice. They click "Go Back" to return to a previous scene that has unexplored choices, select a different option, and a new branch is generated. The original branch is preserved — the user hasn't lost any progress. Their current reading position moves to the new branch. All explored scenes (from both the original and new branches) remain in the story session and are saved when the story completes.

**Why this priority**: This is the core value proposition — making stories truly explorable rather than linear. Without branching, "Go Back" only lets you replay the same path. With branching, every choice becomes a real fork.

**Independent Test**: Start a story, make 2-3 choices, go back to an earlier scene, pick a different choice. Verify the new branch generates correctly, the old branch scenes are preserved in the session, and completing either branch saves all explored scenes.

**Acceptance Scenarios**:

1. **Given** a user is on a scene with 3 choices and has already explored choice A, **When** the user goes back and selects choice B, **Then** a new scene is generated for choice B, the original choice A branch remains accessible, and the user's current position is the new scene.
2. **Given** a user has explored two branches of the same choice point, **When** they go back to that choice point, **Then** they can see which choices have already been explored (visually distinguished from unexplored ones).
3. **Given** a user reaches an ending on a branch, **When** the story is saved to the gallery, **Then** all scenes from all explored branches are included in the saved story, not just the final path.

---

### User Story 2 - View Story Tree Map (Priority: P2)

The user wants to see an overview of their entire story — all the branches they've explored, where they currently are, and which choice points still have unexplored options. A visual tree map shows the branching structure. Nodes represent scenes, edges represent choices. The current scene is highlighted. Explored branches are visually distinct from the current path. The user can click a node to jump directly to that scene.

**Why this priority**: The tree map makes the branching structure tangible and navigable. Without it, users would have to mentally track which branches they've explored. It is the "explorer" part of the feature name.

**Independent Test**: Start a story, explore 2+ branches, open the tree map. Verify it shows all explored scenes as a tree, highlights the current scene, distinguishes explored vs current path, and clicking a node navigates to that scene.

**Acceptance Scenarios**:

1. **Given** a user has explored a story with 2 branches, **When** they open the tree map, **Then** they see a tree diagram showing both branches with the current path highlighted.
2. **Given** the tree map is open, **When** the user clicks a scene node, **Then** they are navigated to that scene and the tree map updates to show the new current position.
3. **Given** a choice point has 3 options with only 1 explored, **When** the tree map displays this node, **Then** the explored branch is shown as a solid line and the 2 unexplored choices are indicated (e.g., dotted outlines or a count).

---

### User Story 3 - Browse Branching Structure in Gallery Reader (Priority: P3)

When viewing a completed story in the gallery reader, the user can see and navigate the full branching structure. Instead of only reading the linear path that ended the story, the reader shows a tree map of all explored branches. The user can click into any branch to read those scenes. This turns the gallery from a linear replay into an explorable archive.

**Why this priority**: This extends the branching experience to the gallery, where stories are permanently stored. It completes the vision of stories as explorable trees rather than linear sequences.

**Independent Test**: Complete a story with multiple branches. View it in the gallery reader. Verify the tree map appears, shows all branches, and clicking any scene navigates to it in the reader.

**Acceptance Scenarios**:

1. **Given** a completed story with 2 branches is in the gallery, **When** the user opens it in the reader, **Then** they see a tree map showing the full branching structure.
2. **Given** the user is viewing a gallery story tree map, **When** they click a scene on a different branch, **Then** the reader navigates to that scene and updates the tree map highlight.
3. **Given** a pre-existing story was saved before branching was available (linear path only), **When** it is viewed in the gallery, **Then** the tree map shows a single linear path without errors.

---

### Edge Cases

- What happens when a user explores every choice at a single choice point? All branches are shown; no special behavior needed beyond normal display.
- What happens when the user goes back multiple levels and branches from an early scene? The tree correctly shows deeply nested branching — a branch from scene 1 creates an entirely separate sub-tree.
- What happens when a branch reaches the maximum story depth? The branch ends normally (as an ending scene), just like the main path.
- How does the tree map handle very large stories (e.g., 7 chapters with 3 branches each = 21+ scenes)? The tree map remains usable — scrollable or zoomable if necessary.
- What happens to in-progress saves with branches? The progress file preserves all explored branches so resume works correctly.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST preserve all explored branches when a user goes back and makes a different choice — no scenes from previous branches are deleted.
- **FR-002**: System MUST generate a new scene when the user selects an unexplored choice, using the story context from the path leading to that choice point (not from the previously explored branch).
- **FR-003**: System MUST visually distinguish explored choices from unexplored ones at each choice point during active play.
- **FR-004**: System MUST provide a tree map view showing all explored scenes as a branching diagram during active play.
- **FR-005**: System MUST highlight the user's current scene in the tree map and show the current path distinctly.
- **FR-006**: System MUST allow the user to click a scene node in the tree map to navigate directly to that scene.
- **FR-007**: System MUST save all explored branches (all scenes, not just the final path) when a story is completed and saved to the gallery.
- **FR-008**: System MUST display the branching tree map in the gallery reader for completed stories.
- **FR-009**: System MUST allow gallery reader navigation to any scene in any branch via the tree map.
- **FR-010**: System MUST preserve all explored branches in progress saves so that resuming a story restores the full tree.
- **FR-011**: System MUST handle pre-existing linear stories gracefully — display them as a single-path tree with no errors.
- **FR-012**: System MUST build the correct story context (the path from root to the current choice point) when generating new branch scenes, ensuring narrative coherence with the path that led to this point rather than a different branch.

### Key Entities

- **Story Tree**: The complete set of explored scenes forming a directed tree. Each scene has at most one parent (the choice point it was generated from). The root scene has no parent.
- **Branch**: A path from any scene to a leaf (ending scene or latest scene in an in-progress branch). Multiple branches can share a common prefix (scenes before the fork).
- **Choice Point**: A non-ending scene where the user has explored more than one choice. The tree forks at these nodes.
- **Current Path**: The ordered list of scenes from root to the user's current position. This is what the path history tracks.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can explore at least 3 distinct branches within a single story session and navigate between them without losing any content.
- **SC-002**: The tree map correctly renders all explored branches and allows navigation to any scene within 1 click.
- **SC-003**: Completed stories with multiple branches display all branches in the gallery reader — no explored content is lost during save.
- **SC-004**: Pre-existing linear stories display correctly in the tree map as a single path, with no errors or visual glitches.
- **SC-005**: Story resume from progress files preserves the full branch tree — all previously explored branches are available after resume.

## Assumptions

- The existing data model already supports tree structures: scenes are stored as a dictionary of all scenes, choices link to generated scenes, and parent scene identifiers trace back to the parent. Only the path history is linear and needs to change when switching branches.
- The tree map will be rendered client-side as an interactive element. It does not need to support extremely large trees (100+ nodes) — practical story trees will have 10-30 nodes.
- Branching does not change the story's target depth — each branch independently tracks its own depth relative to the root.
- The story is considered "complete" when any branch reaches an ending. All explored branches (complete or in-progress) are saved.
- Each tier has branching enabled by default — there is no per-tier toggle for this feature.

## Scope Boundaries

### In Scope

- Branching during active play (go back and pick different choice)
- Visual tree map for active stories and gallery reader
- Exploring choices already taken (re-visiting an existing branch, not re-generating)
- Saving all branches to gallery
- Progress save/resume with full tree

### Out of Scope

- Generating branches without user action (auto-exploring all choices)
- Comparing two branches side-by-side
- Merging branches (two paths converging to the same scene)
- Exporting the tree structure
- AI-generated summaries of branch differences
