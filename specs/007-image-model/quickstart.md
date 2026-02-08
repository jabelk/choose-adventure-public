# Quickstart: Image Model Selection

## How to Test

1. **Configure API keys** in `.env`:
   ```bash
   ANTHROPIC_API_KEY=sk-ant-...    # Claude (required — existing)
   OPENAI_API_KEY=sk-...           # GPT + DALL-E image gen (required — existing)
   GEMINI_API_KEY=AIza...          # Gemini text + image gen (optional)
   XAI_API_KEY=xai-...             # Grok (optional)
   ```

2. **Start the server**:
   ```bash
   venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8080
   ```

3. **Test image model selector display (both keys configured)**:
   - Ensure both OPENAI_API_KEY and GEMINI_API_KEY are set
   - Visit http://localhost:8080/kids/
   - Verify: image model selector appears below the text model selector
   - Verify: "DALL-E" and "Gemini" cards are shown
   - Verify: "DALL-E" is pre-selected (kids tier default)

4. **Test image model selector hidden (single key)**:
   - Remove GEMINI_API_KEY from .env, restart server
   - Visit http://localhost:8080/kids/
   - Verify: no image model selector appears
   - Verify: text model selector still appears normally

5. **Test story with DALL-E images (existing behavior)**:
   - With both keys configured, select "DALL-E", start a story
   - Verify: images generate as before using OpenAI
   - Verify: image model name visible in scene/gallery display

6. **Test story with Gemini images**:
   - Select "Gemini" as the image model, start a story
   - Verify: images generate using Gemini (may notice different art style)
   - Verify: image model name "Gemini" visible in display

7. **Test image retry preserves model**:
   - Start a story with Gemini images
   - If an image fails, click retry
   - Verify: retry uses Gemini (not falling back to DALL-E)
   - Regenerate a completed image
   - Verify: regenerated image uses Gemini

8. **Test model attribution in gallery**:
   - Complete a story with Gemini images
   - Visit the gallery
   - Verify: story card shows both text model and image model names
   - Click into the story reader
   - Verify: reader header shows image model name

9. **Test backward compatibility**:
   - If any pre-existing stories are in the gallery (from before this feature)
   - Verify: they display "DALL-E" as the image model without errors

10. **Test tier defaults**:
    - Visit /kids/ — verify DALL-E is pre-selected as image model
    - Visit /nsfw/ — verify the configured default is pre-selected

11. **Test story resume with image model**:
    - Start a story with Gemini images, navigate a few scenes
    - Close the browser, reopen, visit /kids/
    - Click "Continue" on the resume banner
    - Verify: story continues using Gemini for images
