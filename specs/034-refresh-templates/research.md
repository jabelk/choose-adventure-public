# Research: Refresh Templates Button

## Client-Side Shuffle Approach

**Decision**: Embed the full template pool as a JSON array in a hidden script block on the home page. JavaScript picks a random subset of 6 to display initially and on each shuffle click. No server round-trip needed.

**Rationale**: Templates are small data objects (title, description, emoji, prompt, length, kinks, etc.). Even 20 templates per tier is under 10KB of JSON. Embedding them avoids an extra API endpoint and keeps the interaction instant. The existing `selectTemplate()` function in `app.js` already reads data attributes from template cards, so dynamically-created cards just need the same attributes.

**Alternatives considered**:
- Server-side shuffle via a dedicated `/shuffle-templates` endpoint — rejected because it adds latency and server load for no benefit given the small data size.
- Lazy-loading templates from a JSON file — rejected because it adds complexity (fetch, error handling, loading state) for negligible benefit.

## Template Pool Size

**Decision**: Expand each tier from its current set to at least 12 templates. Kids tier currently has 6, NSFW tier has 10. Add 6+ new kids templates and 2+ new NSFW templates to reach the minimum.

**Rationale**: With 6 shown at a time, a pool of 12 means each shuffle shows a completely fresh set (no overlap required). Going beyond 12 is fine but not required for MVP.

**Alternatives considered**:
- Using AI to generate templates on the fly — rejected as over-engineered for this feature and would require API calls.
- Keeping the current pool sizes and only shuffling order — rejected because the user specifically wants "a new random selection," implying hidden/shown subsets.

## Shuffle Button Placement

**Decision**: Place the shuffle button inline with the template section label ("Pick a template or write your own below"), as a small icon button to the right of the label text.

**Rationale**: This keeps it visually associated with the templates without adding clutter. A shuffle icon (🔀 or a refresh arrow) is universally understood.

**Alternatives considered**:
- A floating button below the template grid — rejected because it could be confused with the "Start Adventure" button.
- A button above the entire form — rejected because it's not visually connected to the templates.

## Template Card Rendering

**Decision**: Render all template cards on the server side (Jinja2) as hidden divs, then use JavaScript to show/hide subsets. This avoids having to reconstruct HTML from JSON in JavaScript.

**Rationale**: The template card HTML includes data attributes, emoji, title, and description. Generating this in Jinja2 keeps the rendering consistent with the current approach. JavaScript just toggles visibility of cards (show 6, hide the rest).

**Alternatives considered**:
- Building cards entirely in JavaScript from a JSON pool — rejected because it duplicates the HTML structure already defined in the Jinja2 template and is harder to maintain.
- Using server-side random selection on each page load — would work for initial randomization but doesn't support client-side shuffle without page reload.
