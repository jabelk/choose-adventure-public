# Phase 0 Research: Bible Story Tier

## R1: Bible Verse API for Accurate Scripture Text

**Decision**: Use **YouVersion Platform API** (developers.youversion.com) with the **NIrV** (New International Reader's Version, translation ID 110) as the primary source for verse text. NIrV is at a 3rd-grade reading level, designed specifically for children — exactly what we need.

**Rationale**:
- YouVersion has NIrV confirmed available (ID 110) and ICB (ID 1359) as a backup
- NIrV is the ideal translation for ages 3-8 — simplified NIV at 3rd-grade reading level
- REST API with SDK support
- Fetching actual verse text and injecting it into the AI prompt ensures accuracy rather than relying on the AI's training data
- User is willing to pay for proper kids' Bible translation access

**Alternatives considered**:
- API.Bible with CEV: Free, but CEV is 5th-grade level, not as kid-friendly as NIrV. NIrV access requires Biblica approval + $10/month.
- bible-api.com: No auth required but only has old translations (KJV, WEB) — not kid-friendly
- pythonbible (Python package): Fully offline but only public domain translations
- Biblica direct licensing: Can get NIrV permission (up to 500 verses royalty-free), but no API — would need to pair with API.Bible
- Relying on AI training data alone: Risky for verse accuracy — models can hallucinate or conflate passages

**Implementation approach**:
- New `app/services/bible.py` service that calls YouVersion Platform API
- Fetches NIrV verse text given a scripture reference (e.g., "Genesis 6:1-22")
- Injects fetched text into content guidelines before story generation
- Falls back gracefully if API is unreachable (AI uses its training data)
- New env var: `BIBLE_API_KEY` (from platform.youversion.com)
- Design the service interface to be API-agnostic so the backend can be swapped (YouVersion, API.Bible, or future provider) without changing callers

## R2: Adding a Third Tier to the Existing System

**Decision**: Add a `"bible"` entry to the `TIERS` dict in `app/tiers.py`. No architectural changes needed.

**Rationale**:
- The router factory pattern in `app/routes.py` creates a full router for any TierConfig
- `app/main.py` iterates `TIERS.values()` and mounts each — new tiers are auto-discovered
- `get_public_tiers()` filters by `is_public=True` for the landing page
- Constitution principle I explicitly states "New tiers SHOULD be addable without modifying existing tier interfaces"

**Alternatives considered**:
- Separate app or sub-application: Over-engineered for a data-only addition
- Mode within kids tier: Rejected in clarification — separate tier provides better identity and isolation

## R3: Collapsible Template Sections for 75+ Templates

**Decision**: Add a `section` field to `StoryTemplate` dataclass (e.g., "Old Testament — Genesis") and group/render templates by section in `home.html` with collapsible accordion behavior.

**Rationale**:
- Kids and NSFW tiers have 12-30 templates shown as a flat grid with shuffle — works at that scale
- Bible tier has 75+ templates — flat grid would be overwhelming
- Collapsible sections with book sub-groups let users browse by topic
- Accordion is simple CSS + JS, no new dependencies

**Alternatives considered**:
- Flat grid with shuffle only: Poor discoverability for 75+ items
- Tabs (OT/NT): Only two levels, not enough granularity for book sub-groups
- Search-only: Requires knowing what you're looking for

## R4: Guided Bible Reference Prompt

**Decision**: Replace the free-text prompt textarea with a guided "Enter a Bible reference" field for the Bible tier. The system validates the input looks like a Bible reference, fetches the verse text via API.Bible, and builds a story prompt from it.

**Rationale**:
- Free-text prompts could lead to non-biblical or theologically inaccurate stories
- Guided input keeps users within scripture
- The AI builds the story prompt from the fetched verse text + content guidelines
- Simpler than building a full book/chapter/verse picker UI

**Alternatives considered**:
- Free-text with strong guidelines: Risk of hallucinated theology
- Book/chapter/verse dropdown picker: More complex UI, slower to use
- Templates only, no custom input: Too restrictive for a 66-book Bible

## R5: OptionGroup Tier Extension

**Decision**: Add a `bible` field to `OptionGroup` dataclass and update `choices_for_tier()` to handle the `"bible"` tier. Bible tier gets a curated subset of story flavor options (writing style, cast size) but not protagonist age/gender (characters are biblical), not kinks/intensity (N/A).

**Rationale**:
- Current pattern: `choices_for_tier()` returns `self.kids if tier == "kids" else self.nsfw`
- Bible stories have fixed characters from scripture — protagonist gender/age/type selectors don't apply
- Writing style and cast size options are still useful (narrator voice, etc.)
- Kinks and intensity are NSFW-only — already gated by `tier_config.name == "nsfw"` checks

**Alternatives considered**:
- Reuse kids options entirely: Most don't make sense for Bible stories
- No options at all: Loses useful controls like writing style
