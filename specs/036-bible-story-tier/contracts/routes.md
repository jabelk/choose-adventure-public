# API Contracts: Bible Story Tier

## Routes (inherited from router factory)

The Bible tier inherits all routes from `create_tier_router()`. No new route handlers are needed — the existing routes work with any TierConfig. Key routes and their Bible-tier behavior:

### GET /bible/
Home page with collapsible template library and guided reference prompt field.

### POST /bible/story/start
Starts a story from a template or guided reference.

**Bible-tier specific behavior**:
- If `prompt` matches a template: standard flow
- If `prompt` comes from the guided reference field: system fetches verse text via BibleService, builds a story prompt from it, then proceeds normally
- `scripture_reference` is injected into content_guidelines alongside the verse text

### POST /bible/story/surprise
Random template selection from the Bible tier's 75+ templates.

### All other routes
Gallery, export, resume, scene, TTS, characters, family, etc. — all work unchanged.

## New Service: BibleService

### fetch_verses(scripture_reference: str) -> str

**Input**: Scripture reference string (e.g., "Genesis 6:1-22", "John 3:16")
**Output**: Verse text from API.Bible (CEV or NIrV translation)
**Fallback**: Returns empty string if API is unreachable
**Side effects**: None (read-only API call)

### validate_reference(user_input: str) -> bool

**Input**: User-typed string from guided prompt field
**Output**: True if input resembles a valid Bible reference
**Logic**: Check against known book names (Genesis, Exodus, ... Revelation) and optional chapter:verse pattern

## New Environment Variable

| Variable | Required | Description |
|----------|----------|-------------|
| `BIBLE_API_KEY` | No | API.Bible key for fetching verse text. If unset, AI uses training data for scripture content. |

## Template Home Page Sections

The home page for the Bible tier renders templates grouped by `section` field:

```
Old Testament — Genesis
  [template cards...]
Old Testament — Exodus
  [template cards...]
...
New Testament — Matthew
  [template cards...]
```

Each testament header is collapsible. Book sub-groups within are shown when expanded.
