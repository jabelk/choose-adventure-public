# Implementation Plan: Image Gallery View

**Branch**: `030-image-gallery-view` | **Date**: 2026-02-08 | **Spec**: [spec.md](spec.md)

## Summary

Add a full-screen, swipeable image gallery overlay accessible from the gallery reader page. Purely client-side — the gallery reader template already has all the image data. A new JS module creates an overlay with keyboard and touch navigation. Both tiers share the same implementation via the router factory pattern.

## Technical Context

**Language/Version**: Python 3 with FastAPI, Jinja2 templates
**Primary Dependencies**: Vanilla JavaScript (client-side only)
**Storage**: N/A (reads existing image URLs)
**Testing**: pytest with FastAPI TestClient

## Constitution Check

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Content Isolation | PASS | Images only accessible within their tier via router factory. |
| II. Local-First | PASS | Client-side JS, local images. |
| III. Iterative Simplicity | PASS | Single JS file, CSS, template button. No new routes or models. |
| IV. Archival by Design | PASS | Enhances archive browsing experience. |
| V. Fun Over Perfection | PASS | Fun image showcase, minimal code. |

## Design

### Client-Side Only
No new server routes. Image URLs are built in the template from `saved.path_history` + scenes and passed as JSON to the JS.

### Overlay Approach
Fixed-position overlay with black background, centered image, nav arrows, close button, position counter. Escape key dismisses.

### Touch Navigation
Standard touchstart/touchend listeners with 50px minimum swipe threshold.
