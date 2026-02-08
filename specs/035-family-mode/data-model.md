# Data Model: Family Mode

## Entities

### FamilyChild

A child member of the family.

| Field  | Type   | Required | Constraints         |
|--------|--------|----------|---------------------|
| name   | string | yes      | 1-50 characters     |
| gender | string | yes      | "girl", "boy", "other" |
| age    | int    | yes      | 1-17                |

### FamilyParent

A parent/guardian member of the family.

| Field | Type   | Required | Constraints     |
|-------|--------|----------|-----------------|
| name  | string | yes      | 1-50 characters |

### Family

The top-level family entity stored per tier.

| Field    | Type            | Required | Constraints          |
|----------|-----------------|----------|----------------------|
| tier     | string          | yes      | "kids" or "nsfw"     |
| children | FamilyChild[]   | yes      | 0-6 items            |
| parents  | FamilyParent[]  | no       | 0-2 items            |

## Storage

- Path: `data/family/{tier}/family.json`
- One family per tier (not multiple families)
- File created on first save, deleted when family is cleared

## Relationships

- Family is **independent** of Profile, Character, and Story models
- Family context is injected into Story at generation time via `content_guidelines` (not stored on the Story model)
