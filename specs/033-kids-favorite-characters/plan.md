# Implementation Plan: Favorite Characters Across Stories (Kids)

**Branch**: `033-kids-favorite-characters` | **Date**: 2026-02-08 | **Spec**: [spec.md](spec.md)

## Summary

Enable the existing character roster feature on the kids tier. The character roster infrastructure (service, storage, routes, templates) is already fully tier-scoped — the service accepts a `tier` parameter for every operation, and storage is at `data/characters/{tier}/`. The current implementation gates access to NSFW-only via route guards and template conditionals. This feature removes those NSFW-only gates to allow both tiers, and adjusts kid-friendly labels in the template and home page.

## Technical Context

**Language/Version**: Python 3 with FastAPI, Jinja2 templates
**Primary Dependencies**: Existing CharacterService, character-picker.js, characters.html template
**Storage**: JSON files at `data/characters/{tier}/{character_id}.json`, photos at `data/characters/{tier}/{character_id}/photos/`
**Testing**: pytest with FastAPI TestClient

## Constitution Check

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Content Isolation | PASS | Characters are already scoped by tier. Kids tier characters stored at `data/characters/kids/`, NSFW at `data/characters/nsfw/`. No cross-tier access. |
| II. Local-First | PASS | All character data stored locally. No external dependencies. |
| III. Iterative Simplicity | PASS | Minimal changes — removing NSFW-only guards and adjusting labels. No new infrastructure needed. |
| IV. Archival by Design | PASS | Characters persist as JSON files. No impact on story archival. |
| V. Fun Over Perfection | PASS | Leverages existing infrastructure. Small, focused change. |

## Design

### Approach: Remove NSFW-Only Gates

The character roster is already built to support multiple tiers. The implementation is:

1. **Remove route guards** in `app/routes.py`: 6 route handlers currently return 404 if `tier_config.name != "nsfw"`. Remove those guards to allow all tiers.
2. **Remove roster loading gate** in `app/routes.py`: The home page handler loads roster characters only if `tier_config.name == "nsfw"`. Change to load for all tiers.
3. **Update template conditionals** in `templates/home.html`: The "Characters" link and character picker section are gated with `{% if tier.name == 'nsfw' %}`. Remove those gates.
4. **Add kid-friendly labels**: The characters.html template heading says "Character Roster" — change to be tier-aware: "My Characters" for kids, keep "Character Roster" for NSFW. Adjust placeholder text for kids tier ("e.g. Mr. Snuggles" instead of "e.g. Margot Ellis").
5. **Profile character references**: The profile editing page also gates character selection to NSFW. Since profiles are NSFW-only, this gate stays as-is.

### Changes by File

**`app/routes.py`** (~12 lines changed):
- Line 159: Remove `if tier_config.name == "nsfw":` gate on roster character loading in home page handler — load for all tiers
- Lines 1762, 1789, 1830, 1865, 1878: Remove `if tier_config.name != "nsfw": return 404` guards on character CRUD routes
- Line 1894: Remove `if tier_config.name != "nsfw":` gate on `/characters/api/list` endpoint

**`templates/home.html`** (~6 lines changed):
- Lines 9-11: Remove `{% if tier.name == 'nsfw' %}` gate on "Characters" link — show on all tiers
- Lines 186-215: Remove `{% if tier.name == 'nsfw' %}` gate on character picker section
- Lines 346-351: Remove `{% if tier.name == 'nsfw' %}` gate on character picker JS initialization
- Adjust link text: "My Characters" for kids tier, "Characters" for NSFW

**`templates/characters.html`** (~4 lines changed):
- Change heading to be tier-aware: "My Characters" vs "Character Roster"
- Change placeholder text for kids tier (kid-friendly examples)

**`tests/test_kids_characters.py`** (new file):
- Test kids tier can access `/characters` page
- Test kids tier can create a character
- Test kids tier character picker appears on story start form
- Test NSFW tier still works (regression)
- Test kids and NSFW characters are isolated

## Project Structure

### Source Code (repository root)

```text
app/routes.py                # Remove NSFW-only guards on character routes + roster loading
templates/home.html          # Remove NSFW-only template gates for character link + picker
templates/characters.html    # Add tier-aware labels (kid-friendly for kids tier)
tests/test_kids_characters.py  # New: test kids tier character access and tier isolation
```
