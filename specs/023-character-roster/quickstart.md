# Quickstart Test Scenarios: Character Roster

**Feature**: 023-character-roster
**Date**: 2026-02-07

## Scenario 1: Create a Character

1. Navigate to `/nsfw/characters`
2. Verify empty state message shown
3. Fill in name: "Margot Ellis"
4. Fill in description: "Early 30s, honey-blonde hair, hazel eyes, athletic build"
5. Click Save
6. **Expected**: Character appears in list with name and truncated description

## Scenario 2: Create Character with Photos

1. Navigate to `/nsfw/characters`
2. Fill in name: "Kayla Rae"
3. Fill in description: "Mid 20s, dark curly hair, brown eyes, petite"
4. Upload 2 reference photos (JPEG)
5. Click Save
6. **Expected**: Character appears in list with thumbnail of first photo

## Scenario 3: Character Limit Enforcement

1. Create 20 characters on the NSFW tier
2. Attempt to create a 21st character
3. **Expected**: Error message "Character limit reached (20 max)"

## Scenario 4: Multi-Select Picker on Story Start

1. Ensure at least 2 characters exist (Margot, Kayla)
2. Navigate to `/nsfw/` (home/start page)
3. Verify character picker shows both characters with checkboxes
4. Select both characters
5. Type a story prompt
6. Click Start Story
7. **Expected**: Both characters appear in the generated story content

## Scenario 5: Roster + Manual Character Additive

1. Select "Margot Ellis" from picker
2. Type manual character name: "John Smith"
3. Type manual character description: "Tall, dark hair"
4. Start story
5. **Expected**: Both Margot (from roster) and John (manual) appear in story

## Scenario 6: Template Pre-Selection

1. Save characters "Margot Ellis" and "Kayla Rae" to roster
2. Click a template that references both names
3. **Expected**: Both characters auto-selected in picker
4. Start story
5. **Expected**: Both characters appear in generated content

## Scenario 7: Edit and Delete Character

1. Navigate to `/nsfw/characters`
2. Click Edit on "Margot Ellis"
3. Change description to "Late 30s, silver-streaked blonde hair"
4. Click Save
5. **Expected**: Updated description shown in list
6. Click Delete on "Kayla Rae"
7. Confirm deletion
8. **Expected**: Kayla Rae removed from list and story start picker

## Scenario 8: Profile Character References

1. Create profile "Date Night"
2. Associate characters "Margot Ellis" and "Kayla Rae" with profile
3. On story start, enable Memory Mode and select "Date Night" profile
4. **Expected**: Both characters auto-selected in picker
5. Start story
6. **Expected**: Profile preferences + both characters in story

## Scenario 9: Migration Verification

1. Run `venv/bin/python scripts/migrate_profile_characters.py`
2. Verify existing profile characters appear as roster characters at `/nsfw/characters`
3. Verify profile edit page shows character ID references (not inline characters)
4. Verify photos migrated to `data/characters/nsfw/{id}/photos/`
5. Start a story with the migrated profile
6. **Expected**: Characters still work in story generation

## Scenario 10: Kids Tier Isolation

1. Navigate to `/kids/characters`
2. **Expected**: 404 or redirect — character roster not available on kids tier
3. Verify no character picker on kids story start form
4. Verify no "Characters" nav link on kids tier
