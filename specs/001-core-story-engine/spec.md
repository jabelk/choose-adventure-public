# Feature Specification: Core Story Engine

**Feature Branch**: `001-core-story-engine`
**Created**: 2026-02-07
**Status**: Draft
**Input**: User description: "Choose Your Own Adventure web app where user provides a text prompt, AI generates a full branching story with 3-4 choices per node, AI generates images for each story node via API calls, playable in browser."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Play a Branching Story (Priority: P1)

A user opens the app in their browser, enters a story prompt (e.g., "A knight discovers a hidden cave in the mountains") and selects a story length (short, medium, or long), and the system generates a branching narrative on-demand. The user reads the opening scene with an accompanying AI-generated image, then selects one of 3-4 choices to advance the story. Each choice leads to a new scene with its own text and image. The user continues making choices until reaching an ending.

**Why this priority**: This is the entire core experience. Without the ability to play a branching story, nothing else matters. A working story loop — prompt, read, choose, repeat — is the MVP.

**Independent Test**: Can be fully tested by entering a prompt, verifying a story generates with images, clicking through choices, and reaching an ending.

**Acceptance Scenarios**:

1. **Given** the app is running, **When** the user enters a story prompt and submits, **Then** the system generates a branching story and displays the first scene with text and an image.
2. **Given** a scene is displayed with 3-4 choices, **When** the user clicks a choice, **Then** the next scene loads with new text and a new image matching the narrative.
3. **Given** the user has navigated to a terminal scene (an ending), **When** the scene loads, **Then** it is clearly marked as an ending and the user is offered the option to start a new story or go back to try a different path.
4. **Given** the user is mid-story, **When** they want to explore a different branch, **Then** they can navigate back to a previous choice point and select a different option.

---

### User Story 2 - Generate Story from Custom Prompt (Priority: P2)

A user wants control over the kind of story they get. They enter a prompt describing the setting, genre, or scenario they want. The system uses this prompt to generate a story that matches the user's intent — the tone, setting, and characters reflect what was requested.

**Why this priority**: Prompt-driven generation is what makes this personal and replayable. Without good prompt handling, every story feels generic.

**Independent Test**: Can be tested by entering several different prompts (fantasy, sci-fi, mystery) and verifying each generated story reflects the prompt's theme in both text and images.

**Acceptance Scenarios**:

1. **Given** the prompt input screen, **When** the user types "A detective investigates a haunted mansion" and submits, **Then** the generated story features detective/mystery themes and the images depict a haunted mansion setting.
2. **Given** the prompt input screen, **When** the user submits a very short prompt like "space pirates", **Then** the system still generates a full branching story with a coherent space pirate theme.
3. **Given** the prompt input screen, **When** the user submits an empty prompt, **Then** the system displays a helpful message asking them to provide a story idea.

---

### User Story 3 - View AI-Generated Images for Each Scene (Priority: P3)

Each scene in the story is accompanied by a unique AI-generated image that visually represents the narrative content. The images enhance the reading experience and make each scene feel distinct.

**Why this priority**: Images are a core differentiator of this app vs. plain text adventures. They are integral to the experience but the story engine must work first.

**Independent Test**: Can be tested by playing through a story and verifying every scene has an image that visually relates to the scene content.

**Acceptance Scenarios**:

1. **Given** a scene is generated, **When** it is displayed to the user, **Then** an AI-generated image appears alongside the text that visually represents the scene content.
2. **Given** the image generation API is unavailable or slow, **When** a scene is displayed, **Then** the text is shown immediately with a placeholder, and the image loads asynchronously when ready.
3. **Given** an image fails to generate, **When** the scene is displayed, **Then** a tasteful fallback placeholder is shown and the story remains fully playable.

---

### Edge Cases

- What happens when the AI generates a story with fewer than 3 choices at a node? The system MUST ensure each non-terminal node has at least 2 and at most 4 choices.
- What happens when the AI generates incoherent or contradictory narrative? The prompt engineering MUST include instructions for narrative consistency across branches.
- What happens when the image API rate-limits or times out? The system MUST degrade gracefully — show text first, load images when available.
- What happens when a user tries to go back past the first scene? The system MUST handle this gracefully (e.g., return to the prompt screen).
- What happens when the story generation takes a long time? The system MUST show a loading indicator so the user knows the story is being created.
- What happens when the text generation API fails mid-story? The system MUST auto-retry up to 3 times, then show an error with a manual retry option. The story path MUST be preserved so no progress is lost.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST accept a text prompt from the user and generate story scenes on-demand — one scene at a time as the user makes choices — with at least 3 levels of depth (opening, middle, ending). The full path of prior scenes and choices MUST be passed as context for each generation. When context exceeds token limits, earlier scenes MUST be automatically summarized to maintain coherence.
- **FR-002**: Each non-terminal story node MUST present 2-4 choices for the user to select.
- **FR-003**: System MUST generate a unique AI image for each story node by calling an image generation API.
- **FR-004**: System MUST display story scenes in a browser with text, image, and clickable choices.
- **FR-005**: System MUST allow the user to navigate backward to previous choice points and select a different path.
- **FR-006**: System MUST clearly indicate when the user has reached a story ending.
- **FR-007**: System MUST show loading states during story generation and image generation.
- **FR-008**: System MUST handle image API failures gracefully without breaking the story experience.
- **FR-008a**: System MUST auto-retry text generation API calls up to 3 times on failure. After exhausting retries, the system MUST display an error with a manual retry button. The user's story path MUST be preserved so they can resume without losing progress.
- **FR-009**: System MUST validate that submitted prompts are non-empty before generating.
- **FR-010**: System MUST run as a local web application accessible via browser on the same machine.
- **FR-011**: System MUST allow the user to select a story length (short, medium, or long) before generation begins. The AI MUST pace the narrative to reach endings at approximately the target depth (e.g., short ~3 levels, medium ~5 levels, long ~7 levels).

### Key Entities

- **Story**: A branching narrative generated on-demand from a single prompt. Contains a tree of interconnected scenes. Has a title, original prompt, selected length (short/medium/long), and creation timestamp.
- **Scene (Node)**: A single point in the narrative. Contains story text, an associated image, and 0-4 choices. Terminal scenes (endings) have 0 choices.
- **Choice**: A selectable option at a scene that leads to another scene. Contains the choice text and a reference to the destination scene.
- **Image**: An AI-generated visual tied to a specific scene. Contains the image data/path, the prompt used to generate it, and generation status (pending, complete, failed).

## Clarifications

### Session 2026-02-07

- Q: Should the entire story tree be generated up front, or one scene at a time as choices are made? → A: On-demand — generate one scene at a time as the user makes each choice.
- Q: How much prior context should be passed to the AI when generating the next scene? → A: Full path (all prior scene texts and choices taken). When context exceeds token limits, automatically summarize earlier scenes to stay within bounds. Speed is not a priority over quality for v1.
- Q: Which AI providers for v1? → A: Claude (Anthropic) for text generation, OpenAI DALL-E for image generation.
- Q: How should the system decide when a story branch reaches an ending? → A: User-controlled — let the user choose story length (short/medium/long) before starting. The AI is prompted to pace the narrative accordingly.
- Q: How should the system handle text generation API failures mid-story? → A: Auto-retry up to 3 times, then show error with manual retry button. Story path is preserved so the user can resume without losing progress.

## Assumptions

- The user will provide their own API keys for Claude (Anthropic) for text generation and OpenAI DALL-E for image generation. Key management is configured via environment variables (ANTHROPIC_API_KEY, OPENAI_API_KEY).
- For v1, a single audience tier is sufficient. Content isolation (kids vs. adult) is deferred to a later feature.
- For v1, stories are ephemeral — generated and played in-session. Persistent storage and archival are deferred to a later feature.
- For v1, a single AI provider is used for text and a single provider for images. Multi-model comparison is deferred.
- The branching story structure is a tree (no merging paths). Each choice leads to a unique scene.
- Story depth varies by user selection: short (~3 levels), medium (~5 levels), long (~7 levels). These are soft targets communicated to the AI via prompt.
- A quality-vs-speed toggle for image generation and an image regeneration option are deferred to a later feature.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A user can go from entering a prompt to reading the first scene with text in under 30 seconds. Image quality is prioritized over speed; images may load after text appears.
- **SC-002**: A complete story playthrough (start to ending) involves at least 3 choice points.
- **SC-003**: Every scene in a generated story displays an image that is contextually related to the narrative text.
- **SC-004**: The user can navigate back to any previous choice point and explore an alternate branch without restarting.
- **SC-005**: The story remains fully readable and playable even when image generation fails or is slow.
- **SC-006**: The app is accessible via a standard web browser without installing any plugins or extensions.
