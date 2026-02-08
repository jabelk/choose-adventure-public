# Quickstart Validation: Multi-Model Image & Video Generation

**Feature**: 013-image-video-gen
**Date**: 2026-02-07

## Prerequisites

- Server running on port 8080
- OpenAI API key configured (OPENAI_API_KEY)
- xAI API key configured (XAI_API_KEY)
- Gemini API key configured (GEMINI_API_KEY) — optional but recommended
- At least one profile with a character and reference photo (from 012-photo-import)

## Validation Steps

### Step 1: Verify Expanded Image Model Selector

1. Go to `http://localhost:8080/kids/`
2. Look at the image model selector
3. **Expected**: See models grouped by provider:
   - **OpenAI**: GPT Image 1 Mini, GPT Image 1, GPT Image 1.5
   - **xAI**: Grok Imagine
   - **Google**: Gemini (if key configured)
4. Verify the default selection is GPT Image 1

### Step 2: Test Each OpenAI Image Model

1. Select "GPT Image 1 Mini", enter a prompt, start a story
2. **Expected**: Image generates successfully, scene view shows "GPT Image 1 Mini" as the model
3. Abandon the story, repeat with "GPT Image 1" and "GPT Image 1.5"
4. **Expected**: All three produce images, with GPT Image 1.5 being noticeably higher quality

### Step 3: Test Grok Imagine Image Generation

1. Select "Grok Imagine", enter a prompt, start a story
2. **Expected**: Image generates successfully via xAI's API
3. Verify the image appears in the scene view and "Grok Imagine" is shown as the model
4. Make a choice and verify the next scene also generates an image with Grok Imagine

### Step 4: Test Reference Photos with New Models

1. Ensure a profile has a character with a reference photo
2. Enable memory mode, select the profile
3. Start a story with "GPT Image 1.5"
4. **Expected**: Image generation uses reference photos (images.edit with input_fidelity="high")
5. Repeat with "GPT Image 1 Mini"
6. **Expected**: Image generation uses reference photos (images.edit without input_fidelity)
7. Repeat with "Grok Imagine"
8. **Expected**: Image generation includes reference photo via xAI's image editing

### Step 5: Verify Video Mode Toggle

1. Go to the home page
2. **Expected**: "Video Mode" toggle is visible (xAI key is configured)
3. If you remove XAI_API_KEY from .env and restart, verify the toggle disappears

### Step 6: Test Video Generation

1. Enable video mode on the home page
2. Select any image model, enter a prompt, start a story
3. **Expected**: Scene shows the static image immediately
4. **Expected**: Below the image, a video loading indicator appears
5. **Expected**: Within ~60 seconds, a playable video clip appears
6. Play the video — verify it's a short animated scene related to the story
7. Make a choice — verify the next scene also gets a video

### Step 7: Test Video Persistence

1. Complete a story with video mode enabled (or save it via gallery)
2. Go to the gallery
3. **Expected**: The story card shows a video indicator/badge
4. Open the story in the reader
5. **Expected**: Each scene's video is playable inline

### Step 8: Test Video Failure/Retry

1. Start a story with video mode on
2. If a video fails (or simulate by temporarily invalidating the xAI key):
3. **Expected**: Static image displays normally, video shows "failed" with a retry button
4. Click retry
5. **Expected**: Video generation restarts

### Step 9: Verify Backward Compatibility

1. Open a previously saved story (from before this feature) in the gallery
2. **Expected**: Story displays normally with images — no broken video elements
3. Start a story with video mode OFF
4. **Expected**: No video generation occurs, story behaves exactly as before

### Step 10: Verify Model Display Names

1. Start stories with different image models
2. Save each to the gallery
3. **Expected**: Gallery cards and reader view show the specific model name (e.g., "GPT Image 1.5", "Grok Imagine") — not generic "DALL-E"

## Quick Smoke Test

For a fast validation, do steps 1, 3, 6, and 9. This confirms:
- Multiple image models are available
- Grok Imagine works for images
- Video generation works end-to-end
- Backward compatibility is maintained
