# Quickstart: Story Gallery

## How to Test

1. Start the server:
   ```bash
   venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8080
   ```

2. Visit http://localhost:8080/kids/ and start a **short** story (3 chapters — fastest to complete).

3. Play through to the ending ("The End" page).

4. After the ending is displayed, verify:
   - A JSON file was created in `data/stories/` with the story's UUID as filename.
   - The file contains story metadata, all scenes, and path_history.

5. Click the "Gallery" link on the home page (or navigate to http://localhost:8080/kids/gallery).

6. Verify:
   - The completed story appears as a card with title, image, prompt, and date.
   - Clicking the card opens the story reader.
   - You can navigate forward/backward through all scenes.
   - The reading order matches the path you originally took.

7. Restart the server and revisit the gallery — the story should still be there.

8. Test tier isolation:
   - Complete a story in `/nsfw/` tier.
   - Visit `/kids/gallery` — the nsfw story should NOT appear.
   - Visit `/nsfw/gallery` — it should appear there.

9. Test empty state:
   - Visit `/nsfw/gallery` before completing any nsfw stories.
   - Verify a friendly "No stories yet" message is shown.
