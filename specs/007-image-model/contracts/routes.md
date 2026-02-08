# Route Contracts: Image Model Selection

## Modified Routes

### POST `/{tier}/story/start` (existing)

**Changes**: Accept a new `image_model` form field.

**Request**: Form data — existing fields plus:
- `image_model` (str, optional): Provider key (e.g., "dalle", "gemini"). Defaults to tier's default_image_model.

**Behavior changes**:
1. Validate the image_model key exists in the image registry and is available (has API key)
2. If image_model is invalid or unavailable, fall back to the tier's default image model
3. If only one image provider is available and no value submitted, use that provider
4. Store the image_model key on the Story object
5. Pass the image_model key to `ImageService.generate_image()` so it uses the correct provider

**Response**: Same as current (redirect to scene page).

### POST `/{tier}/story/choose/{scene_id}/{choice_id}` (existing)

**Changes**: Read image_model from the story session and pass to ImageService.

**Behavior changes**:
1. Get the image_model key from `story_session.story.image_model`
2. Pass it to `ImageService.generate_image()` for the new scene's image

**Response**: Same as current.

### POST `/{tier}/story/image/{scene_id}/retry` (existing)

**Changes**: Read image_model from the story session and pass to ImageService.

**Behavior changes**:
1. Get the image_model key from `story_session.story.image_model`
2. Pass it to `ImageService.generate_image()` for the retry

**Response**: Same as current.

### GET `/{tier}/` (existing — tier home)

**Changes**: Pass available image models and tier default image model to template context.

**Behavior changes**:
1. Query the image model registry for available image models
2. Determine the tier's default image model (fall back to first available if default unavailable)
3. Pass `available_image_models` list and `default_image_model` key to the template
4. Only pass these if more than one image model is available (for conditional rendering)

**Response**: Same as current (renders home.html with additional context).

## No Changes Needed

### GET `/{tier}/story/scene/{scene_id}`

Already passes the full story object to the template. No route change needed.
Template can read `story.image_model` if attribution display is added to scenes.

### GET `/{tier}/gallery`

Already passes story list to template. Stories now have an `image_model` field.
Template just reads it. No route change needed.

### GET `/{tier}/gallery/{story_id}/{scene_index}`

Already passes full saved story to template. Template reads `story.image_model`.
No route change needed.

## Template Changes

### home.html

- Add image model selector section (radio button cards) between model selector and submit button
- Only render when `available_image_models|length > 1`
- Each card shows image model display_name
- Pre-select the tier's default image model
- When only one image provider is available, include a hidden input with that provider's key

### scene.html

- Optionally display image model name in the scene header alongside text model
  (e.g., "Chapter 2 of ~5 · Claude · DALL-E")

### gallery.html

- Display image model name on each story card alongside text model name

### reader.html

- Display image model name in the reader header alongside text model name

## Client-Side Contracts

No new JavaScript needed. The image model selector is a standard HTML radio group.
Form submission sends the selected image_model value as a form field.
