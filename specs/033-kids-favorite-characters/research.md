# Research: Favorite Characters Across Stories (Kids)

## Enabling Character Roster on Kids Tier

**Decision**: Remove NSFW-only guards from existing character roster routes and templates instead of building a separate kids character system.

**Rationale**: The CharacterService already supports tier-scoped operations. Every method accepts a `tier` parameter, storage is at `data/characters/{tier}/`, and the RosterCharacter model has a `tier` field. The NSFW-only restriction is enforced purely at the route and template level (6 route guards, 3 template conditionals). Removing these gates is the simplest path.

**Alternatives considered**:
- Building a separate "kids characters" system with its own service — rejected because it would duplicate existing infrastructure with no benefit.
- Creating a new "favorites" abstraction distinct from the roster — rejected because the roster already does exactly what's needed.

## Kid-Friendly UI Labeling

**Decision**: Use tier-aware conditional labels in templates. Kids tier shows "My Characters" as heading and kid-friendly placeholder text. NSFW keeps "Character Roster" and current placeholders.

**Rationale**: The characters.html template already uses neutral language ("Character Name", "Physical Description"), but the heading "Character Roster" and example name "Margot Ellis" are adult-oriented. Simple Jinja2 conditionals (`{% if tier.name == 'kids' %}`) can switch the few labels that need kid-friendly alternatives.

**Alternatives considered**:
- Separate templates for kids vs NSFW — rejected because the templates are 95% identical and maintaining two copies adds unnecessary complexity.
- Using a single label set for both tiers — rejected because "Character Roster" doesn't resonate with a kids audience.

## Profile Integration

**Decision**: Keep profile-character integration gated to NSFW only. Profiles are an NSFW-only feature and don't exist on the kids tier.

**Rationale**: The profile editing page (`templates/profile_edit.html`) has a character selection section gated to NSFW. Since profiles themselves are NSFW-only, there's no reason to change this gate. Kids tier users interact with characters through the management page and story start picker, not through profiles.

**Alternatives considered**:
- Adding profile support to kids tier — rejected as out of scope for this feature.
