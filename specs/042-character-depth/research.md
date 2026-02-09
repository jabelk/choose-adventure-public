# Research: Enhanced Character Creation & Relationship Depth

**Feature**: 042-character-depth
**Date**: 2026-02-08

## R1: Existing Character Model Extension

**Decision**: Extend `RosterCharacter` with new optional fields (backward compatible).

**Rationale**: The existing `RosterCharacter` Pydantic model uses `Field(default_factory=...)` for optional fields. Adding `attributes: dict[str, str] = Field(default_factory=dict)` and relationship fields with defaults means existing JSON files load without migration. Pydantic fills defaults for missing fields.

**Alternatives considered**:
- Separate attributes model/file: Rejected — adds complexity, separate I/O, harder to keep in sync.
- Store attributes as part of description string: Rejected — can't re-populate pill selectors on edit.

## R2: Pill Selector UI Pattern

**Decision**: Reuse existing kink toggle pill pattern (`<label class="kink-toggle"><input type="checkbox"><span class="kink-pill">`) adapted for radio-style single-select.

**Rationale**: The kink toggles already have mobile-friendly pill styling with 44px+ tap targets. Character attributes are single-select per category (you pick one hair color, not multiple), so we use radio buttons inside the same pill label pattern. This gives visual consistency across the app.

**Alternatives considered**:
- Dropdown/select elements: Rejected by spec (FR-007 explicitly says no dropdowns).
- Custom JS component library: Rejected — YAGNI, vanilla HTML radio+label is sufficient.

## R3: Relationship Stage Persistence

**Decision**: Store relationship data directly on `RosterCharacter` JSON.

**Rationale**: Relationship is 1:1 with character. No need for a separate relationship table/file. Adding `relationship_stage`, `story_count`, `last_story_date` to the character JSON keeps all character data in one place.

**Alternatives considered**:
- Separate relationship tracking file: Rejected — adds file I/O, synchronization risk.
- Track per story pair (character + user): Rejected — single-user app, no need for user dimension.

## R4: Story Completion Hook for Relationship Advancement

**Decision**: Add relationship advancement call at each `gallery_service.save_story()` call site in routes.py.

**Rationale**: There are 6 locations where `save_story()` is called (standard story, sequel, agent mode). Each has access to `story_session.story.roster_character_ids`. A helper function `advance_relationships(tier, roster_character_ids)` can be called right after `save_story()` at each location.

**Alternatives considered**:
- Hook inside `save_story()`: Rejected — `GalleryService` shouldn't know about `CharacterService` (separation of concerns).
- Event/signal system: Rejected — YAGNI for 6 call sites. Direct function call is simpler.

## R5: Attribute Options Count

**Decision**: Define concrete attribute options matching spec minimums.

Physical attributes (all tiers unless noted):
- Hair color: 8 options (Blonde, Brunette, Black, Red, Auburn, Silver, Pink, Blue)
- Hair length: 4 options (Short, Medium, Long, Very Long)
- Eye color: 6 options (Brown, Blue, Green, Hazel, Gray, Amber)
- Skin tone: 6 options (Fair, Light, Medium, Olive, Tan, Dark)
- Body type: 5 options (Petite, Slim, Athletic, Curvy, Plus) — NSFW only
- Bust size: 5 options (A, B, C, D, DD) — NSFW only
- Height: 4 options (Short, Average, Tall, Very Tall)

Personality:
- Temperament: 6 options (Shy, Bold, Playful, Dominant, Gentle, Fierce)
- Energy: 4 options (Calm, Bubbly, Intense, Mysterious)
- Archetype: 6 options (Girl Next Door, Femme Fatale, Tomboy, Nerd, Boss Babe, Free Spirit) — NSFW only

Style:
- Clothing style: 6 options (Casual, Sporty, Elegant, Gothic, Bohemian, Streetwear)
- Aesthetic vibe: 4 options (Natural, Glamorous, Edgy, Vintage)

## R6: New Kink Toggles

**Decision**: Add 7 new toggles to reach 11 total (spec requires at least 11).

New toggles:
1. Role Reversal
2. Power Dynamics
3. Clothing Destruction
4. Size Difference
5. Dominance/Submission
6. Hypnosis
7. Bimboification

Each follows the existing `(display_name, story_prompt, image_prompt)` tuple pattern. No code changes needed — just data additions to `KINK_TOGGLES` dict.

## R7: Kids/Bible Tier Attribute Filtering

**Decision**: Use `tier_restrict` field on each attribute category to filter at template render time.

**Rationale**: The template already has tier-aware conditionals (`{% if tier.name == 'nsfw' %}`). Passing `CHARACTER_ATTRIBUTES` to the template and filtering by `tier_restrict` keeps the logic declarative. Server-side validation also checks that restricted attributes aren't submitted for non-NSFW tiers.

Kids/Bible tiers see: hair color, hair length, eye color, skin tone, height (5 categories).
NSFW tier sees: all 12 categories.
