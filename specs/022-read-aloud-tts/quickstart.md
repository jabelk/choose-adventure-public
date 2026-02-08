# Quickstart: Read Aloud / TTS Narration

**Feature**: 022-read-aloud-tts
**Date**: 2026-02-07

## Prerequisites

- OpenAI API key configured in `.env` (already set up for images/Whisper)
- Server running: `venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8080`

## Test Scenarios

### Scenario 1: Basic Play Button (US1 - P1)

1. Navigate to `http://localhost:8080/kids/`
2. Start a new story (use any template)
3. Wait for the first scene to load
4. Verify a play/speaker button is visible near the scene text
5. Tap the play button
6. Verify: Audio begins playing within 3 seconds
7. Verify: The button changes to a stop icon
8. Tap the stop button
9. Verify: Audio stops immediately
10. Verify: The button returns to play state

### Scenario 2: Auto-Play on Kids Tier (US2 - P2)

1. Navigate to `http://localhost:8080/kids/`
2. Start a new story
3. Verify: Narration begins automatically when the first scene loads (no tap needed)
4. Make a choice to advance to the next scene
5. Verify: Narration begins automatically on the new scene
6. Toggle auto-play off (small toggle near play button)
7. Navigate to next scene
8. Verify: Narration does NOT auto-play

### Scenario 3: NSFW Tier - No Auto-Play (US2 - P2)

1. Navigate to `http://localhost:8080/nsfw/`
2. Start a new story
3. Verify: Play button is visible but narration does NOT auto-play
4. Tap play button
5. Verify: Audio plays normally

### Scenario 4: Voice Selection (US3 - P3)

1. On any scene page, find the voice selector
2. Note the default voice (kids: Nova, nsfw: Onyx)
3. Select a different voice
4. Tap play
5. Verify: The new voice is used
6. Navigate to the next scene
7. Tap play again
8. Verify: The same voice is still selected (preference persisted)

### Scenario 5: Gallery Reader (US1 - P1)

1. Navigate to the gallery on either tier
2. Open a completed story
3. Verify: Play button is visible on the gallery reader scene
4. Tap play
5. Verify: Scene text is read aloud

### Scenario 6: No API Key (Edge Case)

1. Temporarily remove `OPENAI_API_KEY` from `.env`
2. Restart the server
3. Navigate to any scene
4. Verify: No play button appears (feature silently absent)

### Scenario 7: Navigation Stops Audio (Edge Case)

1. Start playing narration on a scene
2. While audio is playing, make a choice (tap a choice button)
3. Verify: Audio from the previous scene stops
4. Verify: New scene loads (with auto-play if kids tier)

### Scenario 8: Sentence Highlighting (US4 - P4, Stretch)

1. On any scene, tap play
2. Verify: The currently spoken sentence is highlighted in the text
3. Verify: Highlighting advances as narration progresses
4. Tap stop
5. Verify: Highlighting is cleared

## Expected Results

| Scenario | Expected | Tier |
|----------|----------|------|
| Play button visible | On every scene (active + gallery) | Both |
| Audio plays on tap | Within 3 seconds | Both |
| Auto-play on load | Immediate narration start | Kids only (default) |
| Voice persists | Same voice across scenes | Both |
| Stop on navigate | Audio stops, no overlap | Both |
| No API key | Play button hidden, no error | Both |
