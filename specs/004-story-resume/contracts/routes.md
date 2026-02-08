# Route Contracts: Story Resume

## New Routes

### POST `/{tier}/story/abandon`

**Purpose**: Explicitly abandon the current in-progress story.

**Request**: No body (form POST from button).

**Behavior**:
1. Delete the progress file for this tier (`data/progress/{tier_name}.json`)
2. Delete the in-memory session
3. Delete the session cookie
4. Redirect to `/{tier}/` (home page)

**Response**: 303 redirect to tier home page.

### GET `/{tier}/story/resume`

**Purpose**: Restore an in-progress story from disk and redirect to the current scene.

**Request**: No parameters.

**Behavior**:
1. Load the StorySession from `data/progress/{tier_name}.json`
2. Create a new in-memory session from the loaded data
3. Set the session cookie
4. Redirect to `/{tier}/story/scene/{current_scene_id}`

**Response**: 303 redirect to the current scene. If no progress file exists or it's corrupted, redirect to `/{tier}/`.

**Error handling**: If the progress file is corrupted, log a warning, delete the file, and redirect to the home page.

## Modified Routes

### GET `/{tier}/` (tier home)

**Current behavior**: Renders home.html with prompt form.

**New behavior**: Before rendering, check if a progress file exists for this tier. If so, load the story title and pass `resume_story` context to the template:
- `resume_story.title` — the story title to display in the banner
- `resume_story.prompt` — the original prompt (for context)
- `resume_story.scene_count` — number of scenes played so far

The template shows a resume banner above the prompt form when `resume_story` is set.

### POST `/{tier}/story/start`

**Current behavior**: Generates first scene and creates session.

**New behavior**: Before generating, delete any existing progress file for this tier (FR-009). After generating and creating the session, save progress to disk (unless the first scene is an ending, in which case only the gallery save happens).

### POST `/{tier}/story/choose/{scene_id}/{choice_id}`

**Current behavior**: Generates next scene.

**New behavior**: After updating the session, save progress to disk. If the new scene is an ending, delete the progress file instead (the gallery save already happens).

### POST `/{tier}/story/back`

**Current behavior**: Navigates backward in path history.

**New behavior**: After updating the session, save progress to disk.
