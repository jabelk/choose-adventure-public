<!--
  Sync Impact Report
  Version change: 0.0.0 → 1.0.0 (initial ratification)
  Added principles:
    - I. Content Isolation (new)
    - II. Local-First (new)
    - III. Iterative Simplicity (new)
    - IV. Archival by Design (new)
    - V. Fun Over Perfection (new)
  Added sections: Scope filled in
  Removed sections: none
  Templates requiring updates:
    - .specify/templates/plan-template.md ✅ no changes needed (Constitution Check is dynamic)
    - .specify/templates/spec-template.md ✅ no changes needed (generic template)
    - .specify/templates/tasks-template.md ✅ no changes needed (generic template)
  Follow-up TODOs: none
-->

# Choose Your Own Adventure Constitution

## Core Principles

### I. Content Isolation

Kid-safe and adult storylines MUST be served through completely separate
interfaces. There MUST be no navigation path, shared URL scheme, or
UI element that allows cross-access between audience tiers.

- Each audience tier (e.g., "kids", "adult") MUST have its own entry
  point and routing namespace.
- Story data and image assets MAY share a common storage backend, but
  the serving layer MUST enforce tier boundaries.
- New tiers SHOULD be addable without modifying existing tier interfaces.

**Rationale**: The app hosts content for children and adults on the same
network. Accidental exposure of age-inappropriate content is the single
highest-risk failure mode.

### II. Local-First

The application MUST run entirely on the home LAN (Intel NUC "warp-nuc")
with no dependency on cloud services for serving content to users.

- The web server, story data, and image assets MUST be self-hosted.
- External AI APIs (Claude, OpenAI, Grok, Google) MAY be called for
  content generation, but the app MUST remain fully functional for
  reading and browsing when those APIs are unreachable.
- Development and testing SHOULD work on a local laptop before
  deploying to the NUC.

**Rationale**: This is a personal home project. It should work reliably
on the local network without internet dependencies for day-to-day use.

### III. Iterative Simplicity

Start with the simplest viable implementation and add complexity only
when a concrete need arises.

- Phase 1 MUST deliver static text stories with pre-generated images
  and basic branching navigation.
- Multi-model AI generation, style comparison, and dynamic image
  creation SHOULD be deferred to later phases.
- New capabilities MUST NOT break or complicate existing working
  features.
- YAGNI applies: do not build abstractions for hypothetical future
  requirements.

**Rationale**: This is a hobby project. Shipping something fun quickly
matters more than designing for scale or extensibility up front.

### IV. Archival by Design

All generated stories and images MUST be persisted and browsable
independently of the interactive story experience.

- Stories MUST be stored in a format that preserves the full branching
  structure (all paths, not just the path taken).
- Images MUST be stored locally with metadata linking them to story
  nodes.
- A gallery/archive view MUST allow browsing past stories and their
  images outside of the choose-your-own-adventure flow.
- Storage format SHOULD be human-readable and portable (e.g., JSON,
  Markdown, flat files) rather than requiring a heavy database.

**Rationale**: Part of the fun is revisiting old stories and seeing
the AI-generated art. The archive is a first-class feature, not an
afterthought.

### V. Fun Over Perfection

Prefer speed, experimentation, and personal enjoyment over enterprise
engineering practices.

- Code SHOULD be clean and readable but MUST NOT be over-engineered
  with abstractions, patterns, or tooling that slow down iteration.
- Testing SHOULD focus on critical paths (content isolation, data
  integrity) rather than aiming for high coverage metrics.
- Tech choices SHOULD favor tools the developer enjoys using and
  can iterate on quickly.
- It is acceptable to cut corners on non-critical polish if it means
  getting to the fun parts faster.

**Rationale**: This is a personal project built for enjoyment. If the
process stops being fun, something is wrong.

## Scope

A self-hosted web application that delivers interactive choose-your-own-
adventure stories with AI-generated images. The app runs on a home Intel
NUC ("warp-nuc") accessible over the local WiFi network.

**In scope**:
- Branching narrative engine with 3-4 choices per story node
- AI-generated images accompanying story nodes
- Multiple audience tiers (kids, adult) with isolated interfaces
- Story and image archive/gallery for browsing past content
- Multi-model AI support (Claude, OpenAI, Grok, Google) for comparing
  generation styles (later phase)
- Local development on laptop, deployment to NUC

**Out of scope**:
- Public internet hosting or authentication for external users
- Mobile-native apps (web-only, accessed via browser on LAN)
- Real-time multiplayer or collaborative story creation
- Monetization or commercial distribution

## Development Workflow

- All work happens on feature branches, merged to `main` via pull request.
- Follow the spec-kit workflow: specify → plan → tasks → implement.
- Commit after each logical unit of work with a descriptive message.
- Keep PRs focused — one feature or fix per PR.

## Governance

This constitution is the highest-priority reference for all implementation
decisions. If a spec or plan conflicts with a principle here, the
constitution wins. Amendments require updating this file, incrementing
the version, and noting the change in the sync impact report comment above.

**Amendment procedure**:
1. Propose the change with rationale.
2. Update this file with the new or modified principle.
3. Increment the version (MAJOR for principle removals/redefinitions,
   MINOR for additions/expansions, PATCH for clarifications).
4. Update the Sync Impact Report comment at the top of this file.
5. Check dependent templates for alignment.

**Version**: 1.0.0 | **Ratified**: 2026-02-07 | **Last Amended**: 2026-02-07
