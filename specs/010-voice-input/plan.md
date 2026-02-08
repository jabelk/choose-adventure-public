# Implementation Plan: Voice Input

**Branch**: `010-voice-input` | **Date**: 2026-02-07 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/010-voice-input/spec.md`

## Summary

Add a microphone button to the home page prompt form that lets users speak their adventure idea instead of typing. Two paths: browser-native Web Speech API (primary, free, real-time) and server-side OpenAI Whisper transcription (fallback for Firefox and unsupported browsers). The feature is entirely client-side JavaScript plus one new server endpoint, with no changes to existing models or story flow.

## Technical Context

**Language/Version**: Python 3.11+ (server), JavaScript ES6+ (client)
**Primary Dependencies**: FastAPI (existing), OpenAI SDK (existing, for Whisper), Web Speech API (browser), MediaRecorder API (browser)
**Storage**: N/A — audio is ephemeral, not persisted
**Testing**: Manual via quickstart.md
**Target Platform**: Web (desktop + mobile browsers, LAN access)
**Project Type**: Web application (existing structure)
**Performance Goals**: <3s transcription latency (browser-native), <10s total round-trip (server fallback)
**Constraints**: Must work on localhost without HTTPS; microphone access required
**Scale/Scope**: Single-user home app, 1 new server endpoint, 1 new JS file, 1 template modification

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Content Isolation | PASS | Voice input is a tier-agnostic input method. The transcription endpoint lives inside the tier router (`/{tier}/voice/transcribe`), following existing patterns. No cross-tier access. |
| II. Local-First | PASS | Browser-native mode needs no server. Server fallback uses OpenAI Whisper API — an accepted external dependency (same API key as image generation). App remains browsable when API is offline. |
| III. Iterative Simplicity | PASS | Simple microphone button + JS module. No new abstractions, no new models, no database changes. Feature-detect and fallback pattern is straightforward. |
| IV. Archival by Design | N/A | Voice input is ephemeral — audio is not stored. Text goes into the prompt field and follows existing story creation flow. |
| V. Fun Over Perfection | PASS | Voice input is inherently fun, especially for kids. Minimal code, quick to implement. |

**Post-design re-check**: All gates still PASS. No violations to track.

## Project Structure

### Documentation (this feature)

```text
specs/010-voice-input/
├── plan.md              # This file
├── research.md          # Browser API research, Whisper API details
├── data-model.md        # No new entities (ephemeral data)
├── quickstart.md        # Manual testing guide (8 steps)
├── contracts/           # Route contracts
│   └── routes.md        # POST /{tier}/voice/transcribe, GET /{tier}/voice/status
└── tasks.md             # Task breakdown (created by /speckit.tasks)
```

### Source Code (repository root)

```text
app/
├── routes.py            # Modified — add voice/transcribe and voice/status routes
└── services/
    └── voice.py         # New — Whisper transcription service

static/js/
└── voice-input.js       # New — client-side voice input logic

templates/
└── home.html            # Modified — add microphone button to prompt form

static/css/
└── style.css            # Modified — add microphone button and recording state styles
```

**Structure Decision**: Follows existing project layout. One new service file (`voice.py`), one new JS file (`voice-input.js`), and modifications to existing template/routes/CSS. No structural changes.
