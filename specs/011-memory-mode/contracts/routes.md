# Route Contracts: Memory Mode

## New Routes

### GET `/{tier}/profiles` (new)

**Purpose**: Display the profile management page for the current tier.

**Request**: No parameters.

**Response**: HTML page listing all profiles for this tier with options to create, edit, and delete.

---

### POST `/{tier}/profiles/create` (new)

**Purpose**: Create a new profile in the current tier.

**Request**: Form data

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| name | string | Yes | Profile display name (max 100 chars) |
| themes | string | No | Comma-separated themes (e.g., "dinosaurs, space") |
| art_style | string | No | Preferred art style (max 200 chars) |
| tone | string | No | Preferred tone (max 200 chars) |
| story_elements | string | No | Comma-separated story elements |

**Response**: Redirect to `/{tier}/profiles` on success. Redirect to `/{tier}/profiles?error=...` on validation failure.

---

### GET `/{tier}/profiles/{profile_id}` (new)

**Purpose**: Display the edit form for a specific profile, including its characters.

**Request**: No parameters (profile_id in URL path).

**Response**: HTML page with the profile edit form and character list. Returns 303 redirect to `/{tier}/profiles` if profile not found.

---

### POST `/{tier}/profiles/{profile_id}/update` (new)

**Purpose**: Update an existing profile's preferences.

**Request**: Form data (same fields as create)

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| name | string | Yes | Profile display name |
| themes | string | No | Comma-separated themes |
| art_style | string | No | Preferred art style |
| tone | string | No | Preferred tone |
| story_elements | string | No | Comma-separated story elements |

**Response**: Redirect to `/{tier}/profiles/{profile_id}` on success.

---

### POST `/{tier}/profiles/{profile_id}/delete` (new)

**Purpose**: Delete a profile and clean up references.

**Request**: No body (profile_id in URL path).

**Behavior**:
1. Delete the profile JSON file from disk
2. For any characters in other same-tier profiles that reference this profile via `linked_profile_id`, set that field to null

**Response**: Redirect to `/{tier}/profiles`.

---

### POST `/{tier}/profiles/{profile_id}/characters/add` (new)

**Purpose**: Add a character to a profile.

**Request**: Form data

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| name | string | Yes | Character name (max 100 chars) |
| description | string | Yes | Character description (max 500 chars) |
| linked_profile_id | string | No | UUID of another profile in the same tier to link |

**Response**: Redirect to `/{tier}/profiles/{profile_id}`.

**Error**: Returns error if profile already has 10 characters (max limit).

---

### POST `/{tier}/profiles/{profile_id}/characters/{character_id}/update` (new)

**Purpose**: Update a character's details.

**Request**: Form data

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| name | string | Yes | Character name |
| description | string | Yes | Character description |
| linked_profile_id | string | No | UUID of another profile to link (empty string to unlink) |

**Response**: Redirect to `/{tier}/profiles/{profile_id}`.

---

### POST `/{tier}/profiles/{profile_id}/characters/{character_id}/delete` (new)

**Purpose**: Remove a character from a profile.

**Request**: No body.

**Response**: Redirect to `/{tier}/profiles/{profile_id}`.

---

## Modified Routes

### POST `/{tier}/story/start` (existing — modified)

**New form fields**:

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| memory_mode | string | No | "on" if memory mode is toggled on (checkbox value) |
| profile_id | string | No | UUID of the selected profile (required if memory_mode is "on") |

**Behavior change**:
- If `memory_mode` is "on" and a valid `profile_id` is provided, load the profile, build the preference context, and augment `content_guidelines` and `image_style` before passing to the story service.
- Store the `profile_id` on the Story model for the session.
- On subsequent scene generation calls (make_choice), re-load the profile from the Story model's `profile_id` and re-apply preferences.

---

## Modified Templates

### home.html (modified)

- Add a "Memory Mode" toggle (checkbox) below the story length selector
- When toggled on, show a profile dropdown populated with profiles for this tier
- When no profiles exist, hide the toggle entirely
- Profile list is passed to the template via the route handler

### New Templates

### profiles.html (new)

- Profile list view with create form
- Each profile shows name, themes, art style, tone, story elements, character count
- Edit and delete buttons per profile
- Link back to home page

### profile_edit.html (new)

- Edit form for profile preferences
- Character list with add/edit/delete forms
- Profile linking dropdown for characters (filtered to same-tier profiles, excluding current profile)
