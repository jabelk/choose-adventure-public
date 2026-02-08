# Research: Bedtime Story Mode

**Feature**: 026-bedtime-story-mode
**Date**: 2026-02-08

## Decision 1: Bedtime Mode Flag Storage

**Decision**: Add `bedtime_mode: bool = False` to the `Story` model (and `SavedStory`), following the same pattern as `video_mode`.

**Rationale**: The bedtime mode flag needs to persist across scene navigations within a session and be saved to the gallery. The existing `video_mode` field on `Story` is the exact same pattern — a boolean form toggle that affects generation behavior and UI rendering throughout the session.

**Alternatives considered**:
- Session cookie: Wouldn't persist in gallery saves; inconsistent with existing patterns.
- Separate bedtime session object: Over-engineered for a single boolean flag.

## Decision 2: Content Guidelines Approach

**Decision**: Append bedtime-specific guidelines to the existing kids content guidelines rather than replacing them.

**Rationale**: The kids content guidelines contain important safety rules (age-appropriate content, no violence, etc.) that must remain active during bedtime stories. Bedtime guidelines add the soothing tone and sleep ending on top of those safety rules. This is the same additive pattern used by kinks, character prompts, and story flavor.

**Alternatives considered**:
- Replace kids guidelines entirely: Would lose safety rules. Dangerous.
- Separate prompt template: Over-engineered; additive string concatenation is the established pattern.

## Decision 3: Night Theme Implementation

**Decision**: Use a `.theme-bedtime` CSS class on the body element that overrides CSS custom properties, applied only on scene pages during bedtime mode sessions.

**Rationale**: The app already uses CSS custom properties with theme classes (`.theme-kids`, `.theme-adult`). Adding `.theme-bedtime` as an additional class follows this exact pattern. It overrides the kids theme variables for darker, warmer colors without needing any new CSS architecture.

**Alternatives considered**:
- Inline styles: Messy, not maintainable.
- Separate stylesheet: Unnecessary; CSS custom property overrides are clean and small.
- JavaScript-driven theme: Over-engineered for static color changes.

## Decision 4: Wind-Down Timer Architecture

**Decision**: Client-side JavaScript timer using `sessionStorage` for the start timestamp, rendered as a small overlay element in the scene template.

**Rationale**: The timer is purely a UI element — it doesn't affect story generation or server-side logic. Using `sessionStorage` means the timer persists across page loads within the same browser tab/session (scene navigations), which is the right scope. When the user closes the tab or starts a new story, it resets naturally.

**Alternatives considered**:
- Server-side `created_at` timestamp: Already exists on Story model, but would require passing to JS and doing time math. `sessionStorage` is simpler for elapsed time.
- No persistence (reset on each page): Would restart the timer on every scene load, making it useless.

## Decision 5: Surprise Me Integration

**Decision**: Read the bedtime mode checkbox from the home page form. Since Surprise Me is a separate `<form>`, add a hidden `bedtime_mode` field that gets synced via JavaScript when the bedtime checkbox is toggled.

**Rationale**: The Surprise Me form is a separate `<form>` element on the home page, so it doesn't automatically include the bedtime checkbox value. A small JS snippet can sync the checkbox state to a hidden input in the surprise form, following the same pattern that would be needed for any cross-form state.

**Alternatives considered**:
- Cookie-based: Would persist across sessions unexpectedly; not desirable.
- Move surprise button inside the main form: Would break the separate form architecture.
