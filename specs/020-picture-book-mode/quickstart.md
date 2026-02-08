# Quickstart: Picture Book Mode

## Test Scenario 1: Picture Book Mode Activates

1. Go to `/kids/` (kids tier home page)
2. Enter any story prompt
3. Set protagonist age to "Toddler (3-4)" or "Young Child (5-6)"
4. Click "Start Adventure"
5. **Expected**: Scene page shows 3 image placeholders (1 main + 2 extra) all in loading state
6. **Expected**: Images appear independently as they complete
7. **Expected**: Extra images appear below the main image in a vertical stack

## Test Scenario 2: Standard Mode Unchanged

1. Go to `/kids/` and start a story with age set to "Any" or "Older Child (7-9)"
2. **Expected**: Scene shows only 1 image (standard behavior)
3. Go to `/nsfw/` and start a story with any age
4. **Expected**: Scene shows only 1 image (picture book never activates on adult tier)

## Test Scenario 3: Extra Images Use Fast Model

1. Start a kids story with "Toddler" age and select a slow image model (e.g., gpt-image-1)
2. **Expected**: Main image uses gpt-image-1
3. **Expected**: Extra images use gpt-image-1-mini (or fall back to user's model if mini unavailable)

## Test Scenario 4: Independent Retry

1. Start a picture book mode story
2. Wait for images to load
3. If an extra image fails, click its retry button
4. **Expected**: Only that image retries; other images remain as-is

## Test Scenario 5: Gallery Persistence

1. Complete a picture book mode story (reach an ending)
2. Go to gallery and open the saved story
3. **Expected**: All scenes show all 3 images (main + extras) that were successfully generated

## Test Scenario 6: Continue Story

1. Start a picture book mode story
2. Make a choice to continue
3. **Expected**: Next scene also shows 3 images (picture book mode persists across scenes)

## Test Scenario 7: Custom Choice

1. Start a picture book mode story
2. Use the custom text input to write your own choice
3. **Expected**: Next scene still shows 3 images
