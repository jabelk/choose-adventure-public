# Feature Specification: Story Export

**Feature Branch**: `009-story-export`
**Created**: 2026-02-07
**Status**: Draft
**Input**: User description: "Story Export - Export completed stories from the gallery as self-contained files that can be shared or archived outside the app. Users can download a story as a single HTML file or PDF that includes all the text, images, and branching structure. The export preserves the full story tree so recipients can read all explored branches. This makes stories portable and shareable beyond the LAN."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Export Story as Self-Contained HTML (Priority: P1)

A user has completed a branching story and wants to share it with someone who doesn't have access to the app. From the gallery, they click an "Export" button on the story card or within the story reader. The system generates a single HTML file that contains all story text, embedded images, and an interactive tree map for navigating between branches. The user downloads the file and can open it in any web browser — no server needed. The recipient can read all explored branches by clicking through the tree, just like in the gallery reader.

**Why this priority**: A single self-contained HTML file is the simplest export format that preserves interactivity. It requires no external dependencies, works in any browser, and maintains the branching navigation experience. This is the core export capability.

**Independent Test**: Complete a story with at least 2 branches. Click "Export" from the gallery. Open the downloaded HTML file in a browser (with no server running). Verify all text, images, and branch navigation work offline.

**Acceptance Scenarios**:

1. **Given** a completed story with 2+ branches in the gallery, **When** the user clicks "Export as HTML", **Then** a single HTML file is downloaded containing all story text, images (embedded as base64), and an interactive tree map.
2. **Given** the exported HTML file is opened in a browser without a server, **When** the user clicks a branch in the tree map, **Then** the view navigates to that scene showing its text and image.
3. **Given** a completed linear story (no branches), **When** the user exports it as HTML, **Then** the exported file shows a simple sequential story with prev/next navigation (or a single-path tree map).

---

### User Story 2 - Export Story as PDF (Priority: P2)

A user wants a printable, archival version of a completed story. From the gallery, they choose "Export as PDF." The system generates a PDF document with each scene on its own page (or section), including the scene text and image. For branched stories, the PDF presents all branches in a readable linear order (e.g., main path first, then alternate branches labeled by their choice point). A visual tree diagram is included at the beginning as a table of contents.

**Why this priority**: PDF is a universal archival format — great for printing, long-term storage, and sharing via email. It complements the interactive HTML export with a static, printable option. However, it's more complex to generate and loses interactivity, so it comes second.

**Independent Test**: Complete a branched story. Click "Export as PDF" from the gallery. Open the PDF and verify all scenes are present, images are included, and branches are clearly labeled.

**Acceptance Scenarios**:

1. **Given** a completed story with branches, **When** the user clicks "Export as PDF", **Then** a PDF file is downloaded containing all scenes with text and images, organized by branch.
2. **Given** the PDF is opened, **When** the user reviews it, **Then** scenes from the main path appear first, followed by alternate branches with clear labels indicating which choice point they diverge from.
3. **Given** a story with images that failed to generate (no image URL), **When** exported as PDF, **Then** a placeholder appears in place of the missing image (not a broken reference).

---

### Edge Cases

- What happens when a story has no images (all image generations failed)? The export includes the text content with placeholder indicators where images would appear. The export does not fail.
- What happens with a very large story (7 chapters, 3+ branches = 20+ scenes)? The HTML export remains functional with scrollable tree map. The PDF handles pagination automatically.
- What happens if images are stored as local file paths vs. external URLs? The export resolves images by reading them from their stored location and embedding them directly (base64 for HTML, inline for PDF).
- What happens when a story was saved before the branching feature (linear path only)? The export works normally — it treats the story as a single-path tree. No errors.
- Can the user export from the story reader view (not just gallery list)? Yes — an export button is available in both the gallery card and the reader view.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide an "Export" option for each completed story in the gallery, accessible from both the gallery list and the reader view.
- **FR-002**: System MUST generate a single self-contained HTML file that includes all story text, images (embedded), and interactive branch navigation.
- **FR-003**: The exported HTML file MUST work when opened directly in a browser without any server or network connection.
- **FR-004**: The exported HTML MUST preserve the full branching structure — all explored branches are navigable via an embedded tree map or equivalent navigation.
- **FR-005**: System MUST generate a PDF file containing all story scenes with text and images, organized by branch.
- **FR-006**: The PDF MUST present branches in a readable order: main path first, then alternate branches with clear labels identifying the choice point they diverge from.
- **FR-007**: The PDF MUST include a visual overview of the story's branching structure (tree diagram or table of contents) at the beginning.
- **FR-008**: Exports MUST handle missing images gracefully — using placeholders instead of broken references or errors.
- **FR-009**: Exports MUST include story metadata: title, creation date, and story prompt.
- **FR-010**: System MUST support exporting stories that were saved before the branching feature (linear stories) without errors.

### Key Entities

- **Export Request**: A user-initiated action specifying the story to export and the desired format (HTML or PDF). Results in a downloadable file.
- **Exported File**: A self-contained document (HTML or PDF) containing all story content, images, metadata, and navigation structure. Has no external dependencies.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can export a completed story as HTML in under 5 seconds, and the resulting file opens and functions correctly in any modern browser without a server.
- **SC-002**: Users can export a completed story as PDF in under 10 seconds, and the resulting file opens correctly in any PDF reader.
- **SC-003**: Exported HTML files preserve 100% of the story's branch navigation — every explored branch is accessible in the offline file.
- **SC-004**: Exported files include all available images embedded directly — no external URLs or broken image references when viewed offline.
- **SC-005**: Pre-existing linear stories (saved before branching) export successfully in both formats without errors or visual glitches.

## Assumptions

- Images stored locally on disk can be read and embedded (base64) at export time. External image URLs are fetched and embedded at export time.
- The exported HTML file reuses a simplified version of the app's tree map component (self-contained, no external D3.js dependency — either inline the needed D3 subset or use a simpler CSS/JS tree).
- PDF generation uses a server-side library. The specific library is a planning-phase decision, but it must work without external services or network calls.
- Export file sizes for typical stories (5-7 scenes, images) will be in the 2-10 MB range, which is acceptable for download and email sharing.
- Export is a synchronous download — the user clicks, waits briefly, and the file downloads. No background job queue is needed for typical story sizes.

## Scope Boundaries

### In Scope

- Export from gallery (list view and reader view)
- HTML export with embedded images and interactive tree navigation
- PDF export with embedded images and branch-organized layout
- Support for both branched and linear (pre-branching) stories
- Story metadata in exports (title, date, prompt)

### Out of Scope

- Exporting in-progress stories (only completed gallery stories)
- Exporting as other formats (EPUB, plain text, Markdown)
- Batch export of multiple stories at once
- Customizable export templates or themes
- Sharing via email or social media directly from the app
- Re-importing an exported story back into the app
