# Implementation Plan: Read Aloud / TTS Narration

**Branch**: `022-read-aloud-tts` | **Date**: 2026-02-07 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/022-read-aloud-tts/spec.md`

## Summary

Add text-to-speech narration to every story scene using the OpenAI TTS API (`gpt-4o-mini-tts`). A play/stop button on each scene page reads the narrative content aloud. The kids tier auto-plays narration on scene load for the 2.5-year-old. Users can select from curated voices per tier, with preferences persisted in the session cookie. Sentence-level highlighting during playback is a P4 stretch goal.

## Technical Context

**Language/Version**: Python 3 (FastAPI + Jinja2)
**Primary Dependencies**: OpenAI SDK (`openai` package, already installed), HTML5 Audio API
**Storage**: N/A (audio generated on demand, not persisted)
**Testing**: pytest (existing test suite)
**Target Platform**: Linux server (Docker on Intel NUC), mobile browsers (iPad/phone)
**Project Type**: Web application (server-rendered templates + client-side JS)
**Performance Goals**: Audio playback starts within 3 seconds of tap (SC-001)
**Constraints**: OpenAI TTS `gpt-4o-mini-tts` model, 2000 token (~4000 char) per-request limit
**Scale/Scope**: Single-user household, LAN-only

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Content Isolation | PASS | TTS uses same tier-scoped routing. No cross-tier audio access. Voice selection and auto-play preferences are per-tier session cookies. |
| II. Local-First | PASS | Audio is generated via external API (same as images), but app remains fully functional for reading/browsing when API is unreachable. Play button silently absent when no API key (FR-011). |
| III. Iterative Simplicity | PASS | Simple synchronous request-response pattern. No background tasks, no audio storage, no caching. P4 (highlighting) deferred as stretch goal. |
| IV. Archival by Design | PASS | Audio is ephemeral by design (not archived). Gallery reader scenes get the play button too, so archived stories can be read aloud on demand. |
| V. Fun Over Perfection | PASS | Focused on getting narration working quickly. No over-engineering (no audio caching, no WebSocket streaming, no custom voice training). |

## Project Structure

### Documentation (this feature)

```text
specs/022-read-aloud-tts/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   └── tts-api.md       # TTS endpoint contract
└── tasks.md             # Phase 2 output (/speckit.tasks command)
```

### Source Code (repository root)

```text
app/
├── services/
│   └── tts.py              # NEW: TTS service (generate_speech)
├── routes.py               # MODIFY: Add TTS endpoint, pass tts_available to templates
├── tiers.py                # MODIFY: Add default voice + auto-play config per tier
└── config.py               # NO CHANGE: OpenAI key already available

templates/
├── scene.html              # MODIFY: Add play button, voice selector, auto-play logic
└── reader.html             # MODIFY: Add play button, voice selector

static/
├── js/
│   └── tts-player.js       # NEW: TTS playback controller (play/stop, auto-play, voice select)
└── css/
    └── style.css            # MODIFY: Add TTS button and highlight styles

tests/
└── test_all_options.py     # MODIFY: Add TTS-related tests
```

**Structure Decision**: Follows existing project layout. One new service file (`tts.py`), one new JS file (`tts-player.js`), modifications to existing templates and routes. No new directories needed.
