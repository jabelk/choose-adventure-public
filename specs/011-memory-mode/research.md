# Research: Memory Mode

## Decision 1: Storage Format

**Decision**: JSON files on disk, one file per profile, stored in `data/profiles/{tier}/`

**Rationale**: Matches the existing gallery persistence pattern (`data/stories/`, `data/progress/`). Pydantic models serialize/deserialize natively with `model_dump_json()` and `model_validate()`. No new dependencies. Files are human-readable and portable per the constitution's Archival by Design principle.

**Alternatives considered**:
- SQLite: Overkill for <20 profiles per tier. Adds a dependency and breaks the flat-file pattern used everywhere else.
- In-memory only: Doesn't survive server restarts (violates FR-002).

## Decision 2: Prompt Injection Strategy

**Decision**: Build a "profile context" string and prepend it to the system prompt, after tier content_guidelines but before the story generation instructions. For image style, append profile art style preferences to the existing `image_style` parameter.

**Rationale**: The story service already supports `content_guidelines` (prepended to system prompt) and `image_style` (appended to image prompts). Profile preferences are the same pattern — they augment the existing prompt construction, not replace it. This keeps the change minimal and non-breaking.

**Alternatives considered**:
- Separate system message: Would require changing the provider API call signatures. Unnecessary complexity.
- User message injection: Less authoritative than system prompt for shaping AI behavior. Preferences belong in the system context.

## Decision 3: Profile-Story Association

**Decision**: Pass the selected profile ID as a form field at story start. The route handler loads the profile, builds the prompt context, and passes augmented `content_guidelines` and `image_style` to the story service. The profile ID is stored on the Story model so it persists across the session.

**Rationale**: The story service doesn't need to know about profiles directly. The route handler resolves the profile to prompt text, keeping the story service's interface unchanged. Storing profile_id on the Story model means subsequent scene generation calls can re-load the profile for consistency.

**Alternatives considered**:
- Store full profile text on Story model: Wastes space and becomes stale if profile is edited mid-story. Better to re-read the profile each time.
- Pass profile to story service: Would couple the story service to the profile system. Better to keep it at the route layer.

## Decision 4: Cross-Profile Character References

**Decision**: A character has an optional `linked_profile_id` field. When building the prompt context for an active profile, the system loads any linked profiles (same tier only) and includes their characters in the prompt. Only one level of linking is followed (no recursive chains).

**Rationale**: Simple and predictable. The user's use case is "my two daughters appear in each other's stories" — one level of linking covers this. Recursive linking adds complexity with minimal value and risks circular references.

**Alternatives considered**:
- Recursive linking: Could create infinite loops. Not needed for the stated use case.
- Explicit character sharing (copy characters between profiles): Duplicates data and risks divergence. Linking is cleaner.

## Decision 5: Profile Management UI

**Decision**: A dedicated profile management page at `/{tier}/profiles` with a list view and inline create/edit forms. Characters are managed within the profile edit view. No separate character management page.

**Rationale**: Profiles and characters are tightly coupled — a character only exists within a profile. A single page with profile CRUD and nested character CRUD keeps the UI simple. Matches the app's existing pattern of server-rendered Jinja2 templates with form submissions.

**Alternatives considered**:
- Modal dialogs: More complex JS, not consistent with the app's current form-based interaction pattern.
- Separate character page: Unnecessary navigation overhead for a small feature.

## Decision 6: Memory Mode Toggle UX

**Decision**: A checkbox toggle on the home page below the prompt textarea. When checked, a profile dropdown appears. Both fields are submitted as form data with the story start request. When unchecked, no profile fields are sent.

**Rationale**: Keeps it simple — a single toggle and dropdown. No JavaScript state management beyond show/hide. The form already has length, model, and image_model selectors, so this follows the same pattern.

**Alternatives considered**:
- Always show profile dropdown: Confusing when the user doesn't want profile influence. Toggle makes intent explicit.
- Separate "start with profile" button: Too much UI surface for a simple on/off feature.
