# Quickstart: Story Templates

## Prerequisites

- Server running: `venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8080`

## Validation Steps

### Step 1: Template Cards Visible
1. Open `http://localhost:8080/kids/`
2. Verify template cards are displayed above the prompt form
3. Expected: At least 6 template cards visible, each with emoji, title, and description

### Step 2: Template Selection Pre-fills Form
1. Click a template card (e.g., "Treasure Hunt Puppy")
2. Verify the prompt textarea is filled with the template's prompt text
3. Verify the story length selector changes to the template's suggested length
4. Verify the selected template card is visually highlighted
5. Expected: Form is pre-filled, card is highlighted

### Step 3: Template Deselection
1. Click the same template card again (or a "clear" mechanism)
2. Verify the prompt textarea is cleared
3. Verify the story length selector returns to default (medium)
4. Verify no template card is highlighted
5. Expected: Form returns to blank state

### Step 4: Start Story from Template
1. Select a template card
2. Click "Start Adventure" without modifying the prompt
3. Expected: Story generates successfully using the template's prompt

### Step 5: Modify Template Before Starting
1. Select a template card
2. Edit the pre-filled prompt text
3. Click "Start Adventure"
4. Expected: Story generates with the modified prompt

### Step 6: Tier Isolation
1. Open `http://localhost:8080/kids/` and note the template titles
2. Open `http://localhost:8080/nsfw/` and note the template titles
3. Expected: Completely different template sets, no overlap, age-appropriate content per tier

### Step 7: Suggestion Chips Removed
1. On the home page, scroll below the form
2. Expected: No "Need inspiration?" section or suggestion chips visible

### Step 8: Mobile Responsive
1. Resize browser to 375px width (or use mobile responsive mode)
2. Verify template cards stack in a single column
3. Verify all cards are tappable and text is readable
4. Expected: No horizontal overflow, all cards accessible

### Step 9: Switch Between Templates
1. Click template A — verify form fills with A's data
2. Click template B — verify form fills with B's data (replacing A's)
3. Expected: Only one template selected at a time, form always reflects current selection
