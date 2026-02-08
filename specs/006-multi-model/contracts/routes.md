# Route Contracts: Multi-Model AI

## Modified Routes

### POST `/{tier}/story/start` (existing)

**Changes**: Accept a new `model` form field.

**Request**: Form data — existing fields plus:
- `model` (str, required): Provider key (e.g., "claude", "gpt", "gemini", "grok")

**Behavior changes**:
1. Validate the model key exists in the registry and is available (has API key)
2. If model is invalid or unavailable, fall back to the tier's default model
3. Store the model key on the Story object
4. Pass the model key to `StoryService.generate_scene()` so it uses the correct provider

**Response**: Same as current (redirect to scene page).

### POST `/{tier}/story/choose/{scene_id}/{choice_id}` (existing)

**Changes**: Read model from the story session and pass to generate_scene().

**Behavior changes**:
1. Get the model key from `story_session.story.model`
2. Pass it to `StoryService.generate_scene()` for the next scene

**Response**: Same as current.

### GET `/{tier}/` (existing — tier home)

**Changes**: Pass available models and tier default model to template context.

**Behavior changes**:
1. Query the model registry for available models (those with configured API keys)
2. Determine the tier's default model (fall back to first available if default unavailable)
3. Pass `available_models` list and `default_model` key to the template

**Response**: Same as current (renders home.html with additional context).

## No Changes Needed

### GET `/{tier}/story/scene/{scene_id}`

Already passes the full story object to the template. The template just needs
to read `story.model` to display the model name. No route change needed.

### GET `/{tier}/gallery`

Already passes story list to template. Stories now have a `model` field.
Template just reads it. No route change needed.

### GET `/{tier}/gallery/{story_id}/{scene_index}`

Already passes full saved story to template. The template reads `story.model`.
No route change needed.

## Template Changes

### home.html

- Add model selector section (radio button cards) between length selector and submit button
- Each card shows model display_name
- Pre-select the tier's default model
- If no models are available, show an error and disable the submit button

### scene.html

- Display model name in the scene header (e.g., next to chapter info)

### gallery.html

- Display model name on each story card

### reader.html

- Display model name in the reader header

## Client-Side Contracts

No new JavaScript needed. The model selector is a standard HTML radio group,
same as the length selector. Form submission sends the selected model value
as a form field.
