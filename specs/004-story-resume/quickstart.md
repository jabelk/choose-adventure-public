# Quickstart: Story Resume

## How to Test

1. Start the server:
   ```bash
   venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8080
   ```

2. Visit http://localhost:8080/kids/ and start a **short** story.

3. Make 1-2 choices to advance the story.

4. Verify auto-save: Check that `data/progress/kids.json` exists and contains the story session data.

5. Close the browser tab completely.

6. Reopen http://localhost:8080/kids/ — verify:
   - A resume banner appears showing the story title
   - "Continue" and "Start Fresh" options are visible

7. Click "Continue" — verify:
   - You're taken to the last scene you were on
   - "Go Back" still works to see previous scenes
   - You can continue making choices

8. Test server restart persistence:
   - Stop the server (Ctrl+C)
   - Restart the server
   - Visit http://localhost:8080/kids/
   - Verify the resume banner still appears
   - Click "Continue" and verify the story is fully intact

9. Test abandon:
   - Return to http://localhost:8080/kids/
   - Click "Start Fresh" on the resume banner
   - Verify the banner disappears and the prompt form is shown
   - Verify `data/progress/kids.json` no longer exists

10. Test completion cleanup:
    - Start a new **short** story
    - Play through to "The End"
    - Visit http://localhost:8080/kids/
    - Verify no resume banner appears
    - Verify the story appears in the gallery
    - Verify `data/progress/kids.json` no longer exists

11. Test tier isolation:
    - Start a story in `/kids/` (don't finish it)
    - Visit `/nsfw/` — verify no resume banner appears
    - Start a story in `/nsfw/` — verify both `kids.json` and `nsfw.json` exist independently

12. Test new story replaces old:
    - With an in-progress kids story, submit a new prompt on the kids home page
    - Verify the old story is replaced (the resume banner, if you go back to home, shows the new story's title)
