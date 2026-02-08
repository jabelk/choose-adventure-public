# Feature Specification: Coloring Page Export

**Feature Branch**: `028-coloring-page-export`
**Created**: 2026-02-07
**Status**: Draft
**Input**: User description: "Coloring Page Export — Generate a line-art version of each scene image that can be printed for coloring. Single API call per image with 'simple black and white coloring page line art, thick outlines, no shading' style override. Export as PDF or downloadable PNG. Available on kids tier primarily but could work on both tiers."

## User Scenarios & Testing

### User Story 1 - Generate and Download Coloring Page PNG (Priority: P1)

A parent or child is reading a completed story in the gallery and sees a scene illustration they love. They click a "Coloring Page" button on the scene image. The system generates a black-and-white line-art version of that scene using the original image prompt with a coloring page style override. The line-art image is displayed and available for immediate download as a PNG file.

**Why this priority**: This is the core feature — generating a printable coloring page from a scene image. A single downloadable PNG per scene delivers the full value proposition. Kids can print and color their own story illustrations.

**Independent Test**: Navigate to a gallery story reader page, click the "Coloring Page" button on a scene image, verify a line-art image is generated, displayed, and downloadable as PNG.

**Acceptance Scenarios**:

1. **Given** a user is viewing a gallery story scene with an image prompt, **When** they click the "Coloring Page" button, **Then** the system generates a line-art version and displays it on the page.
2. **Given** a coloring page has been generated, **When** the user clicks "Download PNG," **Then** a black-and-white PNG file downloads to their device.
3. **Given** a scene has no image prompt, **When** the user views the scene, **Then** no "Coloring Page" button appears.
4. **Given** a coloring page is being generated, **When** the user waits, **Then** a loading indicator is shown and the button is disabled until generation completes.
5. **Given** generation fails, **When** the error occurs, **Then** a user-friendly error message appears with a retry option.

---

### User Story 2 - Download Coloring Page as Print-Ready PDF (Priority: P2)

A parent wants to print the coloring page and prefers PDF format for consistent print quality. After a coloring page is generated, they click "Download PDF" to get a single-page PDF with the line-art image sized for standard paper, ready to print.

**Why this priority**: PDF is the standard format for printing. Many parents will print coloring pages for their kids, and PDF ensures consistent paper sizing and margins.

**Independent Test**: Generate a coloring page, click "Download PDF," verify the downloaded file is a valid PDF with the line-art image properly sized for printing.

**Acceptance Scenarios**:

1. **Given** a coloring page has been generated, **When** the user clicks "Download PDF," **Then** a single-page PDF downloads with the image centered and scaled to fit standard paper with margins.
2. **Given** a coloring page PDF is downloaded, **When** the user prints it, **Then** the line-art image fills most of the page and is suitable for coloring.

---

### User Story 3 - Coloring Pages on Both Tiers (Priority: P3)

NSFW tier users can also generate coloring pages from their story scene images. The feature works identically on both tiers — same button placement, same generation, same download options.

**Why this priority**: Extends the feature trivially to NSFW since UI and generation logic are tier-agnostic. Low effort once P1 and P2 are done.

**Independent Test**: Navigate to an NSFW gallery story reader, click "Coloring Page," verify it generates and downloads identically to the kids tier.

**Acceptance Scenarios**:

1. **Given** a user is viewing an NSFW gallery story scene, **When** they click "Coloring Page," **Then** a line-art version is generated and downloadable, identical to kids tier behavior.

---

### Edge Cases

- What happens when the image generation service is unavailable? The system shows an error message ("Coloring page generation failed. Try again.") and allows the user to retry.
- What happens if the user clicks "Coloring Page" multiple times rapidly? The button is disabled after the first click until generation completes, preventing duplicate requests.
- What happens with very complex or abstract scene images? The line-art style override handles this — the prompt is rewritten for coloring page output regardless of original complexity.
- What happens on mobile devices? Downloads trigger the device's native download/save behavior.

## Requirements

### Functional Requirements

- **FR-001**: System MUST display a "Coloring Page" button on each scene in the gallery reader when the scene has a stored image prompt.
- **FR-002**: System MUST generate a line-art coloring page using the scene's stored image prompt combined with the style override: "simple black and white coloring page line art, thick outlines, no shading, suitable for children to color in."
- **FR-003**: System MUST generate the coloring page with a single image generation call (no multi-step processing).
- **FR-004**: System MUST display the generated line-art image to the user after generation completes.
- **FR-005**: System MUST provide a "Download PNG" option that delivers the coloring page as a PNG file.
- **FR-006**: System MUST provide a "Download PDF" option that delivers the coloring page as a single-page PDF sized for US Letter paper (8.5" x 11") with the image centered and appropriate margins.
- **FR-007**: System MUST show a loading indicator while the coloring page is being generated and disable the generate button to prevent duplicate requests.
- **FR-008**: System MUST hide the "Coloring Page" button when a scene has no image prompt available.
- **FR-009**: System MUST handle generation failures with a user-friendly error message and a retry option.
- **FR-010**: The coloring page feature MUST be available on both kids and NSFW tiers.

## Success Criteria

### Measurable Outcomes

- **SC-001**: Users can generate a coloring page from any gallery scene image in under 30 seconds.
- **SC-002**: Downloaded PNG files contain only black-and-white line art with clear outlines suitable for coloring.
- **SC-003**: Downloaded PDF files render correctly when printed on standard paper.
- **SC-004**: The coloring page button appears on 100% of gallery scenes that have an image prompt.

## Assumptions

- The image generation service supports style override prompts that produce line-art output from any scene prompt.
- A single image generation call per coloring page is sufficient — no post-processing pipeline needed.
- Coloring pages are generated on-demand and not cached or persisted between sessions.
- The coloring page style override produces consistent black-and-white output regardless of the original scene's art style.
- US Letter (8.5" x 11") is the default PDF paper size, which also works well on A4.

## Scope

### In Scope

- "Coloring Page" button on gallery reader scene images
- Line-art image generation via style override prompt
- PNG download of generated coloring page
- PDF download (single page, print-ready)
- Loading state and duplicate-click prevention
- Error handling with retry
- Both kids and NSFW tiers

### Out of Scope

- Batch export of all scenes as coloring pages in one action
- Coloring page generation during active story play (gallery only)
- Interactive digital coloring tools (in-browser drawing/painting)
- Caching or persisting generated coloring pages across sessions
- Custom line-art style options (e.g., simple vs. detailed)
- Coloring pages from extra images (character close-ups, wide shots) — scene main image only
