# Research: "Surprise Me" Button

**Branch**: `024-surprise-me-button` | **Date**: 2026-02-07

## Summary

No significant unknowns or external dependencies. This feature uses only existing codebase infrastructure.

## Decisions

### D1: Server-side vs Client-side Random Selection

- **Decision**: Server-side (new POST endpoint)
- **Rationale**: Server-side keeps randomization simple, avoids client-side JS complexity, and ensures tier isolation is enforced on the server. A single POST with no form fields is the simplest UX.
- **Alternatives considered**:
  - Client-side JS that fills the form and auto-submits: More complex, requires duplicating option data in JS, risk of tier leakage if JS has access to all options.
  - GET redirect chain: Not RESTful for an action that creates a resource.

### D2: Direct Logic Invocation vs Form Redirect

- **Decision**: Extract shared logic into a helper, call from both `start_story()` and `surprise_me()`.
- **Rationale**: Avoids duplicating the full story start logic. The surprise endpoint assembles random params and feeds them into the same code path. A redirect-with-POST-data would require an intermediate page with auto-submitting JS form, which is unnecessarily complex.
- **Alternatives considered**:
  - Hidden auto-submit form page: Works but adds an extra page load and flash of content.
  - Duplicating start_story logic: Violates DRY and creates maintenance burden.

### D3: Fallback Prompts When No Templates Exist

- **Decision**: Use a small hardcoded list of generic creative prompts per tier.
- **Rationale**: Simple and reliable. No API call needed. The prompts are just seed ideas — the AI will generate the full story.
- **Alternatives considered**:
  - AI-generated random prompt: Adds latency and API cost for a simple fallback case.
  - Empty prompt (let AI decide): The existing start_story endpoint requires a non-empty prompt.
