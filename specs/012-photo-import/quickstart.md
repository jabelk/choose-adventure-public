# Quickstart Validation: Photo Import

**Feature**: 012-photo-import
**Date**: 2026-02-07

## Prerequisites

- Server running on port 8080
- At least one profile with a character created (from 011-memory-mode)
- A JPEG or PNG photo file available for upload (any photo will do)
- OpenAI API key configured (for DALL-E image generation with reference)

## Validation Steps

### Step 1: Navigate to Profile Edit Page
1. Go to `http://localhost:8080/kids/profiles`
2. Click on an existing profile (or create one first)
3. Verify the profile edit page loads with the character list

### Step 2: Upload a Photo for a Character
1. On the profile edit page, find a character card
2. Click "Upload Photo" or use the file input
3. Select a JPEG or PNG file (under 5 MB)
4. Submit the upload
5. **Expected**: Page reloads, thumbnail of the uploaded photo appears on the character card

### Step 3: Verify Photo Persistence
1. Refresh the page
2. **Expected**: The thumbnail is still visible — photo persists across page loads
3. Check that the file exists on disk: `data/photos/kids/{profile_id}/{character_id}.jpg`

### Step 4: Replace a Photo
1. Upload a different photo for the same character
2. **Expected**: New thumbnail replaces the old one
3. Verify only one photo file exists on disk for that character

### Step 5: Remove a Photo
1. Click "Remove Photo" on the character card
2. **Expected**: Thumbnail disappears, character card shows no image
3. Verify the photo file is deleted from disk

### Step 6: Validate Upload Constraints
1. Try uploading a `.gif` file → **Expected**: Error message "Only JPEG and PNG files are supported"
2. Try uploading a file > 5 MB → **Expected**: Error message indicating size limit
3. Try uploading a very small image (< 256x256) → **Expected**: Warning message (non-blocking, photo still saved)

### Step 7: Start a Story with Memory Mode + Photo
1. Upload a photo for a character
2. Go to the tier home page
3. Toggle memory mode ON, select the profile
4. Start a story
5. **Expected**: Image generation uses the reference photo — the AI-generated image should incorporate the likeness from the uploaded photo

### Step 8: Start a Story Without Memory Mode
1. Go to the tier home page
2. Keep memory mode OFF
3. Start a story with the same prompt
4. **Expected**: Image generation does NOT use reference photos — standard AI-generated images

### Step 9: Verify Photo Cleanup on Delete
1. Add a photo to a character
2. Delete the character
3. **Expected**: Photo file is removed from disk
4. Alternatively: delete the entire profile and verify all character photos are cleaned up

### Step 10: Verify Tier Isolation
1. Upload a photo in the kids tier
2. Try accessing it via nsfw tier URL: `http://localhost:8080/nsfw/photos/{profile_id}/{character_id}`
3. **Expected**: 404 — the photo is not accessible from the other tier

## Quick Smoke Test

For a fast validation, do steps 1-3 and 7. This confirms:
- Photo upload works
- Photos persist
- Photos influence image generation when memory mode is on
