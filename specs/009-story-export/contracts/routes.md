# Route Contracts: Story Export

## New Routes

### GET `/{tier}/gallery/{story_id}/export/html` (new)

**Purpose**: Download a completed story as a self-contained HTML file.

**Request**: No body or parameters beyond the URL path.

**Behavior**:
1. Load the saved story via `gallery_service.get_story(story_id)`
2. Verify story belongs to the requesting tier
3. For each scene, read the image from disk and encode as base64 data URI
4. Build the tree structure for navigation
5. Render `templates/export.html` with all story data, base64 images, and inline CSS/JS
6. Return the rendered HTML as a file download

**Response**: HTML file download.
- Content-Type: `text/html`
- Content-Disposition: `attachment; filename="{story_title}.html"`
- The file is self-contained: all images are base64 data URIs, all CSS/JS is inline

**Error handling**:
- Story not found or wrong tier: redirect to gallery
- Missing images: embedded SVG placeholder (no broken references)

### GET `/{tier}/gallery/{story_id}/export/pdf` (new)

**Purpose**: Download a completed story as a PDF document.

**Request**: No body or parameters beyond the URL path.

**Behavior**:
1. Load the saved story via `gallery_service.get_story(story_id)`
2. Verify story belongs to the requesting tier
3. Build title page with story metadata (title, prompt, date)
4. Build tree diagram overview (text-based branch listing)
5. For each scene (main path first, then alternate branches):
   - Add scene heading (chapter number, branch label if applicable)
   - Embed image from disk (or placeholder for missing images)
   - Add scene text
   - Add page break between scenes
6. Return the PDF as a file download

**Response**: PDF file download.
- Content-Type: `application/pdf`
- Content-Disposition: `attachment; filename="{story_title}.pdf"`

**Error handling**:
- Story not found or wrong tier: redirect to gallery
- Missing images: text placeholder in PDF (no broken references)
- fpdf2 errors: return error page

## Modified Templates

### gallery.html

- Add "Export" dropdown or buttons on each story card
- Options: "Export HTML" and "Export PDF"
- Links point to the new export routes

### reader.html

- Add "Export" button(s) in the reader navigation area
- Options: "Export HTML" and "Export PDF"
- Links point to the new export routes

## New Template

### export.html (new)

**Purpose**: Jinja2 template that renders a complete self-contained HTML page for offline reading.

**Structure**:
- `<!DOCTYPE html>` with all CSS inline in a `<style>` block
- Story metadata header (title, prompt, date)
- A tree map/navigation panel showing all branches (simple HTML/CSS tree, or inline SVG)
- Scene containers (one `<div>` per scene, shown/hidden via JS)
- Each scene has: heading, base64 image, text content
- Inline `<script>` for navigation (show/hide scenes, highlight current node in tree)
- No external dependencies — everything is embedded

**Template context variables**:
- `story`: SavedStory object
- `scenes_data`: List of dicts with scene info + base64 image data
- `tree_data`: Nested tree structure for navigation
- `styles`: Inline CSS string
