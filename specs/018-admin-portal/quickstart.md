# Quickstart: Admin Portal

**Feature**: 018-admin-portal

## How to Test

### Prerequisites

- App running locally: `venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8080`
- Or on NUC via Docker: `ssh jabelk@warp-nuc "cd ~/choose-adventure && docker compose up -d"`

### Test Scenarios

#### 1. Storage Dashboard (US1)

1. Navigate to `http://localhost:8080/admin`
2. Verify the dashboard shows:
   - Story count (should match number of `.json` files in `data/stories/`)
   - Image count (should match number of `.png` files in `static/images/`)
   - Video count (should match number of `.mp4` files in `static/videos/`)
   - In-progress count (should match number of `.json` files in `data/progress/`)
   - Disk sizes for each category
3. With empty directories, all counts should be 0

#### 2. Story Management (US2)

1. Create a story through the normal UI (any tier)
2. Complete the story so it saves to gallery
3. Visit `/admin` — verify the story appears in the list
4. Click delete on the story
5. Confirm the dialog
6. Verify: story disappears from list, JSON file removed from `data/stories/`, associated images removed from `static/images/`, associated videos removed from `static/videos/`

#### 3. Orphan Cleanup (US3)

1. Manually place a file `test-orphan.png` in `static/images/`
2. Visit `/admin` — verify "1 orphaned image" appears
3. Click "Clean Up Orphans" and confirm
4. Verify `test-orphan.png` is deleted
5. Verify legitimate story images are NOT deleted

#### 4. In-Progress Management (US4)

1. Start a story through the normal UI but don't complete it
2. Visit `/admin` — verify the in-progress entry appears with tier name and prompt
3. Click delete on the in-progress entry
4. Confirm the dialog
5. Verify the progress file is removed from `data/progress/`

#### 5. Edge Cases

- Place a corrupted (non-JSON) file in `data/stories/` — admin page should show it with an error indicator, and it should be deletable
- Delete a story while its image is still generating — should succeed without crashing
