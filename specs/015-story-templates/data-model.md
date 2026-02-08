# Data Model: Story Templates

## Client-Side / Configuration Entities

### Story Template

A pre-built story starter defined in application configuration.

- `title`: Short display name (e.g., "Treasure Hunt Puppy")
- `description`: 1-2 sentence summary of the adventure premise
- `emoji`: Single emoji used as the visual icon on the card
- `prompt`: Full prompt text that gets pre-filled into the textarea
- `length`: Suggested story length ("short", "medium", or "long")

### Template Collection (per Tier)

An ordered list of Story Templates attached to a TierConfig. Each tier has its own collection. Templates are rendered in the order defined.

## No Server-Side Storage Changes

Templates are static configuration data defined in Python code alongside existing tier configuration. No database, no files on disk, no new persistence layer. The existing story models (Story, Scene, etc.) are unchanged — stories started from templates are identical to stories started from free-form prompts.

## Relationship to Existing Entities

- **TierConfig** → has many **StoryTemplate** (replaces the existing `suggestions: list[str]` field)
- **Story** → no new relationship. A story started from a template is indistinguishable from one started manually.
