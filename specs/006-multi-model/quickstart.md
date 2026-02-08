# Quickstart: Multi-Model AI

## How to Test

1. **Configure API keys** in `.env`:
   ```bash
   ANTHROPIC_API_KEY=sk-ant-...    # Claude (required — existing)
   OPENAI_API_KEY=sk-...           # GPT + image gen (required — existing)
   GEMINI_API_KEY=AIza...          # Gemini (optional)
   XAI_API_KEY=xai-...             # Grok (optional)
   ```

2. **Install new dependency**:
   ```bash
   venv/bin/pip install google-genai
   ```

3. **Start the server**:
   ```bash
   venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8080
   ```

4. **Test model selector display**:
   - Visit http://localhost:8080/kids/
   - Verify: model selector appears below the length selector
   - Verify: only models with configured API keys are shown
   - Verify: Claude is pre-selected (kids tier default)
   - If only Anthropic + OpenAI keys are set, should see "Claude" and "GPT" cards

5. **Test story with Claude (existing behavior)**:
   - Select "Claude", enter a prompt, start a story
   - Verify: story generates as before
   - Verify: model name "Claude" appears in the scene header
   - Complete the story or navigate a few scenes

6. **Test story with GPT**:
   - Go back to home, select "GPT", enter a prompt, start a story
   - Verify: story generates using GPT (may notice different writing style)
   - Verify: model name "GPT" appears in the scene header

7. **Test story with Gemini** (if GEMINI_API_KEY configured):
   - Select "Gemini", enter a prompt, start a story
   - Verify: story generates and model name shows "Gemini"

8. **Test story with Grok** (if XAI_API_KEY configured):
   - Select "Grok", enter a prompt, start a story
   - Verify: story generates and model name shows "Grok"

9. **Test model attribution in gallery**:
   - Complete a story with a non-Claude model (e.g., GPT)
   - Visit the gallery
   - Verify: story card shows the model name
   - Click into the story reader
   - Verify: reader header shows the model name

10. **Test backward compatibility**:
    - If any pre-existing stories are in the gallery (from before this feature)
    - Verify: they display "Claude" as the model without errors

11. **Test tier defaults**:
    - Visit /kids/ — verify Claude is pre-selected
    - Visit /nsfw/ — verify the configured default is pre-selected
    - If the default model's key is removed, verify fallback to first available

12. **Test no models available**:
    - Temporarily remove all API keys from .env and restart
    - Visit /kids/
    - Verify: error message shown, submit button disabled

13. **Test story resume with model**:
    - Start a story with GPT, navigate a few scenes
    - Close the browser, reopen, visit /kids/
    - Click "Continue" on the resume banner
    - Verify: story continues using GPT (same model)
