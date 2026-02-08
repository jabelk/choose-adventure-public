# Research: Story Export

## Decision 1: PDF Generation Library

**Decision**: Use fpdf2 for PDF generation. Install via `pip install fpdf2`.

**Rationale**: fpdf2 is pure Python with no system-level dependencies (unlike WeasyPrint which needs Cairo/Pango, or pdfkit which needs wkhtmltopdf). It provides automatic page breaks, text wrapping, and native image embedding from file paths — exactly what's needed for story scenes. The API is simple and procedural, fitting the project's "fun over perfection" principle. It works offline and installs with a single pip command.

**Alternatives considered**:
- ReportLab: More powerful but heavier API. Lower-level drawing commands require more boilerplate for simple text + image layouts. fpdf2's automatic text wrapping is a better fit.
- WeasyPrint: Beautiful HTML-to-PDF but requires system libraries (Cairo, Pango). Violates the "no system-level deps" constraint and complicates deployment on the NUC.
- pdfkit/wkhtmltopdf: Requires a system binary. Not acceptable.

## Decision 2: HTML Export Approach

**Decision**: Use a Jinja2 template (`templates/export.html`) to render a self-contained HTML file. Images are embedded as base64 data URIs. A minimal inline JavaScript tree navigator (no D3.js dependency) handles branch navigation. All CSS is inlined.

**Rationale**: Jinja2 is already in the project. A template keeps the HTML structure readable and maintainable. Base64 images ensure the file works with no server — just `file://` in a browser. Avoiding D3.js in the export keeps the file smaller and removes a 280KB dependency from each exported file. A simple JS show/hide approach for scenes is sufficient for the offline reader.

**Alternatives considered**:
- Inline full D3.js in export: Adds ~280KB to every export file. Overkill for offline reading where the tree is static.
- Server-side rendered SVG for tree diagram: More complex, still needs JS for click-to-navigate. The inline JS approach is simpler.
- String concatenation instead of Jinja2: Harder to maintain, error-prone for HTML escaping.

## Decision 3: Image Embedding Strategy

**Decision**: Read images from the local filesystem (`static/images/{scene_id}.png`) and convert to base64 data URIs at export time. For missing images (failed generation), embed a small SVG placeholder.

**Rationale**: Saved stories store image URLs as relative paths like `/static/images/{scene_id}.png`. The actual PNG files are on disk. Reading and base64-encoding them at export time produces fully self-contained files. A lightweight SVG placeholder for missing images avoids broken image references and keeps the export clean.

**Alternatives considered**:
- Keep image URLs as-is in export: Would break when opened offline or on another machine. Defeats the purpose of self-contained export.
- Download from external URLs at export time: Images are already local. No need for network calls.

## Decision 4: Branch Ordering in PDF

**Decision**: Use depth-first traversal of the story tree, following the original path_history first (the "main path"), then rendering alternate branches at each fork point. Each branch section is labeled with the choice point it diverges from (e.g., "Branch from Chapter 2: 'Enter the cave'").

**Rationale**: The main path (path_history) is the narrative the user completed. It should read first as a coherent story. Alternate branches are presented as "what if" addenda, clearly labeled so the reader knows where they fork. This mirrors how a choose-your-own-adventure book would present alternate endings.

**Alternatives considered**:
- Breadth-first ordering: Interleaves branches, making it hard to read any single path.
- Separate sections per complete path: Duplicates shared content before fork points.

## Decision 5: Export Route Design

**Decision**: Add two new GET routes per tier: `GET /{tier}/gallery/{story_id}/export/html` and `GET /{tier}/gallery/{story_id}/export/pdf`. These return the file as a download (Content-Disposition: attachment).

**Rationale**: GET routes with descriptive paths are simple and linkable. Using separate routes (not query params) makes it clear which format is being requested. The response streams the file directly — no temp files on disk needed. The routes live inside the existing `create_tier_router`, so they're automatically tier-scoped.

**Alternatives considered**:
- POST route with format parameter: Unnecessary complexity for a read-only operation.
- Single route with `?format=html|pdf` query param: Less clear, harder to link directly.
- Async background job: Overkill for single-user app with 5-20 scene stories.
