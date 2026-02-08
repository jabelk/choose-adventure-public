# Quickstart: Story Branching Explorer

## How to Test

1. **Start the server**:
   ```bash
   venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8080
   ```

2. **Test basic branching (US1 — P1)**:
   - Visit http://localhost:8080/kids/
   - Start a new story, advance through 2-3 scenes making choices
   - Click "Go Back" to return to a previous scene
   - Select a DIFFERENT choice than the one you originally picked
   - Verify: A new scene generates (new branch created)
   - Click "Go Back" again to the branch point
   - Verify: The original choice shows an "explored" indicator
   - Select the original choice again
   - Verify: You navigate to the existing scene (no re-generation)

3. **Test explored choice indicators (FR-003)**:
   - At any scene with choices, pick one
   - Go back to that scene
   - Verify: The choice you already took shows an "explored" indicator (checkmark or label)
   - Verify: Unexplored choices have no indicator

4. **Test tree map during active play (US2 — P2)**:
   - With a branched story in progress, click "Story Map" button
   - Verify: A tree diagram appears showing all explored scenes
   - Verify: The current scene is highlighted (bold/colored node)
   - Verify: The current path from root to current scene is distinctly styled
   - Click a different node in the tree
   - Verify: You navigate to that scene
   - Verify: The tree map updates to highlight the new current position

5. **Test story completion with branches**:
   - Continue a branched story until one branch reaches an ending
   - Verify: Story is saved to the gallery
   - Visit the gallery
   - Verify: The story card appears normally

6. **Test gallery reader with tree map (US3 — P3)**:
   - Open a completed branched story from the gallery
   - Verify: The tree map appears showing all explored branches
   - Click a scene node on a different branch
   - Verify: The reader navigates to that scene
   - Verify: The tree map highlights the new position

7. **Test backward compatibility**:
   - If pre-existing saved stories exist (from before branching)
   - Open one in the gallery reader
   - Verify: The tree map shows a single linear path (no errors)
   - Verify: Navigation between scenes works normally

8. **Test progress save/resume with branches**:
   - Start a story, create at least one branch
   - Close the browser
   - Reopen and visit http://localhost:8080/kids/
   - Click "Continue" on the resume banner
   - Verify: All explored branches are preserved
   - Open the tree map
   - Verify: All previously explored branches appear

9. **Test deep branching**:
   - Go back to the very first scene and pick a different choice
   - Verify: An entirely new sub-tree generates from scene 1
   - Verify: The tree map correctly shows the deep branching

10. **Test tree map with single-path story (no branches)**:
    - Start a new story and advance linearly (no going back)
    - Open the tree map
    - Verify: Shows a single straight line of nodes
    - Click any node to jump to that scene
