# Quickstart: Story Export

## How to Test

1. **Start the server**:
   ```bash
   venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8080
   ```

2. **Test HTML export from gallery list (US1)**:
   - Visit http://localhost:8080/kids/gallery
   - If no stories exist, create and complete one first (start story, make choices until ending)
   - Find a completed story card
   - Click "Export HTML" button
   - Verify: A `.html` file downloads
   - Open the downloaded file directly in a browser (double-click, no server)
   - Verify: Story title, prompt, and date appear
   - Verify: All scenes have text and images (or placeholders for missing images)
   - Verify: No broken images or missing content

3. **Test HTML export branch navigation (US1 — FR-004)**:
   - Export a story that has 2+ branches
   - Open the HTML file in a browser
   - Verify: A tree/navigation panel shows all explored branches
   - Click a different branch in the navigation
   - Verify: The view changes to show that branch's scene
   - Navigate through multiple branches
   - Verify: All explored branches are accessible

4. **Test HTML export from reader view (FR-001)**:
   - Open a completed story in the gallery reader
   - Click the "Export HTML" button in the reader
   - Verify: Same HTML file downloads as from the gallery list

5. **Test PDF export (US2)**:
   - From the gallery, click "Export PDF" on a completed story
   - Verify: A `.pdf` file downloads
   - Open the PDF
   - Verify: Title page shows story title, prompt, and date
   - Verify: A branch overview/table of contents appears
   - Verify: Main path scenes appear first with images and text
   - Verify: Alternate branches appear after, clearly labeled

6. **Test PDF with missing images (FR-008)**:
   - If you have a story with a failed image (or manually delete an image file from `static/images/`)
   - Export as PDF
   - Verify: A placeholder appears instead of a broken reference
   - Export as HTML
   - Verify: A placeholder appears instead of a broken image

7. **Test linear story export (FR-010)**:
   - Create and complete a story without branching (no going back)
   - Export as HTML
   - Verify: Shows a simple linear story, tree shows single path
   - Export as PDF
   - Verify: Scenes appear in order, no branch labels

8. **Test export button visibility**:
   - Verify: Export buttons appear only for completed gallery stories
   - Verify: No export option appears on the home page or for in-progress stories
