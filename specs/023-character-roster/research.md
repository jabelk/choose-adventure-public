# Research: Reusable Character Roster

**Feature**: 023-character-roster
**Date**: 2026-02-07

## Decision 1: Character Storage Format

**Decision**: Individual JSON files at `data/characters/{tier}/{character_id}.json`

**Rationale**: Follows the existing pattern used by profiles (`data/profiles/{tier}/{profile_id}.json`). Each character is a self-contained file, making CRUD operations simple (create = write file, delete = remove file, list = glob directory). At 20 characters max, directory scanning is negligible.

**Alternatives considered**:
- Single JSON file with all characters: Simpler reads but concurrent write conflicts possible. Rejected for consistency with profile pattern.
- SQLite database: Overkill for 20 records. Rejected per Constitution III (Iterative Simplicity).

## Decision 2: Photo Storage Location

**Decision**: `data/characters/{tier}/{character_id}/photos/` — self-contained per character

**Rationale**: Keeps character data and photos co-located. Deleting a character means deleting one directory tree. No orphaned photos. Backup-friendly.

**Alternatives considered**:
- `data/photos/{tier}/characters/`: Reuses existing photos directory but mixes concerns with profile photos.
- Base64 in JSON: Bloats JSON files, makes them unreadable. Rejected.

## Decision 3: Profile-Roster Relationship

**Decision**: Roster replaces Profile.characters entirely. Profiles store a list of roster character IDs as references.

**Rationale**: Eliminates duplicate character storage. Characters become first-class entities independent of profiles. Profiles reference characters by ID, and when a profile is selected, its referenced characters are auto-selected in the picker.

**Alternatives considered**:
- Keep both systems: Confusing UX with two places to manage characters. Rejected.
- Fully decouple: Profiles lose character association. Rejected because users want profile-to-character mapping.

## Decision 4: Multi-Select vs Single-Select

**Decision**: Multi-select character picker. Users can select multiple roster characters for a single story.

**Rationale**: Enables multi-character stories without re-typing. Profiles can reference multiple characters that auto-select together. Additive with manual character entry.

**Alternatives considered**:
- Single-select dropdown: Simpler but limits the feature's value for multi-character stories.
- Single primary + extras: Added complexity for marginal benefit over full multi-select.

## Decision 5: Template Character References

**Decision**: Templates store a list of character names (`character_names: list[str]`). Each name is matched against the roster by case-insensitive string comparison. Fallback to template's inline character data if no match.

**Rationale**: Simple string matching avoids ID coupling. Templates are hardcoded in `tiers.py`, so name-based matching is practical. Existing templates already have `character_name` and `character_description` — migration adds `character_names` list and per-character inline fallback data.

**Alternatives considered**:
- ID-based linking: Templates would need to know character UUIDs. Fragile and makes template definition awkward.
- No template integration: Loses value for pre-built scenarios.

## Decision 6: Character Photo Validation

**Decision**: Reuse existing upload validation — JPEG/PNG only, max 10 MB per file, max 3 photos per character.

**Rationale**: Consistent with story start form limits. The profile service uses 5 MB limit but 10 MB (from upload service) is more generous and appropriate since character photos are permanent reference images.

**Alternatives considered**:
- Custom limits: No reason to differ from the existing upload infrastructure.

## Decision 7: Migration Strategy

**Decision**: One-time migration script (`scripts/migrate_profile_characters.py`) that:
1. Reads all profiles in `data/profiles/nsfw/`
2. Extracts each profile's characters
3. Creates roster character JSON files with new UUIDs
4. Copies photos from `data/photos/{tier}/{profile_id}/{character_id}.{ext}` to `data/characters/{tier}/{new_character_id}/photos/`
5. Updates profile JSON to store `character_ids: [...]` instead of `characters: [...]`
6. Backs up original profile files before modification

**Rationale**: Clean one-time migration with backup. Can be re-run safely (idempotent — skips already-migrated profiles).

**Alternatives considered**:
- Lazy migration (migrate on first access): More complex, harder to verify completeness.
- Manual migration: Error-prone with multiple characters and photos.

## Decision 8: Character Picker UI Pattern

**Decision**: Checkbox-based multi-select list rendered server-side in the home template. Client-side JavaScript handles selection state, showing selected character summaries, and injecting hidden form fields.

**Rationale**: Follows existing project patterns (server-rendered HTML with progressive JS enhancement). Checkboxes are the simplest multi-select UX for a small list (max 20 items). No need for a complex dropdown/combobox library.

**Alternatives considered**:
- `<select multiple>`: Poor UX on mobile, hard to see all selections.
- Third-party dropdown library: Against Constitution V (Fun Over Perfection) — unnecessary dependency.
