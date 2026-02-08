# Research: Family Mode

## Storage Pattern

**Decision**: Follow the existing ProfileService pattern — store family data as a single JSON file per tier at `data/family/{tier}/family.json`. Only one family per tier (not multiple families to choose from).

**Rationale**: The existing profile/character storage uses `data/{entity}/{tier}/` with JSON files. Family is simpler — each tier has at most one family. A single file per tier keeps things minimal. A `FamilyService` class follows the same pattern as `ProfileService` and `CharacterService`.

**Alternatives considered**:
- localStorage in the browser — rejected because server-side storage is consistent with existing patterns, persists across devices on the LAN, and allows the server to inject family data into prompts.
- Multiple families with a selector — rejected as over-engineered; the user description says "save once and reuse automatically."

## Family Model

**Decision**: Create a `Family` Pydantic model in `app/models.py` with a list of `FamilyChild` and `FamilyParent` sub-models.

**Rationale**: Pydantic models are used everywhere in the project (Profile, Story, RosterCharacter). The sub-models capture the distinct data shapes: children have name+gender+age, parents have name only.

**Alternatives considered**:
- Reusing the existing `Character` model — rejected because Character has fields like `description`, `photo_path`, `linked_profile_id` that don't apply to family members. A dedicated model is cleaner.

## Prompt Injection

**Decision**: Build a `build_family_context()` function in FamilyService that generates a prompt addition similar to `build_profile_context()`. The prompt tells the AI to feature the children as main characters (using their names, genders, and ages) and optionally include parents as supporting characters.

**Rationale**: The existing pattern for injecting context into stories is to append a text block to `content_guidelines`. Family mode follows the same pattern, inserted right after the memory mode block in the `start_story` handler.

**Alternatives considered**:
- Injecting family as `character_name`/`character_description` fields — rejected because those only support one character and would conflict with the roster character picker.

## Home Page Integration

**Decision**: Add a "Family Mode" toggle on the home page, similar in style to the existing "Memory Mode" toggle and "Bedtime Mode" toggle. Show it only when a family exists for the tier. Add a "Family" link in the home page header alongside Gallery, Profiles, Characters.

**Rationale**: Keeps the UI consistent with existing toggles. Users are already familiar with the pattern.

## Family Settings Page

**Decision**: Create a new template `family.html` with inline forms for adding/editing/removing children and parents. No separate add/edit pages — everything on one page, similar to the characters page.

**Rationale**: The family is small (max 8 members). A single-page form keeps interactions fast and simple, matching the project's "fun over perfection" principle.
