# Data Model: Core Story Engine

**Feature Branch**: `001-core-story-engine`
**Date**: 2026-02-07

## Entities

### ImageStatus (Enum)

Tracks the lifecycle of an AI-generated image.

| Value        | Description                              |
|--------------|------------------------------------------|
| `pending`    | Image generation not yet started         |
| `generating` | API call in progress                     |
| `complete`   | Image generated and saved to disk        |
| `failed`     | Generation failed after retries          |

### StoryLength (Enum)

User-selected story length controlling narrative pacing.

| Value    | Target Depth | Description            |
|----------|-------------|------------------------|
| `short`  | ~3 levels   | Quick 5-minute story   |
| `medium` | ~5 levels   | Standard 10-15 minutes |
| `long`   | ~7 levels   | Extended 20+ minutes   |

### Image

An AI-generated visual tied to a specific scene.

| Field    | Type         | Required | Description                                |
|----------|--------------|----------|--------------------------------------------|
| prompt   | string       | yes      | The prompt sent to the image generation API |
| status   | ImageStatus  | yes      | Current generation lifecycle state          |
| url      | string       | no       | Local URL path to saved image file          |
| error    | string       | no       | Error message if generation failed          |

### Choice

A selectable option at a scene that leads to another scene.

| Field         | Type   | Required | Description                                    |
|---------------|--------|----------|------------------------------------------------|
| choice_id     | string | yes      | Unique identifier (UUID)                       |
| text          | string | yes      | Display text for the choice                    |
| next_scene_id | string | no       | ID of the destination scene (null until generated) |

### Scene

A single point in the narrative tree.

| Field            | Type          | Required | Description                                        |
|------------------|---------------|----------|----------------------------------------------------|
| scene_id         | string        | yes      | Unique identifier (UUID)                           |
| parent_scene_id  | string        | no       | ID of parent scene (null for root scene)           |
| choice_taken_id  | string        | no       | ID of the choice that led to this scene            |
| content          | string        | yes      | Narrative text for this scene                      |
| image            | Image         | yes      | Associated AI-generated image                      |
| choices          | list[Choice]  | yes      | 2-4 choices for non-terminal, empty for endings    |
| is_ending        | boolean       | yes      | Whether this scene is a terminal/ending scene      |
| depth            | integer       | yes      | Level in the tree (root = 0)                       |

**Constraints**:
- Non-terminal scenes: 2 <= len(choices) <= 4
- Terminal scenes (endings): len(choices) == 0, is_ending == true
- depth >= 0

### Story

A branching narrative session generated from a user prompt.

| Field           | Type        | Required | Description                                  |
|-----------------|-------------|----------|----------------------------------------------|
| story_id        | string      | yes      | Unique identifier (UUID)                     |
| title           | string      | yes      | AI-generated title for the story             |
| prompt          | string      | yes      | Original user prompt                         |
| length          | StoryLength | yes      | User-selected story length                   |
| target_depth    | integer     | yes      | Target depth derived from length selection   |
| created_at      | datetime    | yes      | Creation timestamp                           |
| current_scene_id| string      | yes      | ID of the scene the user is currently viewing|

### StorySession

Combines the story tree with navigation state. This is the top-level object stored in the session.

| Field        | Type              | Required | Description                                      |
|--------------|-------------------|----------|--------------------------------------------------|
| story        | Story             | yes      | Story metadata                                   |
| scenes       | dict[str, Scene]  | yes      | All generated scenes, keyed by scene_id          |
| path_history | list[string]      | yes      | Ordered list of scene_ids from root to current   |

## Relationships

```
Story (1) ──contains──> (many) Scene
Scene (1) ──has──> (many) Choice
Scene (1) ──has──> (1) Image
Choice (1) ──leads to──> (0..1) Scene  (null until generated on-demand)
Scene (1) ──child of──> (0..1) Scene   (via parent_scene_id)
StorySession (1) ──wraps──> (1) Story + scenes dict + path history
```

## State Transitions

### Scene Generation Flow

```
User submits prompt
  → Generate root Scene (depth=0)
    → Image starts as PENDING → GENERATING → COMPLETE or FAILED
  → Display Scene with choices
  → User clicks Choice
    → Generate next Scene (depth=parent.depth+1)
    → If depth approaching target_depth, prompt AI to write toward ending
    → Repeat until is_ending == true
```

### Navigation Flow

```
Forward: User clicks choice
  → Append new scene_id to path_history
  → Generate new scene if choice.next_scene_id is null
  → Display scene at choice.next_scene_id

Backward: User clicks "go back"
  → Pop last scene_id from path_history
  → Display scene at new last element of path_history
  → Previously generated scenes remain in scenes dict (can revisit)

Back to start: User at first scene clicks back
  → Return to prompt input screen
```

## Serialization

All entities use Pydantic models with native JSON serialization via `model_dump_json()` / `model_validate_json()`. The full `StorySession` object is serializable for:
- Server-side session storage (in-memory dict for v1)
- Future archival to disk (JSON files, Principle IV)
