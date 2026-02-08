import asyncio
import base64
import logging
from pathlib import Path

import httpx
from google import genai
from openai import AsyncOpenAI, BadRequestError

from app.config import settings
from app.models import Image, ImageStatus

logger = logging.getLogger(__name__)

STATIC_IMAGES_DIR = Path(__file__).resolve().parent.parent.parent / "static" / "images"
STATIC_VIDEOS_DIR = Path(__file__).resolve().parent.parent.parent / "static" / "videos"

MAX_RETRIES = 2
FAST_IMAGE_MODEL = "gpt-image-1-mini"

# Prompt variations for picture book extra images — each rewrites the scene from
# a different artistic angle so the results look visually distinct, not just zoomed.
_EXTRA_IMAGE_VARIATIONS = [
    (
        "close-up",
        "Re-imagine this as an intimate character portrait in warm soft lighting. "
        "Focus on the character's face and emotional expression, with a shallow "
        "depth-of-field background. Style: cozy storybook illustration. Original scene: ",
    ),
    (
        "wide-shot",
        "Re-imagine this as a panoramic landscape painting of the setting. "
        "Show the full environment with dramatic sky and rich background detail. "
        "The characters should be tiny figures in the vast scene. "
        "Style: children's book double-page spread illustration. Original scene: ",
    ),
]

# OpenAI model keys that route to _generate_openai
_OPENAI_IMAGE_MODELS = {"gpt-image-1", "gpt-image-1-mini", "gpt-image-1.5", "dalle"}

# Fallback order when a model refuses content (e.g. safety filters)
_FALLBACK_ORDER = ["gpt-image-1", "grok-imagine"]


class ContentRefusedError(Exception):
    """Raised when a model refuses to generate due to safety/content filters."""
    pass


class ImageService:
    def __init__(self):
        self.openai_client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.gemini_client = (
            genai.Client(api_key=settings.gemini_api_key)
            if settings.gemini_api_key else None
        )
        self.xai_client = (
            AsyncOpenAI(
                base_url="https://api.x.ai/v1",
                api_key=settings.xai_api_key,
            )
            if settings.xai_api_key else None
        )

    async def generate_image(
        self, image: Image, scene_id: str, image_model: str = "gpt-image-1",
        reference_images: list[str] | None = None,
    ) -> None:
        """Generate an image using the specified provider and save to disk.

        Modifies the Image object in-place with status updates.
        This method is designed to be run as a background task.
        Retries up to MAX_RETRIES times on failure with backoff.
        On content refusal (safety filters), skips retries and falls back
        to a different model automatically.
        """
        image.status = ImageStatus.GENERATING
        last_error = None

        for attempt in range(MAX_RETRIES + 1):
            try:
                img_bytes = await self._call_model(
                    image_model, image.prompt, reference_images
                )

                # Save to disk
                STATIC_IMAGES_DIR.mkdir(parents=True, exist_ok=True)
                filepath = STATIC_IMAGES_DIR / f"{scene_id}.png"
                filepath.write_bytes(img_bytes)

                # Verify file is valid (non-zero size)
                if filepath.stat().st_size == 0:
                    raise ValueError("Saved image file is empty")

                image.url = f"/static/images/{scene_id}.png"
                image.status = ImageStatus.COMPLETE
                logger.info(f"Image generated for scene {scene_id} using {image_model}")
                return

            except ContentRefusedError as e:
                # Don't retry the same model — it will refuse again.
                # Try fallback models instead.
                logger.warning(
                    f"{image_model} refused content for scene {scene_id}: {e}. "
                    f"Trying fallback models."
                )
                fallback_result = await self._try_fallbacks(
                    image_model, image.prompt, reference_images, scene_id
                )
                if fallback_result:
                    img_bytes, used_model = fallback_result
                    STATIC_IMAGES_DIR.mkdir(parents=True, exist_ok=True)
                    filepath = STATIC_IMAGES_DIR / f"{scene_id}.png"
                    filepath.write_bytes(img_bytes)
                    image.url = f"/static/images/{scene_id}.png"
                    image.status = ImageStatus.COMPLETE
                    logger.info(
                        f"Image generated for scene {scene_id} using "
                        f"fallback {used_model} (original: {image_model})"
                    )
                    return
                # All fallbacks failed too
                last_error = e
                break

            except Exception as e:
                last_error = e
                logger.warning(
                    f"Image generation attempt {attempt + 1}/{MAX_RETRIES + 1} "
                    f"failed for scene {scene_id} ({image_model}): {e}"
                )
                if attempt < MAX_RETRIES:
                    await asyncio.sleep(2 ** attempt)

        # All retries/fallbacks exhausted
        image.status = ImageStatus.FAILED
        image.error = str(last_error)
        logger.error(
            f"Image generation failed for scene {scene_id} ({image_model}) after "
            f"all attempts. Prompt: {image.prompt[:200]}"
        )

    async def generate_extra_images(
        self,
        extra_images: list[Image],
        scene_id: str,
        main_prompt: str,
        fast_model: str,
        reference_images: list[str] | None = None,
    ) -> None:
        """Generate extra images (picture book mode) in parallel.

        Each extra image gets a varied prompt derived from main_prompt.
        Uses the fast model for generation. Updates each Image object's
        status independently.
        """
        async def _generate_one(image: Image, index: int, variation_suffix: str):
            image.status = ImageStatus.GENERATING
            varied_prompt = f"{variation_suffix}{main_prompt}"
            image.prompt = varied_prompt
            last_error = None

            for attempt in range(MAX_RETRIES + 1):
                try:
                    img_bytes = await self._call_model(
                        fast_model, varied_prompt, reference_images
                    )

                    STATIC_IMAGES_DIR.mkdir(parents=True, exist_ok=True)
                    filepath = STATIC_IMAGES_DIR / f"{scene_id}_extra_{index}.png"
                    filepath.write_bytes(img_bytes)

                    if filepath.stat().st_size == 0:
                        raise ValueError("Saved image file is empty")

                    image.url = f"/static/images/{scene_id}_extra_{index}.png"
                    image.status = ImageStatus.COMPLETE
                    logger.info(
                        f"Extra image {index} generated for scene {scene_id} "
                        f"using {fast_model}"
                    )
                    return

                except ContentRefusedError as e:
                    logger.warning(
                        f"{fast_model} refused content for extra image {index} "
                        f"scene {scene_id}: {e}"
                    )
                    last_error = e
                    break

                except Exception as e:
                    last_error = e
                    logger.warning(
                        f"Extra image {index} attempt {attempt + 1}/{MAX_RETRIES + 1} "
                        f"failed for scene {scene_id}: {e}"
                    )
                    if attempt < MAX_RETRIES:
                        await asyncio.sleep(2 ** attempt)

            image.status = ImageStatus.FAILED
            image.error = str(last_error)
            logger.error(
                f"Extra image {index} generation failed for scene {scene_id}"
            )

        tasks = []
        for i, image in enumerate(extra_images):
            if i < len(_EXTRA_IMAGE_VARIATIONS):
                _, suffix = _EXTRA_IMAGE_VARIATIONS[i]
            else:
                suffix = _EXTRA_IMAGE_VARIATIONS[0][1]
            tasks.append(_generate_one(image, i, suffix))

        await asyncio.gather(*tasks, return_exceptions=True)

    async def _call_model(
        self, image_model: str, prompt: str,
        reference_images: list[str] | None = None,
    ) -> bytes:
        """Dispatch to the correct model backend. Returns raw image bytes."""
        if image_model == "gemini":
            return await self._generate_gemini(
                prompt, reference_images=reference_images
            )
        elif image_model == "grok-imagine":
            return await self._generate_grok(
                prompt, reference_images=reference_images
            )
        else:
            model_name = "gpt-image-1" if image_model == "dalle" else image_model
            return await self._generate_openai(
                prompt, model_name=model_name,
                reference_images=reference_images,
            )

    async def _try_fallbacks(
        self, refused_model: str, prompt: str,
        reference_images: list[str] | None, scene_id: str,
    ) -> tuple[bytes, str] | None:
        """Try fallback models after a content refusal. Returns (bytes, model_name) or None."""
        for fallback in _FALLBACK_ORDER:
            if fallback == refused_model:
                continue
            try:
                logger.info(
                    f"Trying fallback model {fallback} for scene {scene_id}"
                )
                img_bytes = await self._call_model(
                    fallback, prompt, reference_images
                )
                return img_bytes, fallback
            except Exception as e:
                logger.warning(
                    f"Fallback {fallback} also failed for scene {scene_id}: {e}"
                )
        return None

    async def _generate_openai(
        self, prompt: str, model_name: str = "gpt-image-1",
        reference_images: list[str] | None = None,
    ) -> bytes:
        """Generate an image using an OpenAI GPT Image model. Returns raw image bytes.

        Supports gpt-image-1, gpt-image-1-mini, and gpt-image-1.5.
        When reference_images are provided, uses images.edit.
        input_fidelity="high" is only passed for models that support it
        (gpt-image-1, gpt-image-1.5 — NOT gpt-image-1-mini).
        Raises ContentRefusedError on moderation blocks.
        """
        try:
            return await self._openai_request(prompt, model_name, reference_images)
        except BadRequestError as e:
            if "moderation_blocked" in str(e) or "safety" in str(e).lower():
                raise ContentRefusedError(
                    f"OpenAI refused to generate image: {e}"
                ) from e
            raise

    async def _openai_request(
        self, prompt: str, model_name: str,
        reference_images: list[str] | None,
    ) -> bytes:
        """Execute the OpenAI API call. Returns raw image bytes."""
        if reference_images:
            image_files = []
            for img_path in reference_images:
                path = Path(img_path)
                if path.exists():
                    image_files.append(path)

            if image_files:
                logger.info(
                    f"Using images.edit with {len(image_files)} reference image(s) "
                    f"and model {model_name}"
                )
                ref_prompt = (
                    f"Use the person from the reference photo as the main character "
                    f"in this scene. Preserve their face, features, and likeness "
                    f"accurately. Scene: {prompt}"
                )
                edit_params = {
                    "model": model_name,
                    "image": image_files,
                    "prompt": ref_prompt,
                    "size": "1024x1024",
                }
                if model_name != "gpt-image-1-mini":
                    edit_params["input_fidelity"] = "high"

                response = await self.openai_client.images.edit(**edit_params)
            else:
                response = await self.openai_client.images.generate(
                    model=model_name,
                    prompt=prompt,
                    n=1,
                    size="1024x1024",
                )
        else:
            response = await self.openai_client.images.generate(
                model=model_name,
                prompt=prompt,
                n=1,
                size="1024x1024",
            )

        image_data = response.data[0]

        if hasattr(image_data, "b64_json") and image_data.b64_json:
            return base64.b64decode(image_data.b64_json)
        elif hasattr(image_data, "url") and image_data.url:
            async with httpx.AsyncClient() as http:
                img_response = await http.get(image_data.url)
                return img_response.content
        else:
            raise ValueError("No image data in OpenAI response")

    async def _generate_grok(
        self, prompt: str, reference_images: list[str] | None = None,
    ) -> bytes:
        """Generate an image using xAI Grok Imagine. Returns raw image bytes.

        Uses the OpenAI-compatible endpoint for basic generation.
        For reference images (editing), uses raw httpx since the OpenAI SDK's
        images.edit doesn't work with xAI (multipart vs JSON mismatch).
        """
        if not self.xai_client:
            raise RuntimeError("xAI API key not configured")

        if reference_images:
            # Use raw httpx for image editing with reference photos
            valid_refs = [p for p in reference_images if Path(p).exists()]
            if valid_refs:
                ref_path = Path(valid_refs[0])
                mime = "image/jpeg" if ref_path.suffix in (".jpg", ".jpeg") else "image/png"
                b64_data = base64.b64encode(ref_path.read_bytes()).decode("utf-8")
                image_url = f"data:{mime};base64,{b64_data}"

                ref_prompt = (
                    f"Use the person from the reference photo as the main character "
                    f"in this scene. Preserve their face, features, and likeness "
                    f"accurately. Scene: {prompt}"
                )
                logger.info("Using Grok Imagine image editing with reference photo")
                async with httpx.AsyncClient(timeout=60.0) as http:
                    resp = await http.post(
                        "https://api.x.ai/v1/images/generations",
                        headers={
                            "Authorization": f"Bearer {settings.xai_api_key}",
                            "Content-Type": "application/json",
                        },
                        json={
                            "model": "grok-imagine-image",
                            "prompt": ref_prompt,
                            "n": 1,
                            "image_url": image_url,
                            "response_format": "b64_json",
                        },
                    )
                    resp.raise_for_status()
                    data = resp.json()
                    return base64.b64decode(data["data"][0]["b64_json"])

        # Basic generation via OpenAI-compatible SDK
        response = await self.xai_client.images.generate(
            model="grok-imagine-image",
            prompt=prompt,
            n=1,
            response_format="b64_json",
        )

        image_data = response.data[0]
        if hasattr(image_data, "b64_json") and image_data.b64_json:
            return base64.b64decode(image_data.b64_json)
        elif hasattr(image_data, "url") and image_data.url:
            async with httpx.AsyncClient() as http:
                img_response = await http.get(image_data.url)
                return img_response.content
        else:
            raise ValueError("No image data in Grok Imagine response")

    async def _generate_gemini(
        self, prompt: str, reference_images: list[str] | None = None,
    ) -> bytes:
        """Generate an image using Gemini native image generation. Returns raw image bytes.

        When reference_images are provided, includes them as inline_data
        so Gemini can incorporate character likeness.
        """
        if not self.gemini_client:
            raise RuntimeError("Gemini API key not configured")

        contents = []

        # Add reference images if provided
        if reference_images:
            for img_path in reference_images:
                path = Path(img_path)
                if path.exists():
                    mime = "image/jpeg" if path.suffix in (".jpg", ".jpeg") else "image/png"
                    contents.append(
                        genai.types.Part(
                            inline_data=genai.types.Blob(
                                mime_type=mime, data=path.read_bytes()
                            )
                        )
                    )
            if contents:
                logger.info(
                    f"Including {len(contents)} reference image(s) for Gemini"
                )
                contents.append(
                    f"Generate an image incorporating the people from the "
                    f"reference photos into this scene: {prompt}"
                )
            else:
                contents = f"Generate an image: {prompt}"
        else:
            contents = f"Generate an image: {prompt}"

        logger.info(f"Calling Gemini image generation (model=gemini-2.5-flash-image)")
        try:
            response = await asyncio.wait_for(
                self.gemini_client.aio.models.generate_content(
                    model="gemini-2.5-flash-image",
                    contents=contents,
                    config=genai.types.GenerateContentConfig(
                        response_modalities=["IMAGE"],
                    ),
                ),
                timeout=120,
            )
        except asyncio.TimeoutError:
            raise TimeoutError("Gemini image generation timed out after 120s")

        logger.info(f"Gemini response received, extracting image data")

        # Extract image bytes from response
        if (
            response.candidates
            and response.candidates[0].content
            and response.candidates[0].content.parts
        ):
            for part in response.candidates[0].content.parts:
                if part.inline_data and part.inline_data.data:
                    return part.inline_data.data

        # Determine why no image was returned
        if response.candidates:
            candidate = response.candidates[0]
            finish_reason = getattr(candidate, "finish_reason", "unknown")
            reason_str = str(finish_reason)
            logger.error(f"Gemini response had no image data. finish_reason={reason_str}")

            # Safety/content refusals — don't retry, fall back instead
            if "SAFETY" in reason_str or "OTHER" in reason_str:
                raise ContentRefusedError(
                    f"Gemini refused to generate image (finish_reason={reason_str})"
                )
        else:
            logger.error(f"Gemini response had no candidates")

        raise ValueError("No image data in Gemini response")

    async def generate_coloring_page(
        self, image_prompt: str, scene_id: str, image_model: str = "gpt-image-1",
    ) -> str:
        """Generate a coloring page version of a scene image.

        Checks if a cached coloring page exists on disk first. If not,
        generates a new one using the scene's image prompt with a
        coloring page style override. Returns the URL path.
        """
        STATIC_IMAGES_DIR.mkdir(parents=True, exist_ok=True)
        filepath = STATIC_IMAGES_DIR / f"{scene_id}_coloring.png"
        url_path = f"/static/images/{scene_id}_coloring.png"

        # Return cached version if it exists
        if filepath.exists() and filepath.stat().st_size > 0:
            logger.info(f"Coloring page cache hit for scene {scene_id}")
            return url_path

        coloring_prompt = (
            "Simple black and white coloring page line art, thick outlines, "
            "no shading, no color, no grayscale, suitable for children to "
            "color in. Scene: " + image_prompt
        )

        last_error = None
        for attempt in range(MAX_RETRIES + 1):
            try:
                img_bytes = await self._call_model(image_model, coloring_prompt)

                filepath.write_bytes(img_bytes)

                if filepath.stat().st_size == 0:
                    raise ValueError("Saved coloring page file is empty")

                logger.info(
                    f"Coloring page generated for scene {scene_id} "
                    f"using {image_model}"
                )
                return url_path

            except ContentRefusedError as e:
                logger.warning(
                    f"{image_model} refused coloring page for scene {scene_id}: {e}. "
                    f"Trying fallback models."
                )
                fallback_result = await self._try_fallbacks(
                    image_model, coloring_prompt, None, scene_id
                )
                if fallback_result:
                    img_bytes, used_model = fallback_result
                    filepath.write_bytes(img_bytes)
                    logger.info(
                        f"Coloring page generated for scene {scene_id} using "
                        f"fallback {used_model}"
                    )
                    return url_path
                last_error = e
                break

            except Exception as e:
                last_error = e
                logger.warning(
                    f"Coloring page attempt {attempt + 1}/{MAX_RETRIES + 1} "
                    f"failed for scene {scene_id}: {e}"
                )
                if attempt < MAX_RETRIES:
                    await asyncio.sleep(2 ** attempt)

        raise RuntimeError(
            f"Coloring page generation failed for scene {scene_id}: {last_error}"
        )

    async def generate_video(
        self, image: Image, scene_id: str,
    ) -> None:
        """Generate a video clip for a scene using xAI Grok Imagine.

        Prefers image-to-video (using the scene's generated image) for
        visual continuity. Falls back to text-to-video if no image available.
        Polls the xAI API until the video is ready or timeout.
        """
        if not settings.xai_api_key:
            image.video_status = "failed"
            image.video_error = "xAI API key not configured"
            return

        image.video_status = "generating"

        try:
            headers = {
                "Authorization": f"Bearer {settings.xai_api_key}",
                "Content-Type": "application/json",
            }

            body = {
                "model": "grok-imagine-video",
                "prompt": image.prompt,
                "duration": 8,
                "aspect_ratio": "1:1",
                "resolution": "720p",
            }

            # Prefer image-to-video if the scene image is available
            image_path = STATIC_IMAGES_DIR / f"{scene_id}.png"
            if image_path.exists():
                b64_data = base64.b64encode(image_path.read_bytes()).decode("utf-8")
                body["image"] = {"url": f"data:image/png;base64,{b64_data}"}
                logger.info(f"Using image-to-video for scene {scene_id}")
            else:
                logger.info(f"Using text-to-video for scene {scene_id} (no image file)")

            async with httpx.AsyncClient(timeout=30.0) as http:
                # Submit video generation request
                resp = await http.post(
                    "https://api.x.ai/v1/videos/generations",
                    headers=headers,
                    json=body,
                )
                resp.raise_for_status()
                request_id = resp.json()["request_id"]
                logger.info(f"Video generation started for scene {scene_id}: {request_id}")

            # Poll for result (up to 5 minutes, every 5 seconds)
            max_polls = 60
            async with httpx.AsyncClient(timeout=30.0) as http:
                for poll in range(max_polls):
                    await asyncio.sleep(5)
                    poll_resp = await http.get(
                        f"https://api.x.ai/v1/videos/{request_id}",
                        headers={"Authorization": f"Bearer {settings.xai_api_key}"},
                    )
                    poll_data = poll_resp.json()

                    # Response format: {"video": {"url": "..."}, "model": "..."}
                    video_obj = poll_data.get("video", {})
                    video_url = video_obj.get("url") if isinstance(video_obj, dict) else poll_data.get("url")
                    if video_url:
                        # Download and save the video
                        video_resp = await http.get(video_url)
                        STATIC_VIDEOS_DIR.mkdir(parents=True, exist_ok=True)
                        video_path = STATIC_VIDEOS_DIR / f"{scene_id}.mp4"
                        video_path.write_bytes(video_resp.content)

                        if video_path.stat().st_size == 0:
                            raise ValueError("Downloaded video file is empty")

                        image.video_url = f"/static/videos/{scene_id}.mp4"
                        image.video_status = "complete"
                        logger.info(f"Video generated for scene {scene_id}")
                        return

                    if "error" in poll_data:
                        raise ValueError(f"Video generation error: {poll_data['error']}")

                # Timeout
                raise TimeoutError(
                    f"Video generation timed out after {max_polls * 5}s"
                )

        except Exception as e:
            image.video_status = "failed"
            image.video_error = str(e)
            logger.error(f"Video generation failed for scene {scene_id}: {e}")
