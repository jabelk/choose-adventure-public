import json
import asyncio
import logging

from anthropic import AsyncAnthropic
from openai import AsyncOpenAI
from google import genai

from app.config import settings
from app.models import Scene, StoryLength

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """\
You are a master storyteller creating an interactive choose-your-own-adventure story.

RULES:
1. Generate exactly ONE scene at a time.
2. Each scene must have vivid, engaging narrative text (2-4 paragraphs).
3. Non-ending scenes MUST have exactly {choice_count} distinct choices for the reader.
4. Each choice should lead to meaningfully different story directions.
5. Maintain narrative consistency with all prior scenes — characters, locations, and plot threads must remain coherent.
6. The user's original prompt is your creative north star. Every scene must reflect:
   - The THEME and GENRE specified (fantasy, sci-fi, mystery, romance, horror, etc.)
   - The TONE matching the genre (noir for detective, whimsical for fairy tales, tense for thrillers)
   - The SETTING established in the prompt — keep locations, time period, and world consistent
   - CHARACTER NAMES and traits that persist across all scenes
   - Even short prompts like "space pirates" should produce fully realized, genre-appropriate stories
7. Generate a detailed image_prompt that visually describes this scene for an AI image generator.
   - Describe composition, lighting, mood, and key visual elements in detail.
   - Include consistent character descriptions across ALL scenes (e.g., "a tall woman with silver hair and a blue cloak" should appear the same way every time).
   - Match the art style to the story genre (dark oil painting for horror, bright watercolor for children's fantasy, cinematic realism for thrillers, etc.).
   - Describe the specific environment, weather, and atmosphere.
   - Do NOT include any text, words, letters, or writing in the image description.

STORY PACING:
- Story length: {story_length} ({target_depth} chapters total)
- Current chapter: {current_depth} of {target_depth}
- {pacing_instruction}
{chapter_instruction}

OUTPUT FORMAT (strict JSON, no markdown):
{{
  "title": "Scene title (short, evocative)",
  "content": "The narrative text for this scene. Multiple paragraphs separated by newlines.",
  "image_prompt": "Detailed visual description for AI image generation.",
  "is_ending": false,{chapter_title_field}
  "choices": [
    {{"text": "Choice 1 description"}},
    {{"text": "Choice 2 description"}},
    {{"text": "Choice 3 description"}}
  ]
}}

For ending scenes, set is_ending to true and choices to an empty array [].
Write a satisfying conclusion that wraps up the story thread.
"""


class StoryService:
    def __init__(self):
        self.claude_client = AsyncAnthropic(api_key=settings.anthropic_api_key)
        self.openai_client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.grok_client = (
            AsyncOpenAI(api_key=settings.xai_api_key, base_url="https://api.x.ai/v1")
            if settings.xai_api_key else None
        )
        self.gemini_client = (
            genai.Client(api_key=settings.gemini_api_key)
            if settings.gemini_api_key else None
        )

    async def generate_scene(
        self,
        prompt: str,
        story_length: StoryLength,
        context_scenes: list[Scene],
        current_depth: int,
        target_depth: int,
        choice_text: str | None = None,
        content_guidelines: str = "",
        image_style: str = "",
        model: str = "claude",
        is_chapter_start: bool = False,
        chapter_number: int | None = None,
        total_chapters: int | None = None,
    ) -> dict:
        """Generate a single scene using the specified AI provider."""
        # Determine pacing
        remaining = target_depth - current_depth
        if remaining <= 1:
            pacing = "This MUST be the final scene. Set is_ending to true and choices to []."
            choice_count = 0
        elif remaining <= 2:
            pacing = "The story is approaching its conclusion. Begin wrapping up loose threads. You may end the story here or give 2-3 final choices."
            choice_count = 3
        else:
            pacing = "The story is still developing. Build tension and expand the narrative."
            choice_count = 3

        # Build chapter-specific instructions for epic stories
        chapter_instruction = ""
        chapter_title_field = ""
        if chapter_number and total_chapters:
            chapter_instruction = (
                f"\nCHAPTER STRUCTURE:\n"
                f"- You are writing Chapter {chapter_number} of {total_chapters}.\n"
                f"- Each chapter spans ~5 scenes with its own mini narrative arc.\n"
                f"- Maintain an overarching story thread across all chapters."
            )
            if chapter_number == 1:
                chapter_instruction += "\n- This is the opening chapter. Establish the world, characters, and central conflict."
            elif chapter_number == total_chapters:
                chapter_instruction += "\n- This is the final chapter. Build toward the story's climax and resolution."
            else:
                chapter_instruction += f"\n- This is a middle chapter. Develop subplots and raise the stakes."

            if is_chapter_start:
                chapter_instruction += "\n- This scene is the FIRST scene of a new chapter. Set a new tone or location shift to mark the chapter transition."
                chapter_title_field = '\n  "chapter_title": "A short, evocative chapter title (3-6 words)",'

        system = SYSTEM_PROMPT.format(
            choice_count=choice_count,
            story_length=story_length.value,
            target_depth=target_depth,
            current_depth=current_depth + 1,
            pacing_instruction=pacing,
            chapter_instruction=chapter_instruction,
            chapter_title_field=chapter_title_field,
        )

        # Prepend tier-specific content guidelines
        if content_guidelines:
            system = content_guidelines + "\n\n" + system

        # Build conversation messages
        messages = self._build_messages(prompt, context_scenes, choice_text)

        # Call the selected provider
        response_text = await self._call_provider(model, system, messages)

        # Parse JSON response
        data = self._parse_response(response_text)

        # Append tier-specific image style to the image prompt
        if image_style and data.get("image_prompt"):
            data["image_prompt"] = data["image_prompt"] + ", " + image_style

        return data

    async def _call_provider(
        self, model: str, system: str, messages: list[dict]
    ) -> str:
        """Dispatch to the correct provider's generation method."""
        if model == "gpt":
            return await self._call_gpt(system, messages, model_name="gpt-4o")
        elif model == "gpt5":
            return await self._call_gpt(system, messages, model_name="gpt-5.2")
        elif model == "gemini":
            return await self._call_gemini(system, messages)
        elif model == "grok":
            return await self._call_grok(system, messages)
        else:
            return await self._call_claude(system, messages)

    async def _call_claude(
        self, system: str, messages: list[dict], max_retries: int = 3
    ) -> str:
        """Call Claude API with exponential backoff retry."""
        last_error = None
        for attempt in range(max_retries):
            try:
                response = await self.claude_client.messages.create(
                    model="claude-sonnet-4-5-20250929",
                    max_tokens=2000,
                    system=system,
                    messages=messages,
                )
                return response.content[0].text
            except Exception as e:
                last_error = e
                logger.warning(
                    f"Claude API attempt {attempt + 1}/{max_retries} failed: {e}"
                )
                if attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt)

        raise RuntimeError(
            f"Claude API failed after {max_retries} attempts: {last_error}"
        )

    async def _call_gpt(
        self, system: str, messages: list[dict], max_retries: int = 3, model_name: str = "gpt-4o"
    ) -> str:
        """Call OpenAI GPT API with exponential backoff retry."""
        last_error = None
        for attempt in range(max_retries):
            try:
                oai_messages = [{"role": "system", "content": system}]
                oai_messages.extend(messages)
                params = {
                    "model": model_name,
                    "messages": oai_messages,
                }
                # GPT-5+ uses max_completion_tokens; older models use max_tokens
                if model_name.startswith("gpt-5"):
                    params["max_completion_tokens"] = 2000
                else:
                    params["max_tokens"] = 2000
                response = await self.openai_client.chat.completions.create(**params)
                return response.choices[0].message.content
            except Exception as e:
                last_error = e
                logger.warning(
                    f"GPT API attempt {attempt + 1}/{max_retries} failed: {e}"
                )
                if attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt)

        raise RuntimeError(
            f"GPT API failed after {max_retries} attempts: {last_error}"
        )

    async def _call_gemini(
        self, system: str, messages: list[dict], max_retries: int = 3
    ) -> str:
        """Call Google Gemini API with exponential backoff retry."""
        if not self.gemini_client:
            raise RuntimeError("Gemini API key not configured")
        last_error = None
        for attempt in range(max_retries):
            try:
                # Combine messages into a single user content string
                user_content = "\n\n".join(m["content"] for m in messages)
                response = await self.gemini_client.aio.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=user_content,
                    config=genai.types.GenerateContentConfig(
                        system_instruction=system,
                        max_output_tokens=2000,
                    ),
                )
                return response.text
            except Exception as e:
                last_error = e
                logger.warning(
                    f"Gemini API attempt {attempt + 1}/{max_retries} failed: {e}"
                )
                if attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt)

        raise RuntimeError(
            f"Gemini API failed after {max_retries} attempts: {last_error}"
        )

    async def _call_grok(
        self, system: str, messages: list[dict], max_retries: int = 3
    ) -> str:
        """Call xAI Grok API (OpenAI-compatible) with exponential backoff retry."""
        if not self.grok_client:
            raise RuntimeError("xAI API key not configured")
        last_error = None
        for attempt in range(max_retries):
            try:
                oai_messages = [{"role": "system", "content": system}]
                oai_messages.extend(messages)
                response = await self.grok_client.chat.completions.create(
                    model="grok-3",
                    max_tokens=2000,
                    messages=oai_messages,
                )
                return response.choices[0].message.content
            except Exception as e:
                last_error = e
                logger.warning(
                    f"Grok API attempt {attempt + 1}/{max_retries} failed: {e}"
                )
                if attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt)

        raise RuntimeError(
            f"Grok API failed after {max_retries} attempts: {last_error}"
        )

    def _build_messages(
        self,
        prompt: str,
        context_scenes: list[Scene],
        choice_text: str | None,
    ) -> list[dict]:
        """Build the conversation history for the AI provider."""
        messages = []

        if not context_scenes:
            # First scene — just the user prompt
            messages.append({
                "role": "user",
                "content": f"Create the opening scene for this adventure: {prompt}",
            })
        else:
            # Build context from prior scenes
            context = self._build_context(prompt, context_scenes)
            user_msg = context
            if choice_text:
                user_msg += f"\n\nThe reader chose: \"{choice_text}\"\n\nGenerate the next scene."
            else:
                user_msg += "\n\nGenerate the next scene."
            messages.append({"role": "user", "content": user_msg})

        return messages

    def _build_context(self, prompt: str, scenes: list[Scene]) -> str:
        """Assemble full story context from prior scenes."""
        parts = [f"Original adventure prompt: {prompt}\n\nStory so far:\n"]

        total_chars = len(parts[0])
        scene_texts = []

        for i, scene in enumerate(scenes):
            text = f"--- Chapter {i + 1} ---\n{scene.content}"
            if scene.choices and i < len(scenes) - 1:
                # Find which choice was taken (next scene in path)
                next_scene = scenes[i + 1] if i + 1 < len(scenes) else None
                if next_scene and next_scene.choice_taken_id:
                    for c in scene.choices:
                        if c.choice_id == next_scene.choice_taken_id:
                            text += f"\n[Reader chose: \"{c.text}\"]"
                            break
            scene_texts.append(text)
            total_chars += len(text)

        # If context is too long, summarize earlier scenes
        if total_chars > settings.context_char_threshold and len(scene_texts) > 2:
            return self._summarize_long_context(prompt, scene_texts)

        parts.extend(scene_texts)
        return "\n\n".join(parts)

    def _summarize_long_context(self, prompt: str, scene_texts: list[str]) -> str:
        """When context is too long, keep recent scenes verbatim and summarize earlier ones."""
        # Keep last 2 scenes verbatim, summarize the rest
        keep_count = 2
        to_summarize = scene_texts[:-keep_count]
        to_keep = scene_texts[-keep_count:]

        summary_text = "\n\n".join(to_summarize)
        summary = (
            f"Original adventure prompt: {prompt}\n\n"
            f"[Summary of earlier chapters: The story has progressed through "
            f"{len(to_summarize)} chapters. Key events: "
            f"{summary_text[:2000]}...]\n\n"
            f"Recent chapters:\n\n"
        )
        summary += "\n\n".join(to_keep)
        return summary

    def _parse_response(self, text: str) -> dict:
        """Parse and validate the AI provider's JSON response."""
        # Strip markdown code fences if present
        cleaned = text.strip()
        if cleaned.startswith("```"):
            lines = cleaned.split("\n")
            # Remove first and last lines (fences)
            lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            cleaned = "\n".join(lines)

        try:
            data = json.loads(cleaned)
        except json.JSONDecodeError as e:
            # Common LLM issue: valid JSON followed by extra text.
            # Try extracting just the first JSON object.
            try:
                decoder = json.JSONDecoder()
                data, _ = decoder.raw_decode(cleaned)
                logger.warning(f"Recovered JSON by ignoring trailing data: {e}")
            except json.JSONDecodeError:
                logger.error(f"Failed to parse AI response as JSON: {e}\n{text[:500]}")
                raise ValueError(f"Invalid JSON from AI: {e}")

        # Validate required fields
        required = ["title", "content", "image_prompt", "is_ending", "choices"]
        for field in required:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")

        # Validate choice count for non-endings
        if not data["is_ending"]:
            choice_count = len(data["choices"])
            if choice_count < 2:
                # Pad with generic choices if model gave too few
                while len(data["choices"]) < 2:
                    data["choices"].append({"text": "Continue onward..."})
            elif choice_count > 4:
                data["choices"] = data["choices"][:4]

        return data

    async def generate_recap(
        self,
        scenes: list[Scene],
        model: str = "claude",
        content_guidelines: str = "",
        recap_style: str = "",
    ) -> str:
        """Generate a 2-3 sentence recap of the story so far.

        Uses the same AI provider as the story for consistent voice.
        Returns plain text summary, or empty string on failure.
        """
        if not scenes:
            return ""

        scene_count = len(scenes)
        sentence_count = "2-3" if scene_count < 10 else "3-4"

        system = (
            f"You are a story recap writer. Summarize the story events so far "
            f"in {sentence_count} short sentences. Write in the same tone and "
            f"voice as the story. Do not mention choices, options, or what might "
            f"happen next. Just summarize what has happened."
        )
        if recap_style:
            system += " " + recap_style
        if content_guidelines:
            system = content_guidelines + "\n\n" + system

        # Build a compact summary of each scene
        story_text = "\n\n".join(
            f"Scene {i + 1}: {s.content}" for i, s in enumerate(scenes)
        )
        messages = [
            {"role": "user", "content": f"Summarize this story so far:\n\n{story_text}"},
        ]

        try:
            return await self._call_provider(model, system, messages)
        except Exception as e:
            logger.warning(f"Recap generation failed: {e}")
            return ""
