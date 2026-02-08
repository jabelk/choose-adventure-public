# Quickstart: Direct Image Upload

**Feature**: 019-direct-image-upload

## Prerequisites

- App running locally: `venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8080`
- 1-3 test images (JPEG or PNG, under 10MB each) available on your computer

## Test Scenarios

### Scenario 1: Upload photos and start a story

1. Navigate to `http://localhost:8080/kids/` (or any tier)
2. Enter a story prompt (e.g., "A magical adventure in a forest")
3. In the "Reference Photos" section, click "Choose Files" or drag-and-drop 1-3 images
4. Verify thumbnail previews appear for each selected image
5. Click "Start Adventure"
6. Wait for the first scene to load
7. Verify the scene image incorporates elements from the uploaded photos
8. Navigate through 2-3 choices and verify subsequent scene images also use the reference photos

**Expected**: Every generated image in the story uses the uploaded photos as references.

### Scenario 2: Thumbnail preview and removal

1. Navigate to the story start form
2. Select 3 photos
3. Verify 3 thumbnails appear with remove (X) buttons
4. Click remove on the middle photo
5. Verify only 2 thumbnails remain
6. Try to add 2 more photos (should be blocked at 3 max)
7. Add 1 more photo — verify it appears as the 3rd thumbnail

**Expected**: Thumbnails update live. Max 3 photos enforced.

### Scenario 3: No photos (regression test)

1. Navigate to the story start form
2. Do NOT upload any photos
3. Start a story as normal
4. Verify the story works identically to before — images generate without reference photos

**Expected**: Zero regression when no photos uploaded.

### Scenario 4: Direct upload overrides memory mode

1. Navigate to the story start form
2. Enable memory mode and select a profile that has character photos
3. Also upload 1-2 direct reference photos
4. Start the story
5. Verify the generated images use the directly uploaded photos (not the profile photos)

**Expected**: Direct uploads take priority over profile photos.

### Scenario 5: Invalid file handling

1. Try to upload a PDF or text file — should be rejected
2. Try to upload an image larger than 10MB — should be rejected with a message
3. Try to upload 4 images — should be blocked at 3 max

**Expected**: Clear error messages for invalid uploads. Form does not submit with invalid files.

### Scenario 6: Cleanup verification

1. Upload photos and start a story
2. Note the session ID from the cookie or URL
3. Complete the story (save to gallery) or start a new story
4. Check `data/uploads/` — the previous session's directory should be cleaned up

**Expected**: Temp files are removed when the session ends.

## Verification Checklist

- [ ] Upload area appears on story start form
- [ ] Drag-and-drop works
- [ ] Click-to-browse works
- [ ] Thumbnails show for selected files
- [ ] Remove button works on thumbnails
- [ ] Max 3 files enforced
- [ ] Max 10MB per file enforced
- [ ] JPEG/PNG only enforced
- [ ] Story generates with reference images in every scene
- [ ] Story works normally without any uploads
- [ ] Direct uploads override memory mode photos
- [ ] Temp files cleaned up after story ends
- [ ] Works on mobile (tap-to-select)
