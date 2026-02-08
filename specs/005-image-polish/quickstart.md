# Quickstart: Image Retry & Polish

## How to Test

1. Start the server:
   ```bash
   venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8080
   ```

2. **Test improved loading state**:
   - Visit http://localhost:8080/kids/ and start a short story
   - Observe the image area while it generates
   - Verify: pulsing gradient animation (not just a spinner), progress text visible
   - Verify: when the image arrives, it fades in smoothly (~0.5s)
   - Verify: no layout shift when the image appears (container doesn't resize)

3. **Test retry on failure**:
   - To simulate failure: temporarily set an invalid OpenAI API key, or disconnect from internet
   - Start a story — the image should fail after retries
   - Verify: failed state shows "Image generation failed" message with a "Retry" button
   - Restore the API key / reconnect
   - Click "Retry" — verify it transitions to the generating state
   - Verify: on success, the image fades in

4. **Test regenerate on completed image**:
   - On a scene with a completed image, look for a "Regenerate" button
   - On desktop: hover over the image area to reveal the button
   - Click "Regenerate" — verify the image is replaced with the generating state
   - Wait for the new image to appear

5. **Test duplicate prevention**:
   - While an image is generating, try clicking Retry/Regenerate rapidly
   - Verify: only one generation is in flight (button is disabled during generation)

6. **Test background generation**:
   - Start a story (image starts generating)
   - Quickly click "Go Back" or navigate away
   - Wait ~15 seconds for generation to complete
   - Navigate back to the scene
   - Verify: the image is shown immediately (already generated)

7. **Test gallery reader exclusion**:
   - Complete a story and visit it in the gallery reader
   - Verify: no "Regenerate" button appears on gallery reader images

8. **Test tier theming**:
   - Test in both `/kids/` and `/nsfw/` tiers
   - Verify: the loading animation and buttons use the correct tier colors
