# Implementation Plan: Sound Effects / Ambiance

**Branch**: `032-sound-effects-ambiance` | **Date**: 2026-02-08 | **Spec**: [spec.md](spec.md)

## Summary

Add ambient audio that auto-plays on scene load based on keyword matching against scene content. A JS module maps scene text to audio categories (forest, ocean, dragon, magic, space), plays the matching audio file on loop, and provides a mute toggle that persists via localStorage. No new server routes — purely client-side with bundled static audio files. Both templates (scene.html, reader.html) get a mute toggle and the ambient audio script.

## Technical Context

**Language/Version**: Python 3 with FastAPI, Jinja2 templates
**Primary Dependencies**: Vanilla JavaScript (client-side only), HTML5 Audio API
**Storage**: Static audio files in `static/audio/`, mute preference in browser localStorage
**Testing**: pytest with FastAPI TestClient

## Constitution Check

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Content Isolation | PASS | Same audio on both tiers, no tier-specific content. |
| II. Local-First | PASS | Audio files bundled as static assets, no external CDN. |
| III. Iterative Simplicity | PASS | Single JS file, a few audio files, template additions. No new routes. |
| IV. Archival by Design | PASS | No impact on story data. Audio is presentation-only. |
| V. Fun Over Perfection | PASS | Adds atmosphere and fun to the story experience. |

## Design

### Audio Category Mapping

A JS config object maps category names to keywords and audio file paths:

```
forest: ["forest", "trees", "woods", "woodland", "jungle"]
ocean: ["ocean", "sea", "beach", "waves", "shore", "lake", "river", "water"]
dragon: ["dragon", "fire", "flame", "lava", "volcano", "inferno"]
magic: ["magic", "spell", "wizard", "witch", "enchant", "fairy", "wand", "potion"]
space: ["space", "spaceship", "galaxy", "planet", "star", "rocket", "alien", "cosmic"]
city: ["city", "town", "market", "street", "tavern", "inn", "castle", "kingdom"]
storm: ["storm", "thunder", "lightning", "rain", "wind"]
```

Scene content text is lowercased and checked for substring matches. First match wins.

### Audio Files

Royalty-free ambient loops stored at `static/audio/`:
- `forest.mp3` — bird chirps, rustling leaves
- `ocean.mp3` — waves, seagulls
- `dragon.mp3` — crackling fire, distant roar
- `magic.mp3` — sparkle, ethereal chimes
- `space.mp3` — low hum, electronic ambiance
- `city.mp3` — crowd murmur, distant bells
- `storm.mp3` — rain, thunder

Files should be 10-30 seconds, looping seamlessly, under 200KB each.

### Client-Side JS Module

New file: `static/js/ambiance.js`
- `initAmbiance(config)` accepting `{ sceneContent, bedtimeMode }`
- Matches scene content against keyword categories
- Creates/reuses a single HTML5 Audio element
- Sets volume to 0.15 (low background level)
- Loops audio via `loop = true`
- Reads mute state from `localStorage.getItem('ambiance_muted')`
- Bedtime mode forces muted by default
- Handles autoplay rejection gracefully (catches promise rejection)

### Mute Toggle

A small speaker icon button placed near the scene text area. Shows speaker icon when unmuted, muted-speaker icon when muted. Click toggles `localStorage` key and pauses/resumes audio.

### Template Changes

**scene.html**: Add mute toggle button, include `ambiance.js`, initialize with `scene.content` passed as data attribute.

**reader.html**: Same — add mute toggle, include `ambiance.js`, initialize with `scene.content` (for saved stories, `scene.content` is available in template context).

## Project Structure

### Source Code (repository root)

```text
static/
├── audio/                 # New: ambient audio files
│   ├── forest.mp3
│   ├── ocean.mp3
│   ├── dragon.mp3
│   ├── magic.mp3
│   ├── space.mp3
│   ├── city.mp3
│   └── storm.mp3
├── css/style.css          # Add mute toggle styles
└── js/ambiance.js         # New: ambient audio JS module

templates/
├── scene.html             # Add mute toggle + ambiance init
└── reader.html            # Add mute toggle + ambiance init

tests/
└── test_ambiance.py       # New: test mute toggle visibility, data attributes
```
