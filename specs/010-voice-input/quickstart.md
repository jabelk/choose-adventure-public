# Quickstart: Voice Input

## How to Test

1. **Start the server**:
   ```bash
   venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8080
   ```

2. **Test browser-native voice input (US1 — Chrome/Safari)**:
   - Visit http://localhost:8080/kids/ in Chrome or Safari
   - Verify: A microphone button appears next to the prompt text area
   - Click the microphone button
   - Verify: Browser requests microphone permission (first time only)
   - Grant permission and speak a story prompt (e.g., "A brave knight and a friendly dragon")
   - Verify: Text appears in the prompt text area as you speak
   - Stop speaking (or click the microphone button again)
   - Verify: Button returns to idle state, transcribed text remains in the text area
   - Click "Begin Adventure"
   - Verify: Story starts normally using the transcribed text

3. **Test append behavior (FR-005)**:
   - Type some text in the prompt area (e.g., "Once upon a time")
   - Click the microphone button and speak additional text
   - Verify: Spoken text is appended after the typed text, not replacing it

4. **Test auto-stop (FR-007)**:
   - Click the microphone button and don't speak
   - Wait ~10 seconds
   - Verify: Recording stops automatically, button returns to idle

5. **Test server-side fallback (US2 — Firefox)**:
   - Visit http://localhost:8080/kids/ in Firefox
   - Verify: Microphone button is visible (server fallback is available since OpenAI API key is configured)
   - Click the microphone button
   - Grant microphone permission and speak a story prompt
   - Click the microphone button again to stop recording
   - Verify: A loading indicator appears while audio is being transcribed
   - Verify: Transcribed text appears in the prompt text area within ~10 seconds

6. **Test permission denied (Edge case)**:
   - Click the microphone button
   - Deny microphone permission when prompted
   - Verify: An error message appears explaining that microphone access is needed
   - Verify: The prompt text area and form still work normally for typing

7. **Test without OpenAI API key (FR-013)**:
   - Temporarily unset the OpenAI API key environment variable
   - Restart the server
   - Visit in Firefox (no native speech recognition)
   - Verify: Microphone button is hidden (no voice input available)
   - Visit in Chrome
   - Verify: Microphone button is visible (browser-native still works without API key)

8. **Test mobile (FR-012)**:
   - Open the site on a mobile device (same LAN)
   - Verify: Microphone button is visible and tappable
   - Tap and speak
   - Verify: Transcription works on mobile browser
