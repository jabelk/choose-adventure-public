# Quickstart: Memory Mode

## Prerequisites

- Server running: `venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8080`
- At least one AI API key configured (ANTHROPIC_API_KEY or OPENAI_API_KEY)

## Validation Steps

### Step 1: Navigate to Profile Management

1. Open browser to `http://localhost:8080/kids/`
2. Click the "Profiles" link on the home page
3. **Verify**: Profile management page loads at `/kids/profiles` with an empty profile list and a "Create Profile" form

### Step 2: Create a Profile

1. On the profiles page, enter:
   - Name: "Lily's Profile"
   - Themes: "dinosaurs, space, underwater"
   - Art Style: "bright watercolor"
   - Tone: "silly and lighthearted"
   - Story Elements: "talking animals, treasure hunts"
2. Click "Create Profile"
3. **Verify**: Profile appears in the list with all entered data. Page refreshes and profile persists.

### Step 3: Add Characters to Profile

1. Click "Edit" on Lily's profile
2. In the character section, add:
   - Name: "Lily"
   - Description: "A curious 5-year-old girl with pigtails who loves dinosaurs and has a pet cat named Whiskers"
3. Click "Add Character"
4. **Verify**: Character appears in the profile's character list

### Step 4: Create a Second Profile and Link Characters

1. Go back to `/kids/profiles`
2. Create another profile:
   - Name: "Rose's Profile"
   - Themes: "princesses, magic, gardens"
3. Edit Rose's profile, add a character:
   - Name: "Rose"
   - Description: "Lily's 3-year-old sister, loves flowers and magic wands"
   - Linked Profile: Select "Lily's Profile" from dropdown
4. **Verify**: Character shows link to Lily's profile

### Step 5: Start a Story with Memory Mode Off

1. Go to `/kids/`
2. **Verify**: Memory Mode toggle is visible (since profiles exist)
3. Leave Memory Mode OFF
4. Enter prompt: "An adventure in a magical garden"
5. Start the story
6. **Verify**: Story generates normally without any profile influence (no mention of Lily, Rose, dinosaurs, etc.)

### Step 6: Start a Story with Memory Mode On

1. Go to `/kids/`
2. Toggle Memory Mode ON
3. Select "Lily's Profile" from the dropdown
4. Enter prompt: "An adventure in a magical garden"
5. Start the story
6. **Verify**: Story reflects Lily's preferences — look for:
   - Dinosaur or space themes woven in
   - Silly, lighthearted tone
   - Characters from the profile (Lily, Whiskers the cat)
   - Image style influenced by "bright watercolor"

### Step 7: Verify Cross-Profile Characters

1. Go to `/kids/`
2. Toggle Memory Mode ON
3. Select "Rose's Profile"
4. Start a story about "A day in a magical kingdom"
5. **Verify**: Rose appears in the story, and since Rose's profile links to Lily's, Lily may also appear as a character

### Step 8: Verify Tier Isolation

1. Go to `/nsfw/profiles`
2. **Verify**: No kids-tier profiles are visible
3. Create an nsfw profile with different preferences
4. Go back to `/kids/profiles`
5. **Verify**: The nsfw profile is not visible

### Step 9: Verify Profile Deletion Cleanup

1. Go to `/kids/profiles`
2. Delete "Lily's Profile"
3. Edit "Rose's Profile"
4. **Verify**: Rose's character that linked to Lily's profile now shows no link (graceful degradation)

### Step 10: Verify Persistence

1. Stop the server (Ctrl+C)
2. Restart the server
3. Go to `/kids/profiles`
4. **Verify**: Rose's profile and all its data are intact
