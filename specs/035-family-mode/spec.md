# Feature Specification: Family Mode

**Feature Branch**: `035-family-mode`
**Created**: 2026-02-07
**Status**: Draft
**Input**: User description: "Family Mode — Save the audience profile once and reuse it automatically. Asks for kids' names, genders, and ages, plus parents' names. Saved names are injected into every story so kids always appear as characters. Supports one or more children plus optional parent characters. Stored locally and selectable from a simple settings page. Both tiers."

## User Scenarios & Testing

### User Story 1 - Create and Save a Family (Priority: P1)

A parent opens the Family settings page from the home page and creates a family profile. They enter each child's name, gender, and age. They optionally add one or two parent names. The family is saved and persists across visits. On the home page, a "Family Mode" toggle becomes available that, when enabled, injects the family members into every new story automatically.

**Why this priority**: Without the ability to create and store a family, no other part of Family Mode works. This is the foundational building block.

**Independent Test**: Can be fully tested by opening the Family settings page, creating a family with 2 children and 1 parent, saving it, reloading the page, and confirming the data persisted.

**Acceptance Scenarios**:

1. **Given** a user is on the Family settings page, **When** they add a child with name "Isla", gender "girl", and age 5, **Then** the child appears in the saved family list.
2. **Given** a user has added children, **When** they add a parent named "Dad", **Then** the parent appears in the family alongside the children.
3. **Given** a user has created a family, **When** they navigate away and return to the Family settings page, **Then** all previously saved family members are still displayed.
4. **Given** no family has been created yet, **When** the user visits the home page, **Then** the Family Mode toggle is not shown.

---

### User Story 2 - Family Members Injected Into Stories (Priority: P2)

When Family Mode is toggled on for a new story, the system automatically includes the saved family members as characters in the story. Children's names, genders, and ages inform the story content. Parent names appear when contextually appropriate. The user does not need to manually type character names each time.

**Why this priority**: This is the core value of Family Mode — the "magic" that makes kids squeal because they see themselves in the story. Depends on US1 (family must exist first).

**Independent Test**: Can be tested by creating a family, starting a story with Family Mode enabled, and verifying the generated story prompt includes the family member names.

**Acceptance Scenarios**:

1. **Given** a family exists with children "Isla" (girl, 5) and "Nora" (girl, 2), **When** the user starts a story with Family Mode on, **Then** the story generation prompt includes instructions to feature Isla and Nora as characters.
2. **Given** a family has a parent named "Dad", **When** Family Mode is on, **Then** the story prompt mentions Dad as an optional supporting character.
3. **Given** Family Mode is toggled off, **When** a story is started, **Then** no family names are injected and the story behaves as before.

---

### User Story 3 - Edit and Delete Family Members (Priority: P3)

A parent can edit any family member's details (name, gender, age) or remove them from the family. They can also delete the entire family profile to start fresh.

**Why this priority**: Managing the family is important for long-term use but not essential for initial setup. Editing can be done by deleting and re-adding at first.

**Independent Test**: Can be tested by creating a family, editing a child's name, and confirming the update persists, then deleting a member and confirming removal.

**Acceptance Scenarios**:

1. **Given** a family exists with child "Isla", **When** the user edits Isla's name to "Isla Rose", **Then** the updated name is saved and displayed.
2. **Given** a family has 2 children, **When** the user removes one child, **Then** only the remaining child is shown.
3. **Given** a family exists, **When** the user deletes the entire family, **Then** the Family settings page shows the empty creation form again.

---

### Edge Cases

- What happens when a user tries to add a child without a name? Validation prevents saving — name is required.
- What happens when the user adds more than 6 children? System caps at 6 children per family to keep stories focused and manageable.
- What happens when Family Mode is on but the family was deleted? The toggle resets to off and the story proceeds without family injection.
- What happens when Family Mode is combined with Memory Mode (profiles)? Both can be active simultaneously — family names are injected alongside profile preferences.
- What happens when Family Mode is combined with a character from the roster? Both work together — roster characters and family members coexist in the story.

## Requirements

### Functional Requirements

- **FR-001**: System MUST provide a Family settings page accessible from both tier home pages.
- **FR-002**: Users MUST be able to add children with name (required), gender (required, choose from girl/boy/other), and age (required, 1-17).
- **FR-003**: Users MUST be able to add parent/guardian names (optional, name only, up to 2 parents).
- **FR-004**: System MUST persist the family data locally so it survives page reloads and browser restarts.
- **FR-005**: The home page MUST show a "Family Mode" toggle when a family has been saved, allowing the user to enable/disable family injection for each story.
- **FR-006**: When Family Mode is enabled, the system MUST include family member details in the story generation prompt so the AI writes them as characters.
- **FR-007**: System MUST allow editing any family member's details after creation.
- **FR-008**: System MUST allow removing individual family members.
- **FR-009**: System MUST allow deleting the entire family profile.
- **FR-010**: System MUST support up to 6 children and 2 parents per family.
- **FR-011**: The Family settings page MUST be accessible from both kids and adult tiers.
- **FR-012**: Family data MUST be scoped per tier (kids tier family is separate from adult tier family).

### Key Entities

- **Family**: A saved group of family members associated with a tier. Contains children and optional parents.
- **Child**: A family member with name, gender, and age. Max 6 per family.
- **Parent**: An optional family member with name only. Max 2 per family.

## Success Criteria

### Measurable Outcomes

- **SC-001**: Users can create a complete family profile (2 children + 1 parent) in under 2 minutes.
- **SC-002**: Stories started with Family Mode enabled mention at least one child's name within the first scene.
- **SC-003**: Family data persists across 100% of page reloads without data loss.
- **SC-004**: The Family Mode toggle is visible and functional on both kids and adult tier home pages.
- **SC-005**: Users can edit or delete any family member in under 30 seconds.

## Assumptions

- Family data is stored per tier (kids and NSFW families are separate), consistent with the project's content isolation principle.
- Family data is stored on the server filesystem, consistent with the existing profile and character storage patterns.
- The "Family Mode" toggle on the home page is separate from the existing "Memory Mode" toggle — both can be active simultaneously.
- Gender options are kept simple: girl, boy, other. No additional gender options are needed for the target audience.
- Parent entries are name-only (no gender or age) since they're supporting characters, not protagonists.
- The maximum of 6 children and 2 parents keeps the AI prompt focused and prevents stories from being overloaded with characters.
