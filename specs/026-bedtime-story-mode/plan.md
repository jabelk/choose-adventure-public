# Implementation Plan: Bedtime Story Mode

**Branch**: `026-bedtime-story-mode` | **Date**: 2026-02-08 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/026-bedtime-story-mode/spec.md`

## Summary

Add a "Bedtime Mode" toggle to the kids tier home page that produces calming, short stories with bedtime-specific content guidelines and image style. When active, the UI switches to a warm night theme on scene pages, and a wind-down timer shows elapsed story time with a gentle 5-minute indicator.

## Technical Context

**Language/Version**: Python 3.11
**Primary Dependencies**: FastAPI, Jinja2, Pydantic
**Storage**: JSON file-based sessions (existing `app/session.py`)
**Testing**: pytest with `TestClient`
**Target Platform**: Linux (Intel NUC) / macOS (dev)
**Project Type**: Web application
**Performance Goals**: No new API calls — bedtime mode only modifies prompt text and CSS
**Constraints**: Kids tier only; must not break existing features
**Scale/Scope**: 1 new model field, route modifications, template conditionals, CSS theme, JS timer

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Content Isolation | PASS | Bedtime mode is kids-tier only. Toggle does not appear on NSFW. No cross-tier access. |
| II. Local-First | PASS | No new external API calls. Bedtime guidelines modify existing prompt text sent to AI. |
| III. Iterative Simplicity | PASS | Follows existing patterns: checkbox form field, boolean on Story model, CSS theme class, small JS timer. |
| IV. Archival by Design | PASS | Bedtime mode flag persisted on Story model, saved with gallery stories. |
| V. Fun Over Perfection | PASS | Simple toggle, no configuration screen, no scheduling. Cozy and fun. |

## Project Structure

### Documentation (this feature)

```text
specs/026-bedtime-story-mode/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── spec.md              # Feature specification
├── checklists/
│   └── requirements.md  # Spec quality checklist
└── tasks.md             # Phase 2 output (created by /speckit.tasks)
```

### Source Code (repository root)

```text
app/
├── models.py            # Add bedtime_mode: bool field to Story and SavedStory
├── routes.py            # Modify start_story, surprise_me, make_choice, custom_choice, view_scene
└── tiers.py             # Add BEDTIME_CONTENT_GUIDELINES and BEDTIME_IMAGE_STYLE constants

templates/
├── home.html            # Add bedtime mode checkbox (kids tier only)
└── scene.html           # Add bedtime theme class + wind-down timer

static/
├── css/style.css        # Add .theme-bedtime CSS custom properties
└── js/bedtime-timer.js  # Wind-down timer component (new file)

tests/
└── test_bedtime_mode.py # Tests for bedtime mode (new file)
```

**Structure Decision**: Follows existing patterns exactly. The `bedtime_mode` boolean on Story mirrors `video_mode`. Bedtime content guidelines in `tiers.py` mirrors existing `KIDS_CONTENT_GUIDELINES`. CSS theme class mirrors `.theme-kids` / `.theme-adult` pattern.

## Implementation Approach

### Model (app/models.py)

Add `bedtime_mode: bool = False` to both `Story` and `SavedStory` models. This follows the same pattern as `video_mode`.

### Content Guidelines (app/tiers.py)

Add two new constants:

- `BEDTIME_CONTENT_GUIDELINES`: Appended to kids guidelines when bedtime mode is active. Instructs AI to be gentle, soothing, no tension, end with sleep.
- `BEDTIME_IMAGE_STYLE`: Replaces normal kids image style. Warm, soft, nighttime, cozy imagery.

### Routes (app/routes.py)

**start_story**: Add `bedtime_mode: str = Form("")` parameter. If `bedtime_mode == "on"` and tier is kids:
- Append bedtime content guidelines
- Override image style with bedtime image style
- Force `story_length = StoryLength.SHORT` and `target_depth = 3`
- Set `story.bedtime_mode = True`

**surprise_me**: Check for bedtime mode cookie/form. If active on kids tier, apply same overrides.

**make_choice / custom_choice**: Check `story_session.story.bedtime_mode`. If True, append bedtime guidelines and use bedtime image style when rebuilding content_guidelines.

**view_scene**: Pass `story.bedtime_mode` to template context.

### Template (templates/home.html)

Add a bedtime mode checkbox inside the kids tier section (next to the existing video mode / memory mode toggles):
```html
{% if tier.name == 'kids' %}
<div class="bedtime-mode-selector">
    <label class="section-label">Bedtime Mode</label>
    <div class="memory-toggle-row">
        <label>
            <input type="checkbox" name="bedtime_mode" value="on">
            Calming bedtime story with warm night theme
        </label>
    </div>
</div>
{% endif %}
```

### Template (templates/scene.html)

- Add `theme-bedtime` class to body when bedtime mode is active (via base.html data attribute or inline override)
- Add wind-down timer div (hidden unless bedtime mode)

### CSS (static/css/style.css)

Add `.theme-bedtime` that overrides CSS custom properties:
- Deep navy/indigo background
- Soft amber/warm gold accents
- Muted, warm text colors
- Reduced contrast for low-light viewing

### JavaScript (static/js/bedtime-timer.js)

Simple elapsed timer:
- Starts counting from 0:00 on page load
- Uses `sessionStorage` to persist start time across scene navigations
- After 5 minutes, adds a `.wind-down` class that triggers a gentle CSS pulse animation
- Displays as "mm:ss" in a small overlay

### Gallery Reader Exclusion

Gallery reader uses `reader.html`, not `scene.html`. No bedtime theme or timer in gallery. Bedtime mode flag is saved on the story for archival purposes only.

## Complexity Tracking

> No violations — all constitution gates pass.
