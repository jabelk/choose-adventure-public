# Research: Admin Portal

**Feature**: 018-admin-portal
**Date**: 2026-02-07

## Summary

No technical unknowns. This feature uses only existing project patterns and stdlib. Research focused on confirming design choices.

## Decisions

### 1. Admin route mounting strategy

**Decision**: Standalone `admin_routes.py` with `APIRouter(prefix="/admin")` mounted in `main.py`.

**Rationale**: The existing `routes.py` uses a `create_tier_router()` factory that creates tier-scoped routers. The admin page is tier-independent and should not go through that factory. A separate file keeps concerns clean.

**Alternatives considered**:
- Adding admin routes to `routes.py` — rejected because it would pollute the tier router factory with non-tier logic.
- Adding admin routes directly in `main.py` — rejected because `main.py` is already doing app setup and shouldn't grow with route handlers.

### 2. Storage stats calculation approach

**Decision**: Walk directories with `pathlib.Path.glob()` and `stat()` on each file.

**Rationale**: The file counts are small (hundreds at most). No need for caching or background calculation. Direct filesystem traversal is fast enough for the 3-second target.

**Alternatives considered**:
- Background task to pre-compute stats — rejected as over-engineering for the expected scale.
- Database tracking of file metadata — rejected; no database exists and this violates Iterative Simplicity.

### 3. Orphan detection strategy

**Decision**: Collect all scene IDs from all saved stories and in-progress saves into a set. Compare against filenames (stem) in `static/images/` and `static/videos/`. Any file whose stem is not in the set is an orphan.

**Rationale**: Simple set-difference operation. Story files already contain all scene IDs. In-progress saves also contain scene data in their StorySession model.

**Alternatives considered**:
- Track file references in a separate manifest — rejected as unnecessary complexity.

### 4. Story deletion cascade

**Decision**: When deleting a story, extract all scene IDs from its saved JSON, then delete `static/images/{scene_id}.png` and `static/videos/{scene_id}.mp4` for each scene ID, then delete the story JSON itself.

**Rationale**: Scene IDs are UUIDs embedded in the story JSON. Image/video files use scene IDs as filenames. This is a clean, reliable cascade.

**Alternatives considered**:
- Only delete the JSON and let orphan cleanup handle media — rejected because it leaves files around until manual cleanup, which defeats the purpose.
