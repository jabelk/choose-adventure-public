# Research: Core Story Engine

**Feature Branch**: `001-core-story-engine`
**Date**: 2026-02-07

## 1. Web Framework: FastAPI + Jinja2

**Decision**: Python 3.11+ with FastAPI and Jinja2 server-side templates.

**Rationale**:
- FastAPI natively supports async/await for non-blocking AI API calls
- Jinja2 templates keep the frontend dead simple (no JS framework)
- Template inheritance allows consistent layout across pages
- Built-in static file serving for generated images
- Developer (user) is most comfortable with Python

**Alternatives Considered**:
- Flask: Simpler but lacks native async support, would need workarounds for AI API calls
- Django: Too heavy for a personal project with no database needs in v1
- Next.js/React SPA: Over-engineered for "read text, click choice" UI

## 2. AI Text Generation: Anthropic Claude

**Decision**: Use `anthropic` official Python SDK with `AsyncAnthropic` client.

**Rationale**:
- Official SDK with native async support for FastAPI
- User already has Anthropic API access
- Strong narrative generation capabilities
- Simple API: `messages.create()` with system prompt + conversation history

**Alternatives Considered**:
- OpenAI GPT: Good alternative but user prefers Claude
- LangChain wrapper: Unnecessary abstraction layer for direct API calls
- LiteLLM: Useful for multi-provider later, overkill for v1 single provider

## 3. AI Image Generation: OpenAI gpt-image-1

**Decision**: Use `openai` official Python SDK with `AsyncOpenAI` client and `gpt-image-1` model.

**Rationale**:
- **DALL-E 3 is deprecated as of May 12, 2026** — must use `gpt-image-1` or `gpt-image-1-mini`
- `gpt-image-1` produces higher quality images than DALL-E 3
- Official SDK with async support
- Returns image data that can be saved locally

**Alternatives Considered**:
- DALL-E 3: Deprecated, not viable
- Google Imagen: Less mature Python SDK
- Stability AI: Additional vendor relationship for v1

## 4. Session/State Management

**Decision**: Server-side in-memory session store with cookie-based session IDs.

**Rationale**:
- Story state (tree of scenes, path history) can be moderately complex
- In-memory storage is simplest for single-user personal project
- Cookie-based session ID ties browser to server state
- No external dependencies (no Redis needed for v1)
- Pydantic models serialize/deserialize cleanly for session storage

**Alternatives Considered**:
- Client-side localStorage: Size limits, requires JS state management
- URL-based state: Fragile, exposes story logic
- Redis: Overkill for single-user local app
- fastapi-sessions library: Adds dependency; simple dict-based sessions sufficient for v1

## 5. Data Modeling

**Decision**: Pydantic models for all entities (Story, Scene, Choice, Image).

**Rationale**:
- FastAPI is built on Pydantic — zero friction
- Automatic JSON serialization/deserialization
- Built-in validation catches malformed AI outputs
- Future-proof for archival (Principle IV) — clean JSON export

**Alternatives Considered**:
- Python dataclasses: No validation, manual JSON serialization
- Plain dicts: No type safety
- SQLAlchemy models: No database in v1, unnecessary ORM

## 6. Tree Representation

**Decision**: Dictionary-based adjacency structure (`dict[str, Scene]`) with parent references on each scene.

**Rationale**:
- O(1) lookup for any scene by ID
- Parent references enable backward navigation without traversal
- Simple JSON serialization
- Supports lazy/on-demand scene generation
- Path history tracked as a list of scene IDs

**Alternatives Considered**:
- Nested dicts: Hard to navigate backward
- Tree libraries (anytree, treelib): Unnecessary dependency
- Graph database: Massive overkill

## 7. Image Serving

**Decision**: Save generated images to `static/images/` directory, serve via FastAPI `StaticFiles` mount.

**Rationale**:
- FastAPI's StaticFiles middleware handles serving automatically
- Images saved with UUID filenames for uniqueness
- Jinja2 templates reference via URL path
- Images persist on disk for potential future archival

**Alternatives Considered**:
- Streaming bytes from memory: No caching, lost on restart
- Base64 inline in HTML: Bloats page size
- External storage: Violates local-first principle

## 8. Project Structure

**Decision**: Single-project flat structure.

**Rationale**:
- Constitution Principle V (Fun Over Perfection) — keep it simple
- All code in one `app/` package
- Separate `templates/` and `static/` directories per FastAPI convention
- No need for frontend/backend split (server-side rendering)

```
choose-adventure/
├── app/
│   ├── __init__.py
│   ├── main.py           # FastAPI app, startup, middleware
│   ├── routes.py          # Route handlers
│   ├── models.py          # Pydantic models (Story, Scene, etc.)
│   ├── services/
│   │   ├── __init__.py
│   │   ├── story.py       # Story generation (Claude API)
│   │   └── image.py       # Image generation (OpenAI API)
│   └── config.py          # Settings, API keys from env vars
├── templates/
│   ├── base.html          # Base layout
│   ├── home.html          # Prompt input page
│   ├── scene.html         # Story scene display
│   └── error.html         # Error display
├── static/
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   └── app.js         # Minimal JS for loading states
│   └── images/            # Generated scene images
├── requirements.txt
├── .env.example           # API key template
└── README.md
```
