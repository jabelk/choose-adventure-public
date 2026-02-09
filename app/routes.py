import asyncio
import logging
import random
import time
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, Request, Form, File, UploadFile
from fastapi.responses import RedirectResponse, JSONResponse, Response

from app.main import templates
from app.models import (
    Story,
    Scene,
    Choice,
    Image,
    ImageStatus,
    StoryLength,
    StorySession,
)
from app.session import create_session, get_session, update_session, delete_session
from app.services.story import StoryService
from app.services.image import ImageService
from app.services.gallery import GalleryService
from app.services.export import export_html, export_pdf
from app.services.profile import ProfileService
from app.services.upload import UploadService
from app.services.character import CharacterService
from app.services.family import FamilyService
from app.config import settings as app_settings
from app.tiers import TierConfig, BEDTIME_CONTENT_GUIDELINES, BEDTIME_IMAGE_STYLE
from app.tree import build_tree
from app.models_registry import (
    get_available_models,
    get_model_display_name,
    get_available_image_models,
    get_image_model_display_name,
    get_art_styles,
    get_art_style_prompt,
)
from app.story_options import get_option_groups, build_story_flavor_prompt, is_picture_book_age, build_kink_prompt, build_intensity_prompt, KINK_TOGGLES
from app.services.image import FAST_IMAGE_MODEL
from app.services.tts import generate_speech
from app.services.bible import BibleService

logger = logging.getLogger(__name__)

# Fallback prompts when a tier has no templates defined
_SURPRISE_FALLBACK_KIDS = [
    "A friendly dragon learns to bake cupcakes for the village party.",
    "Two best friends discover a secret garden that grows candy flowers.",
    "A brave little mouse sets off to find the moon's lost glow.",
    "A baby penguin accidentally hatches a magical golden egg.",
    "A group of woodland animals build a treehouse in the tallest oak.",
]

_SURPRISE_FALLBACK_BIBLE = [
    "Noah builds an enormous ark and gathers two of every animal before the great flood. Based on Genesis 6-9.",
    "Young David faces the giant Goliath with nothing but faith and five smooth stones. Based on 1 Samuel 17.",
    "Daniel is thrown into a den of hungry lions, but God sends an angel to keep him safe. Based on Daniel 6.",
    "Jonah tries to run away from God and ends up inside an enormous fish. Based on Jonah 1-2.",
    "Jesus calms a raging storm on the Sea of Galilee while his disciples watch in awe. Based on Mark 4:35-41.",
    "The Good Samaritan stops to help a stranger when everyone else walks by. Based on Luke 10:25-37.",
    "Baby Moses is hidden in a basket on the river and found by a kind princess. Based on Exodus 2:1-10.",
    "Jesus feeds five thousand people with just five loaves of bread and two fish. Based on John 6:1-14.",
]


story_service = StoryService()
image_service = ImageService()
gallery_service = GalleryService()
profile_service = ProfileService()
upload_service = UploadService()
character_service = CharacterService()
family_service = FamilyService()
bible_service = BibleService()

def create_tier_router(tier_config: TierConfig) -> APIRouter:
    """Create a router for a specific audience tier.

    All route handlers are scoped to the tier via closure over tier_config.
    Session cookies are scoped to the tier's URL prefix.
    """
    router = APIRouter(prefix=f"/{tier_config.prefix}")
    url_prefix = f"/{tier_config.prefix}"
    cookie_path = f"/{tier_config.prefix}/"
    session_cookie = f"session_{tier_config.prefix}"

    def _setup_extra_images(scene, main_prompt, image_model, photo_paths):
        """If picture book mode is active, create extra Image objects and kick off generation."""
        story = None  # Will be set from caller context
        # Caller passes protagonist_age; this is checked before calling
        extra_images = [Image(prompt="") for _ in range(2)]
        scene.extra_images = extra_images

        # Determine fast model: use gpt-image-1-mini if available, else user's model
        available_image_keys = [m.key for m in get_available_image_models()]
        fast_model = FAST_IMAGE_MODEL if FAST_IMAGE_MODEL in available_image_keys else image_model

        asyncio.create_task(
            image_service.generate_extra_images(
                extra_images, scene.scene_id, main_prompt,
                fast_model, reference_images=photo_paths or None,
            )
        )

    def _start_cover_art(story_session):
        """Kick off async cover art generation for a completed story."""
        story = story_session.story
        asyncio.create_task(
            gallery_service.generate_cover_art(
                image_service=image_service,
                story_id=story.story_id,
                title=story.title,
                prompt=story.prompt,
                image_model=story.image_model,
                tier=tier_config.name,
                art_style=story.art_style,
            )
        )

    async def _chain_video_after_image(image, scene_id):
        """Wait for image generation to complete, then generate video."""
        max_wait = 120  # 2 minutes
        waited = 0
        while image.status not in (ImageStatus.COMPLETE, ImageStatus.FAILED) and waited < max_wait:
            await asyncio.sleep(2)
            waited += 2
        if image.status == ImageStatus.COMPLETE:
            await image_service.generate_video(image, scene_id)

    def _ctx(extra: dict | None = None) -> dict:
        """Build common template context with tier info."""
        ctx = {"tier": tier_config, "url_prefix": url_prefix}
        if extra:
            ctx.update(extra)
        return ctx

    def _advance_relationships_for_story(story_session):
        """Advance relationship stage for all roster characters in a completed story (NSFW only)."""
        if tier_config.name != "nsfw":
            return
        roster_ids = getattr(story_session.story, "roster_character_ids", [])
        for rc_id in roster_ids:
            character_service.advance_relationship(tier_config.name, rc_id)

    def _get_story_session(request: Request) -> StorySession | None:
        session_id = request.cookies.get(session_cookie)
        if not session_id:
            return None
        return get_session(session_id)

    def _build_reference_images(story_session: StorySession) -> list[str] | None:
        """Build the reference image list for image generation.

        Priority: direct uploads > roster character photos > generated scene reference.
        Capped at 3 total images.
        """
        story = story_session.story

        # Direct uploads take highest priority
        if story.reference_photo_paths:
            return story.reference_photo_paths[:3] or None

        refs: list[str] = []
        # Collect roster character photos
        for rc_id in story.roster_character_ids:
            rc = character_service.get_character(tier_config.name, rc_id)
            if rc:
                rc_photos = character_service.get_absolute_photo_paths(rc)
                for rp in rc_photos:
                    if len(refs) < 3:
                        refs.append(rp)

        # Append generated scene reference if available and file exists
        if story.generated_reference_path:
            gen_path = Path(story.generated_reference_path)
            if gen_path.exists() and len(refs) < 3:
                refs.append(str(gen_path))

        return refs or None

    async def _generate_and_track_reference(
        image: Image, scene_id: str, image_model: str,
        reference_images: list[str] | None, story: Story,
    ) -> None:
        """Wrapper around generate_image that updates the rolling reference on success."""
        await image_service.generate_image(
            image, scene_id, image_model,
            reference_images=reference_images,
        )
        if image.status == ImageStatus.COMPLETE:
            from app.services.image import STATIC_IMAGES_DIR
            gen_path = STATIC_IMAGES_DIR / f"{scene_id}.png"
            if gen_path.exists():
                story.generated_reference_path = str(gen_path)

    def _get_session_id(request: Request) -> str | None:
        return request.cookies.get(session_cookie)

    @router.get("/")
    async def tier_home(request: Request):
        """Tier home page with prompt input form."""
        error = request.query_params.get("error")

        # Check for in-progress story to show resume banner
        resume_story = None
        progress = gallery_service.load_progress(tier_config.name)
        if progress:
            resume_story = {
                "title": progress.story.title,
                "prompt": progress.story.prompt,
                "scene_count": len(progress.path_history),
            }

        resume_chat = None

        # Get available models and determine effective default
        available_models = get_available_models()
        default_model = tier_config.default_model
        available_keys = [m.key for m in available_models]
        if default_model not in available_keys and available_models:
            default_model = available_models[0].key

        # Get available image models and determine effective default
        available_image_models = get_available_image_models()
        default_image_model = tier_config.default_image_model
        available_image_keys = [m.key for m in available_image_models]
        if default_image_model not in available_image_keys and available_image_models:
            default_image_model = available_image_models[0].key

        # Get profiles for memory mode toggle
        profiles = profile_service.list_profiles(tier_config.name)

        # Get roster characters for character picker
        import json
        roster_characters = []
        roster_characters_json = "[]"
        roster_characters = character_service.list_characters(tier_config.name)
        if roster_characters:
            # Build JSON for picker initialization
            roster_json_data = []
            for char in roster_characters:
                photo_urls = []
                for pp in char.photo_paths:
                    fname = pp.split("/")[-1]
                    photo_urls.append(f"{url_prefix}/characters/{char.character_id}/photo/{fname}")
                roster_json_data.append({
                    "character_id": char.character_id,
                    "name": char.name,
                    "description": char.description,
                    "photo_urls": photo_urls,
                    "photo_count": len(char.photo_paths),
                    "relationship_stage": char.relationship_stage,
                    "story_count": char.story_count,
                })
            roster_characters_json = json.dumps(roster_json_data)

        # Get family for Family Mode toggle
        family = family_service.get_family(tier_config.name)

        # Build inline attribute config for character section
        from app.story_options import get_attributes_for_tier
        tier_attrs = get_attributes_for_tier(tier_config.name)
        inline_attrs_grouped: dict[str, list] = {}
        for key, attr in tier_attrs.items():
            group = attr["group"]
            if group not in inline_attrs_grouped:
                inline_attrs_grouped[group] = []
            inline_attrs_grouped[group].append({
                "key": key,
                "label": attr["label"],
                "options": attr["options"],
            })
        inline_attrs_json = json.dumps(inline_attrs_grouped)

        return templates.TemplateResponse(
            request, "home.html", _ctx({
                "error": error,
                "resume_story": resume_story,
                "resume_chat": resume_chat,
                "available_models": available_models,
                "default_model": default_model,
                "available_image_models": available_image_models,
                "default_image_model": default_image_model,
                "art_styles": get_art_styles(tier_config.name),
                "kink_toggles": KINK_TOGGLES,
                "story_option_groups": get_option_groups(),
                "profiles": profiles,
                "video_mode_available": bool(app_settings.xai_api_key),
                "roster_characters": roster_characters,
                "roster_characters_json": roster_characters_json,
                "family": family,
                "inline_attrs_json": inline_attrs_json,
            })
        )

    @router.post("/story/start")
    async def start_story(
        request: Request,
        prompt: str = Form(...),
        length: str = Form("medium"),
        model: str = Form(None),
        image_model: str = Form(None),
        art_style: str = Form("none"),
        protagonist_gender: str = Form(""),
        protagonist_age: str = Form(""),
        character_type: str = Form(""),
        num_characters: str = Form(""),
        writing_style: str = Form(""),
        conflict_type: str = Form(""),
        kinks: list[str] = Form(default=[]),
        intensity: str = Form(""),
        character_name: str = Form(""),
        character_description: str = Form(""),
        video_mode: str = Form(""),
        bedtime_mode: str = Form(""),
        memory_mode: str = Form(""),
        profile_id: str = Form(""),
        roster_character_ids: list[str] = Form(default=[]),
        template_fallback_characters: str = Form(""),
        reference_photos: list[UploadFile] = File(default=[]),
        family_mode: str = Form(""),
        bible_reference_mode: str = Form(""),
    ):
        """Start a new story within this tier."""
        # Fall back to tier defaults if not provided
        if not model:
            model = tier_config.default_model
        if not image_model:
            image_model = tier_config.default_image_model

        if not prompt or not prompt.strip():
            return RedirectResponse(
                url=f"{url_prefix}/?error=Please+describe+your+adventure!",
                status_code=303,
            )

        prompt = prompt.strip()

        # Handle Bible guided reference mode
        if bible_reference_mode == "on" and tier_config.name == "bible":
            if not bible_service.validate_reference(prompt):
                import urllib.parse
                error_msg = urllib.parse.quote(
                    "That doesn't look like a Bible reference. "
                    "Try a book name like \"Genesis 1\", \"Psalm 23\", or \"John 3:16\", "
                    "or pick a story from the library above."
                )
                return RedirectResponse(
                    url=f"{url_prefix}/?error={error_msg}",
                    status_code=303,
                )
            # Build a scripturally constrained prompt from the reference
            scripture_ref = prompt
            verse_text = await bible_service.fetch_verses(scripture_ref)
            prompt = (
                f"Tell an interactive Bible story based on {scripture_ref}. "
                f"Follow the actual biblical narrative faithfully."
            )
            if verse_text:
                prompt += f"\n\nReference scripture text (NIrV): {verse_text}"

        # Clean up previous session's uploads if starting a new story
        old_session_id = _get_session_id(request)
        if old_session_id:
            upload_service.cleanup_session(old_session_id)

        # Validate model against available models, fall back to tier default
        available_keys = [m.key for m in get_available_models()]
        if model not in available_keys:
            model = tier_config.default_model
            if model not in available_keys and available_keys:
                model = available_keys[0]

        # Validate image_model against available image models, fall back to tier default
        available_image_keys = [m.key for m in get_available_image_models()]
        if image_model not in available_image_keys:
            image_model = tier_config.default_image_model
            if image_model not in available_image_keys and available_image_keys:
                image_model = available_image_keys[0]

        # Build content guidelines and image style, augmenting with profile if memory mode is on
        content_guidelines = tier_config.content_guidelines
        image_style = tier_config.image_style
        active_profile_id = None
        photo_paths: list[str] = []

        # Inject scripture reference for Bible tier stories
        if tier_config.name == "bible":
            # Check if prompt matches a template to get scripture_reference
            scripture_ref = ""
            for tpl in tier_config.templates:
                if tpl.prompt == prompt and tpl.scripture_reference:
                    scripture_ref = tpl.scripture_reference
                    break
            # Also check if guided reference mode set a reference
            if bible_reference_mode == "on" and not scripture_ref:
                # The prompt was rewritten above; extract reference from original input
                # The guided reference already injected the reference into the prompt text
                pass
            if scripture_ref:
                scripture_addition = (
                    f"\nSCRIPTURE REFERENCE: {scripture_ref}\n"
                    f"This story MUST follow the narrative from {scripture_ref}. "
                    f"Quote from this passage using the NIrV translation."
                )
                # Try to fetch verse text for template-based stories too
                verse_text = await bible_service.fetch_verses(scripture_ref)
                if verse_text:
                    scripture_addition += f"\n\nNIrV verse text for reference:\n{verse_text}"
                content_guidelines = content_guidelines + "\n" + scripture_addition

        if memory_mode == "on" and profile_id:
            profile = profile_service.get_profile(tier_config.name, profile_id)
            if profile:
                active_profile_id = profile_id
                ctx_addition, style_addition, photo_paths = profile_service.build_profile_context(
                    profile, tier_config.name
                )
                if ctx_addition:
                    content_guidelines = content_guidelines + "\n\n" + ctx_addition
                if style_addition:
                    image_style = (image_style + ", " + style_addition) if image_style else style_addition

        # Inject family context if Family Mode is enabled
        if family_mode == "on":
            family = family_service.get_family(tier_config.name)
            if family:
                family_ctx = family_service.build_family_context(family)
                if family_ctx:
                    content_guidelines = content_guidelines + "\n\n" + family_ctx

        # Apply user-selected art style
        art_style_prompt = get_art_style_prompt(art_style)
        if art_style_prompt:
            image_style = (image_style + ", " + art_style_prompt) if image_style else art_style_prompt

        # Build story flavor from option selections
        story_flavor = build_story_flavor_prompt(
            protagonist_gender=protagonist_gender,
            protagonist_age=protagonist_age,
            character_type=character_type,
            num_characters=num_characters,
            writing_style=writing_style,
            conflict_type=conflict_type,
        )
        if story_flavor:
            content_guidelines = content_guidelines + "\n\n" + story_flavor


        # Build inline character attributes (ignored if roster characters are selected)
        form_data = await request.form()
        inline_attrs: dict[str, str] = {}
        if not roster_character_ids or not any(rid.strip() for rid in roster_character_ids):
            from app.story_options import get_attributes_for_tier as _get_attrs
            from app.services.character import compose_description as _compose
            tier_attrs = _get_attrs(tier_config.name)
            for attr_key in tier_attrs:
                val = form_data.get(f"inline_attr_{attr_key}", "")
                if val and isinstance(val, str) and val.strip():
                    inline_attrs[attr_key] = val.strip()
            if inline_attrs:
                composed = _compose(inline_attrs)
                if composed:
                    if character_description.strip():
                        character_description = composed + " " + character_description.strip()
                    else:
                        character_description = composed

        # Build character prompt from name/description
        character_name = character_name.strip()
        character_description = character_description.strip()
        if character_name:
            char_block = f"CHARACTER:\nName: {character_name}"
            if character_description:
                char_block += f"\nAppearance: {character_description}"
            char_block += "\nThis character MUST appear in every scene. Use their name consistently. Maintain their physical description across all scenes."
            content_guidelines = content_guidelines + "\n\n" + char_block
            # Add character description to image style for visual consistency
            if character_description:
                image_style = (image_style + ", " + character_description) if image_style else character_description

        # Merge profile's character_ids into roster selection (T026)
        if memory_mode == "on" and profile_id:
            profile_obj = profile_service.get_profile(tier_config.name, profile_id)
            if profile_obj and profile_obj.character_ids:
                for pc_id in profile_obj.character_ids:
                    if pc_id not in roster_character_ids:
                        roster_character_ids.append(pc_id)

        # Build roster character context from selected roster characters
        valid_roster_ids: list[str] = []
        for rc_id in roster_character_ids:
            rc_id = rc_id.strip()
            if not rc_id:
                continue
            rc = character_service.get_character(tier_config.name, rc_id)
            if rc:
                valid_roster_ids.append(rc_id)
                char_block = f"CHARACTER:\nName: {rc.name}"
                if rc.description:
                    char_block += f"\nAppearance: {rc.description}"
                # Inject relationship context (NSFW only)
                if tier_config.name == "nsfw" and rc.relationship_stage != "strangers":
                    from app.story_options import RELATIONSHIP_PROMPTS
                    rel_prompt = RELATIONSHIP_PROMPTS.get(rc.relationship_stage, "")
                    if rel_prompt:
                        char_block += f"\nRelationship: {rel_prompt.format(name=rc.name)}"
                char_block += "\nThis character MUST appear in every scene. Use their name consistently. Maintain their physical description across all scenes."
                content_guidelines = content_guidelines + "\n\n" + char_block
                if rc.description:
                    image_style = (image_style + ", " + rc.description) if image_style else rc.description
                # Collect roster character photos (up to 3 total across all characters)
                if len(photo_paths) < 3:
                    rc_photos = character_service.get_absolute_photo_paths(rc)
                    for rp in rc_photos:
                        if len(photo_paths) < 3:
                            photo_paths.append(rp)

        # Handle template fallback characters (roster characters not found)
        if template_fallback_characters:
            try:
                import json
                fallback_chars = json.loads(template_fallback_characters)
                for fc in fallback_chars:
                    fc_name = fc.get("name", "").strip()
                    fc_desc = fc.get("description", "").strip()
                    if fc_name:
                        char_block = f"CHARACTER:\nName: {fc_name}"
                        if fc_desc:
                            char_block += f"\nAppearance: {fc_desc}"
                        char_block += "\nThis character MUST appear in every scene. Use their name consistently. Maintain their physical description across all scenes."
                        content_guidelines = content_guidelines + "\n\n" + char_block
                        if fc_desc:
                            image_style = (image_style + ", " + fc_desc) if image_style else fc_desc
            except (json.JSONDecodeError, TypeError):
                pass

        # Replace any existing in-progress save for this tier (FR-009)
        gallery_service.delete_progress(tier_config.name)

        try:
            story_length = StoryLength(length)
        except ValueError:
            story_length = StoryLength.MEDIUM

        target_depth = story_length.target_depth

        # Apply bedtime mode overrides (kids tier only)
        is_bedtime = bedtime_mode == "on" and tier_config.name == "kids"
        if is_bedtime:
            content_guidelines = content_guidelines + "\n\n" + BEDTIME_CONTENT_GUIDELINES
            image_style = BEDTIME_IMAGE_STYLE
            story_length = StoryLength.SHORT
            target_depth = 3

        try:
            scene_data = await story_service.generate_scene(
                prompt=prompt,
                story_length=story_length,
                context_scenes=[],
                current_depth=0,
                target_depth=target_depth,
                content_guidelines=content_guidelines,
                image_style=image_style,
                model=model,
            )

            image = Image(prompt=scene_data["image_prompt"])
            choices = [Choice(text=c["text"]) for c in scene_data.get("choices", [])]
            scene = Scene(
                content=scene_data["content"],
                image=image,
                choices=choices,
                is_ending=scene_data.get("is_ending", False),
                depth=0,
            )

            story = Story(
                title=scene_data.get("title", "Untitled Adventure"),
                prompt=prompt,
                length=story_length,
                target_depth=target_depth,
                tier=tier_config.name,
                model=model,
                image_model=image_model,
                video_mode=(video_mode == "on"),
                bedtime_mode=is_bedtime,
                intensity=intensity,
                art_style=art_style,
                protagonist_gender=protagonist_gender,
                protagonist_age=protagonist_age,
                character_type=character_type,
                num_characters=num_characters,
                writing_style=writing_style,
                conflict_type=conflict_type,
                kinks=kinks,
                character_name=character_name,
                character_description=character_description,
                profile_id=active_profile_id,
                roster_character_ids=valid_roster_ids,
                current_scene_id=scene.scene_id,
            )

            story_session = StorySession(story=story)
            story_session.navigate_forward(scene)
            session_id = create_session(story_session)

            # Handle direct reference photo uploads (FR-006, FR-008)
            direct_upload_files = [f for f in reference_photos if f.filename]
            if direct_upload_files:
                try:
                    upload_paths = await upload_service.save_upload_files(
                        session_id, direct_upload_files
                    )
                    story_session.story.reference_photo_paths = upload_paths
                    # Direct uploads override profile photos (FR-008)
                    photo_paths = upload_paths
                except ValueError as upload_err:
                    logger.warning(f"Upload validation failed: {upload_err}")
                    # Continue without reference photos rather than failing the story

            ref_images = _build_reference_images(story_session)
            asyncio.create_task(
                _generate_and_track_reference(
                    image, scene.scene_id, image_model,
                    ref_images, story,
                )
            )

            # Picture book mode: generate extra images for young ages
            if is_picture_book_age(protagonist_age):
                _setup_extra_images(scene, scene_data["image_prompt"], image_model, ref_images or [])

            if story.video_mode:
                asyncio.create_task(
                    _chain_video_after_image(image, scene.scene_id)
                )

            # Auto-save if the first scene is already an ending
            if scene.is_ending:
                gallery_service.save_story(story_session)
                _start_cover_art(story_session)
                _advance_relationships_for_story(story_session)
                upload_service.cleanup_session(session_id)
            else:
                gallery_service.save_progress(tier_config.name, story_session)

            redirect = RedirectResponse(
                url=f"{url_prefix}/story/scene/{scene.scene_id}", status_code=303
            )
            redirect.set_cookie(
                key=session_cookie, value=session_id,
                httponly=True, path=cookie_path,
            )
            return redirect

        except Exception as e:
            logger.error(f"Failed to start story: {e}")
            return templates.TemplateResponse(
                request,
                "error.html",
                _ctx({
                    "error_message": f"Failed to generate story: {e}",
                    "retry_url": f"{url_prefix}/",
                }),
            )

    @router.post("/story/surprise")
    async def surprise_me(request: Request, bedtime_mode: str = Form(""), family_mode: str = Form("")):
        """Start a story with randomly selected parameters — zero user input."""
        # Check that at least one AI model is available
        available_models = get_available_models()
        if not available_models:
            return RedirectResponse(
                url=f"{url_prefix}/?error=No+AI+models+available",
                status_code=303,
            )

        # Pick random template or fallback prompt
        if tier_config.templates:
            tpl = random.choice(tier_config.templates)
            prompt = tpl.prompt
            conflict_type = tpl.conflict_type
            kinks = list(tpl.kinks)
            character_name = tpl.character_names[0] if tpl.character_names else ""
            character_description = ""
            if tpl.character_data:
                character_description = tpl.character_data[0].get("description", "")
        else:
            if tier_config.name == "bible":
                fallbacks = _SURPRISE_FALLBACK_BIBLE
            else:
                fallbacks = _SURPRISE_FALLBACK_KIDS
            prompt = random.choice(fallbacks)
            conflict_type = ""
            kinks = []
            character_name = ""
            character_description = ""

        # Random story flavor options (one from each group, tier-appropriate)
        option_groups = get_option_groups()
        flavor_selections = {}
        for group in option_groups:
            choices = group.choices_for_tier(tier_config.name)
            # Filter out the "Any"/"Default" empty-key option sometimes to get variety
            non_default = [c for c in choices if c.key]
            if non_default and random.random() > 0.3:
                selected = random.choice(non_default)
            else:
                selected = choices[0]  # "Any" / "Default"
            flavor_selections[group.name] = selected.key

        # Override conflict_type from template if it was set
        if conflict_type:
            flavor_selections["conflict_type"] = conflict_type

        # Random art style
        art_styles = get_art_styles(tier_config.name)
        art_style = "none"
        if art_styles:
            art_style = random.choice(art_styles).key

        # Random story length
        length = random.choice(["short", "medium", "long"])


        # Pick models
        model = available_models[0].key
        available_image_models = get_available_image_models()
        image_model = tier_config.default_image_model
        if available_image_models:
            available_image_keys = [m.key for m in available_image_models]
            if image_model not in available_image_keys:
                image_model = available_image_models[0].key

        # Clean up previous session's uploads
        old_session_id = _get_session_id(request)
        if old_session_id:
            upload_service.cleanup_session(old_session_id)

        # Build content guidelines and image style
        content_guidelines = tier_config.content_guidelines
        image_style = tier_config.image_style

        # Apply art style
        art_style_prompt = get_art_style_prompt(art_style)
        if art_style_prompt:
            image_style = (image_style + ", " + art_style_prompt) if image_style else art_style_prompt

        # Build story flavor
        story_flavor = build_story_flavor_prompt(**flavor_selections)
        if story_flavor:
            content_guidelines = content_guidelines + "\n\n" + story_flavor

        surprise_intensity = ""

        # Character prompt
        if character_name:
            char_block = f"CHARACTER:\nName: {character_name}"
            if character_description:
                char_block += f"\nAppearance: {character_description}"
            char_block += "\nThis character MUST appear in every scene. Use their name consistently. Maintain their physical description across all scenes."
            content_guidelines = content_guidelines + "\n\n" + char_block
            if character_description:
                image_style = (image_style + ", " + character_description) if image_style else character_description

        # Inject family context if Family Mode is enabled
        if family_mode == "on":
            family = family_service.get_family(tier_config.name)
            if family:
                family_ctx = family_service.build_family_context(family)
                if family_ctx:
                    content_guidelines = content_guidelines + "\n\n" + family_ctx

        # Delete any in-progress story
        gallery_service.delete_progress(tier_config.name)

        try:
            story_length = StoryLength(length)
        except ValueError:
            story_length = StoryLength.MEDIUM

        target_depth = story_length.target_depth

        # Apply bedtime mode overrides (kids tier only)
        is_bedtime = bedtime_mode == "on" and tier_config.name == "kids"
        if is_bedtime:
            content_guidelines = content_guidelines + "\n\n" + BEDTIME_CONTENT_GUIDELINES
            image_style = BEDTIME_IMAGE_STYLE
            story_length = StoryLength.SHORT
            target_depth = 3

        try:
            scene_data = await story_service.generate_scene(
                prompt=prompt,
                story_length=story_length,
                context_scenes=[],
                current_depth=0,
                target_depth=target_depth,
                content_guidelines=content_guidelines,
                image_style=image_style,
                model=model,
            )

            image = Image(prompt=scene_data["image_prompt"])
            choices = [Choice(text=c["text"]) for c in scene_data.get("choices", [])]
            scene = Scene(
                content=scene_data["content"],
                image=image,
                choices=choices,
                is_ending=scene_data.get("is_ending", False),
                depth=0,
            )

            story = Story(
                title=scene_data.get("title", "Untitled Adventure"),
                prompt=prompt,
                length=story_length,
                target_depth=target_depth,
                tier=tier_config.name,
                model=model,
                image_model=image_model,
                bedtime_mode=is_bedtime,
                intensity=surprise_intensity,
                art_style=art_style,
                protagonist_gender=flavor_selections.get("protagonist_gender", ""),
                protagonist_age=flavor_selections.get("protagonist_age", ""),
                character_type=flavor_selections.get("character_type", ""),
                num_characters=flavor_selections.get("num_characters", ""),
                writing_style=flavor_selections.get("writing_style", ""),
                conflict_type=flavor_selections.get("conflict_type", ""),
                kinks=kinks,
                character_name=character_name,
                character_description=character_description,
                current_scene_id=scene.scene_id,
            )

            story_session = StorySession(story=story)
            story_session.navigate_forward(scene)
            session_id = create_session(story_session)

            ref_images = _build_reference_images(story_session)
            asyncio.create_task(
                _generate_and_track_reference(
                    image, scene.scene_id, image_model,
                    ref_images, story,
                )
            )

            # Picture book mode for young ages
            protagonist_age = flavor_selections.get("protagonist_age", "")
            if is_picture_book_age(protagonist_age):
                _setup_extra_images(scene, scene_data["image_prompt"], image_model, ref_images or [])

            if scene.is_ending:
                gallery_service.save_story(story_session)
                _start_cover_art(story_session)
                _advance_relationships_for_story(story_session)
            else:
                gallery_service.save_progress(tier_config.name, story_session)

            redirect = RedirectResponse(
                url=f"{url_prefix}/story/scene/{scene.scene_id}", status_code=303
            )
            redirect.set_cookie(
                key=session_cookie, value=session_id,
                httponly=True, path=cookie_path,
            )
            return redirect

        except Exception as e:
            logger.error(f"Failed to start surprise story: {e}")
            return templates.TemplateResponse(
                request,
                "error.html",
                _ctx({
                    "error_message": f"Failed to generate story: {e}",
                    "retry_url": f"{url_prefix}/",
                }),
            )

    @router.get("/story/scene/{scene_id}")
    async def view_scene(request: Request, scene_id: str):
        """Display a story scene."""
        story_session = _get_story_session(request)
        if not story_session:
            return RedirectResponse(url=f"{url_prefix}/", status_code=303)

        scene = story_session.scenes.get(scene_id)
        if not scene:
            return RedirectResponse(url=f"{url_prefix}/", status_code=303)

        # Compute explored choices (choice IDs that have next_scene_id set)
        explored_choices = {
            c.choice_id for c in scene.choices if c.next_scene_id
        }

        # Build tree data for tree map
        tree_data = build_tree(
            story_session.scenes,
            story_session.story.current_scene_id,
            story_session.path_history,
        )

        # Determine if story has branches (more than one leaf node)
        leaf_count = sum(
            1 for s in story_session.scenes.values()
            if s.is_ending or not any(
                c.next_scene_id for c in s.choices
            )
        )
        has_branches = leaf_count > 1 or len(story_session.scenes) >= 2

        return templates.TemplateResponse(
            request,
            "scene.html",
            _ctx({
                "story": story_session.story,
                "scene": scene,
                "model_display_name": get_model_display_name(story_session.story.model),
                "explored_choices": explored_choices,
                "tree_data": tree_data,
                "has_branches": has_branches,
                "tts_available": bool(app_settings.openai_api_key),
                "tts_voices": tier_config.tts_voices,
                "tts_current_voice": request.cookies.get(f"tts_voice_{tier_config.prefix}", tier_config.tts_default_voice),
                "tts_autoplay": request.cookies.get(f"tts_autoplay_{tier_config.prefix}", str(tier_config.tts_autoplay_default).lower()),
                "bedtime_mode": story_session.story.bedtime_mode,
                "has_reference_images": bool(_build_reference_images(story_session)),
                "has_generated_reference": bool(story_session.story.generated_reference_path),
                "show_recap": scene.depth >= 1,
                "recap_expanded": request.query_params.get("resumed") == "1",
                "recap_url": f"{url_prefix}/story/recap/{scene.scene_id}",
            }),
        )

    @router.get("/story/recap/{scene_id}")
    async def get_recap(request: Request, scene_id: str):
        """Generate or return cached recap for the story so far."""
        story_session = _get_story_session(request)
        if not story_session:
            return JSONResponse({"status": "error"})

        scene = story_session.scenes.get(scene_id)
        if not scene or scene.depth < 1:
            return JSONResponse({"status": "error"})

        # Build cache key from path history up to this scene
        depth = scene.depth
        path_slice = story_session.path_history[:depth + 1]
        cache_key = "|".join(path_slice[:depth])  # scenes before current

        # Check cache
        if cache_key in story_session.recap_cache:
            return JSONResponse({
                "status": "ok",
                "text": story_session.recap_cache[cache_key],
            })

        # Generate recap from scenes along the path before the current one
        context_scenes = [
            story_session.scenes[sid]
            for sid in path_slice[:depth]
            if sid in story_session.scenes
        ]
        if not context_scenes:
            return JSONResponse({"status": "error"})

        # Tier-specific recap style guidance
        recap_styles = {
            "kids": "Use very simple words and short sentences a 3-year-old can understand.",
            "bible": "Use warm, reverent language befitting a Bible story.",
            "nsfw": "Preserve the story's mature tone and atmosphere.",
        }
        recap_style = recap_styles.get(tier_config.name, "")

        recap_text = await story_service.generate_recap(
            scenes=context_scenes,
            model=story_session.story.model,
            content_guidelines=tier_config.content_guidelines,
            recap_style=recap_style,
        )

        if not recap_text:
            return JSONResponse({"status": "error"})

        # Cache and return
        story_session.recap_cache[cache_key] = recap_text
        return JSONResponse({"status": "ok", "text": recap_text})

    @router.post("/story/keep-going/{scene_id}")
    async def keep_going(request: Request, scene_id: str):
        """Extend the story's target depth by 3."""
        story_session = _get_story_session(request)
        session_id = _get_session_id(request)
        if not story_session or not session_id:
            return RedirectResponse(url=f"{url_prefix}/", status_code=303)
        story_session.story.target_depth += 3
        update_session(session_id, story_session)
        return RedirectResponse(
            url=f"{url_prefix}/story/scene/{scene_id}", status_code=303
        )

    @router.post("/story/wrap-up/{scene_id}")
    async def wrap_up(request: Request, scene_id: str):
        """Reduce the story's target depth to end within 1-2 more scenes."""
        story_session = _get_story_session(request)
        session_id = _get_session_id(request)
        if not story_session or not session_id:
            return RedirectResponse(url=f"{url_prefix}/", status_code=303)
        scene = story_session.scenes.get(scene_id)
        if not scene:
            return RedirectResponse(url=f"{url_prefix}/", status_code=303)
        new_target = scene.depth + 2
        if new_target <= scene.depth:
            new_target = scene.depth + 1
        story_session.story.target_depth = new_target
        update_session(session_id, story_session)
        return RedirectResponse(
            url=f"{url_prefix}/story/scene/{scene_id}", status_code=303
        )

    @router.post("/story/reset-appearance")
    async def reset_appearance(request: Request):
        """Clear generated scene reference images for intentional appearance changes."""
        story_session = _get_story_session(request)
        session_id = _get_session_id(request)
        if not story_session or not session_id:
            return RedirectResponse(url=f"{url_prefix}/", status_code=303)
        story_session.story.generated_reference_path = ""
        update_session(session_id, story_session)
        current_scene_id = story_session.story.current_scene_id
        return RedirectResponse(
            url=f"{url_prefix}/story/scene/{current_scene_id}", status_code=303
        )

    @router.post("/story/choose/{scene_id}/{choice_id}")
    async def make_choice(request: Request, scene_id: str, choice_id: str):
        """User selects a choice, generate the next scene."""
        story_session = _get_story_session(request)
        session_id = _get_session_id(request)
        if not story_session or not session_id:
            logger.warning(f"make_choice: no session found. session_id={session_id}, cookie={request.cookies.get(session_cookie)}")
            return RedirectResponse(url=f"{url_prefix}/", status_code=303)

        scene = story_session.scenes.get(scene_id)
        if not scene:
            logger.warning(f"make_choice: scene {scene_id} not found in session. Available: {list(story_session.scenes.keys())}")
            return RedirectResponse(url=f"{url_prefix}/", status_code=303)

        selected_choice = None
        for choice in scene.choices:
            if choice.choice_id == choice_id:
                selected_choice = choice
                break

        if not selected_choice:
            return RedirectResponse(
                url=f"{url_prefix}/story/scene/{scene_id}", status_code=303
            )

        if selected_choice.next_scene_id:
            existing_scene = story_session.scenes.get(selected_choice.next_scene_id)
            if existing_scene:
                # Use navigate_to to rebuild path_history correctly for the branch
                story_session.navigate_to(existing_scene.scene_id)
                update_session(session_id, story_session)
                gallery_service.save_progress(tier_config.name, story_session)
                return RedirectResponse(
                    url=f"{url_prefix}/story/scene/{existing_scene.scene_id}",
                    status_code=303,
                )

        try:
            context_scenes = story_session.get_full_context()
            new_depth = scene.depth + 1

            # Build content guidelines and image style, re-applying profile if active
            content_guidelines = tier_config.content_guidelines
            image_style = tier_config.image_style
            choice_photo_paths: list[str] = []

            if story_session.story.profile_id:
                profile = profile_service.get_profile(
                    tier_config.name, story_session.story.profile_id
                )
                if profile:
                    ctx_addition, style_addition, profile_photos = profile_service.build_profile_context(
                        profile, tier_config.name
                    )
                    if ctx_addition:
                        content_guidelines = content_guidelines + "\n\n" + ctx_addition
                    if style_addition:
                        image_style = (image_style + ", " + style_addition) if image_style else style_addition
                    choice_photo_paths = profile_photos

            # Apply user-selected art style (persisted on story)
            art_style_prompt = get_art_style_prompt(story_session.story.art_style)
            if art_style_prompt:
                image_style = (image_style + ", " + art_style_prompt) if image_style else art_style_prompt

            # Rebuild story flavor from persisted options
            story_flavor = build_story_flavor_prompt(
                protagonist_gender=story_session.story.protagonist_gender,
                protagonist_age=story_session.story.protagonist_age,
                character_type=story_session.story.character_type,
                num_characters=story_session.story.num_characters,
                writing_style=story_session.story.writing_style,
                conflict_type=story_session.story.conflict_type,
            )
            if story_flavor:
                content_guidelines = content_guidelines + "\n\n" + story_flavor


            # Rebuild character prompt from persisted character fields
            if story_session.story.character_name:
                char_block = f"CHARACTER:\nName: {story_session.story.character_name}"
                if story_session.story.character_description:
                    char_block += f"\nAppearance: {story_session.story.character_description}"
                char_block += "\nThis character MUST appear in every scene. Use their name consistently. Maintain their physical description across all scenes."
                content_guidelines = content_guidelines + "\n\n" + char_block
                if story_session.story.character_description:
                    image_style = (image_style + ", " + story_session.story.character_description) if image_style else story_session.story.character_description

            # Rebuild roster character context from persisted roster_character_ids
            for rc_id in story_session.story.roster_character_ids:
                rc = character_service.get_character(tier_config.name, rc_id)
                if rc:
                    char_block = f"CHARACTER:\nName: {rc.name}"
                    if rc.description:
                        char_block += f"\nAppearance: {rc.description}"
                    if tier_config.name == "nsfw" and rc.relationship_stage != "strangers":
                        from app.story_options import RELATIONSHIP_PROMPTS
                        rel_prompt = RELATIONSHIP_PROMPTS.get(rc.relationship_stage, "")
                        if rel_prompt:
                            char_block += f"\nRelationship: {rel_prompt.format(name=rc.name)}"
                    char_block += "\nThis character MUST appear in every scene. Use their name consistently. Maintain their physical description across all scenes."
                    content_guidelines = content_guidelines + "\n\n" + char_block
                    if rc.description:
                        image_style = (image_style + ", " + rc.description) if image_style else rc.description
                    if len(choice_photo_paths) < 3:
                        rc_photos = character_service.get_absolute_photo_paths(rc)
                        for rp in rc_photos:
                            if len(choice_photo_paths) < 3:
                                choice_photo_paths.append(rp)

            # Apply bedtime mode guidelines if active
            if story_session.story.bedtime_mode:
                content_guidelines = content_guidelines + "\n\n" + BEDTIME_CONTENT_GUIDELINES
                image_style = BEDTIME_IMAGE_STYLE

            # Direct uploads take priority over profile photos (FR-008)
            if story_session.story.reference_photo_paths:
                choice_photo_paths = story_session.story.reference_photo_paths

            scene_data = await story_service.generate_scene(
                prompt=story_session.story.prompt,
                story_length=story_session.story.length,
                context_scenes=context_scenes,
                current_depth=new_depth,
                target_depth=story_session.story.target_depth,
                choice_text=selected_choice.text,
                content_guidelines=content_guidelines,
                image_style=image_style,
                model=story_session.story.model,
            )

            new_image = Image(prompt=scene_data["image_prompt"])
            new_choices = [
                Choice(text=c["text"]) for c in scene_data.get("choices", [])
            ]
            new_scene = Scene(
                content=scene_data["content"],
                image=new_image,
                choices=new_choices,
                is_ending=scene_data.get("is_ending", False),
                depth=new_depth,
                parent_scene_id=scene.scene_id,
                choice_taken_id=choice_id,
            )

            selected_choice.next_scene_id = new_scene.scene_id
            story_session.navigate_forward(new_scene)
            update_session(session_id, story_session)

            ref_images = _build_reference_images(story_session)
            asyncio.create_task(
                _generate_and_track_reference(
                    new_image, new_scene.scene_id, story_session.story.image_model,
                    ref_images, story_session.story,
                )
            )

            # Picture book mode: generate extra images for young ages
            if is_picture_book_age(story_session.story.protagonist_age):
                _setup_extra_images(
                    new_scene, scene_data["image_prompt"],
                    story_session.story.image_model, ref_images or [],
                )

            if story_session.story.video_mode:
                asyncio.create_task(
                    _chain_video_after_image(new_image, new_scene.scene_id)
                )

            # Auto-save completed stories to gallery, or save progress
            if new_scene.is_ending:
                gallery_service.save_story(story_session)
                _start_cover_art(story_session)
                _advance_relationships_for_story(story_session)
                gallery_service.delete_progress(tier_config.name)
                if session_id:
                    upload_service.cleanup_session(session_id)
            else:
                gallery_service.save_progress(tier_config.name, story_session)

            return RedirectResponse(
                url=f"{url_prefix}/story/scene/{new_scene.scene_id}",
                status_code=303,
            )

        except Exception as e:
            logger.error(f"Failed to generate next scene: {e}")
            update_session(session_id, story_session)
            return templates.TemplateResponse(
                request,
                "error.html",
                _ctx({
                    "error_message": f"Failed to generate the next scene: {e}",
                    "retry_url": f"{url_prefix}/story/scene/{scene_id}",
                }),
            )

    @router.post("/story/custom-choice/{scene_id}")
    async def custom_choice(request: Request, scene_id: str, custom_text: str = Form(...)):
        """User writes their own choice direction."""
        story_session = _get_story_session(request)
        session_id = _get_session_id(request)
        if not story_session or not session_id:
            return RedirectResponse(url=f"{url_prefix}/", status_code=303)

        scene = story_session.scenes.get(scene_id)
        if not scene:
            return RedirectResponse(url=f"{url_prefix}/", status_code=303)

        custom_text = custom_text.strip()
        if not custom_text:
            return RedirectResponse(
                url=f"{url_prefix}/story/scene/{scene_id}", status_code=303
            )

        try:
            context_scenes = story_session.get_full_context()
            new_depth = scene.depth + 1

            # Build content guidelines and image style
            content_guidelines = tier_config.content_guidelines
            image_style = tier_config.image_style
            choice_photo_paths: list[str] = []

            if story_session.story.profile_id:
                profile = profile_service.get_profile(
                    tier_config.name, story_session.story.profile_id
                )
                if profile:
                    ctx_addition, style_addition, profile_photos = profile_service.build_profile_context(
                        profile, tier_config.name
                    )
                    if ctx_addition:
                        content_guidelines = content_guidelines + "\n\n" + ctx_addition
                    if style_addition:
                        image_style = (image_style + ", " + style_addition) if image_style else style_addition
                    choice_photo_paths = profile_photos

            # Apply user-selected art style
            art_style_prompt = get_art_style_prompt(story_session.story.art_style)
            if art_style_prompt:
                image_style = (image_style + ", " + art_style_prompt) if image_style else art_style_prompt

            # Rebuild story flavor from persisted options
            story_flavor = build_story_flavor_prompt(
                protagonist_gender=story_session.story.protagonist_gender,
                protagonist_age=story_session.story.protagonist_age,
                character_type=story_session.story.character_type,
                num_characters=story_session.story.num_characters,
                writing_style=story_session.story.writing_style,
                conflict_type=story_session.story.conflict_type,
            )
            if story_flavor:
                content_guidelines = content_guidelines + "\n\n" + story_flavor


            # Rebuild character prompt from persisted character fields
            if story_session.story.character_name:
                char_block = f"CHARACTER:\nName: {story_session.story.character_name}"
                if story_session.story.character_description:
                    char_block += f"\nAppearance: {story_session.story.character_description}"
                char_block += "\nThis character MUST appear in every scene. Use their name consistently. Maintain their physical description across all scenes."
                content_guidelines = content_guidelines + "\n\n" + char_block
                if story_session.story.character_description:
                    image_style = (image_style + ", " + story_session.story.character_description) if image_style else story_session.story.character_description

            # Rebuild roster character context from persisted roster_character_ids
            for rc_id in story_session.story.roster_character_ids:
                rc = character_service.get_character(tier_config.name, rc_id)
                if rc:
                    char_block = f"CHARACTER:\nName: {rc.name}"
                    if rc.description:
                        char_block += f"\nAppearance: {rc.description}"
                    if tier_config.name == "nsfw" and rc.relationship_stage != "strangers":
                        from app.story_options import RELATIONSHIP_PROMPTS
                        rel_prompt = RELATIONSHIP_PROMPTS.get(rc.relationship_stage, "")
                        if rel_prompt:
                            char_block += f"\nRelationship: {rel_prompt.format(name=rc.name)}"
                    char_block += "\nThis character MUST appear in every scene. Use their name consistently. Maintain their physical description across all scenes."
                    content_guidelines = content_guidelines + "\n\n" + char_block
                    if rc.description:
                        image_style = (image_style + ", " + rc.description) if image_style else rc.description
                    if len(choice_photo_paths) < 3:
                        rc_photos = character_service.get_absolute_photo_paths(rc)
                        for rp in rc_photos:
                            if len(choice_photo_paths) < 3:
                                choice_photo_paths.append(rp)

            # Apply bedtime mode guidelines if active
            if story_session.story.bedtime_mode:
                content_guidelines = content_guidelines + "\n\n" + BEDTIME_CONTENT_GUIDELINES
                image_style = BEDTIME_IMAGE_STYLE

            # Direct uploads take priority
            if story_session.story.reference_photo_paths:
                choice_photo_paths = story_session.story.reference_photo_paths

            scene_data = await story_service.generate_scene(
                prompt=story_session.story.prompt,
                story_length=story_session.story.length,
                context_scenes=context_scenes,
                current_depth=new_depth,
                target_depth=story_session.story.target_depth,
                choice_text=custom_text,
                content_guidelines=content_guidelines,
                image_style=image_style,
                model=story_session.story.model,
            )

            new_image = Image(prompt=scene_data["image_prompt"])
            new_choices = [
                Choice(text=c["text"]) for c in scene_data.get("choices", [])
            ]

            # Create a Choice on the current scene for the custom text
            custom_choice_obj = Choice(text=custom_text)
            new_scene = Scene(
                content=scene_data["content"],
                image=new_image,
                choices=new_choices,
                is_ending=scene_data.get("is_ending", False),
                depth=new_depth,
                parent_scene_id=scene.scene_id,
                choice_taken_id=custom_choice_obj.choice_id,
            )
            custom_choice_obj.next_scene_id = new_scene.scene_id
            scene.choices.append(custom_choice_obj)

            story_session.navigate_forward(new_scene)
            update_session(session_id, story_session)

            ref_images = _build_reference_images(story_session)
            asyncio.create_task(
                _generate_and_track_reference(
                    new_image, new_scene.scene_id, story_session.story.image_model,
                    ref_images, story_session.story,
                )
            )

            # Picture book mode: generate extra images for young ages
            if is_picture_book_age(story_session.story.protagonist_age):
                _setup_extra_images(
                    new_scene, scene_data["image_prompt"],
                    story_session.story.image_model, ref_images or [],
                )

            if story_session.story.video_mode:
                asyncio.create_task(
                    _chain_video_after_image(new_image, new_scene.scene_id)
                )

            if new_scene.is_ending:
                gallery_service.save_story(story_session)
                _start_cover_art(story_session)
                _advance_relationships_for_story(story_session)
                gallery_service.delete_progress(tier_config.name)
                if session_id:
                    upload_service.cleanup_session(session_id)
            else:
                gallery_service.save_progress(tier_config.name, story_session)

            return RedirectResponse(
                url=f"{url_prefix}/story/scene/{new_scene.scene_id}",
                status_code=303,
            )

        except Exception as e:
            logger.error(f"Failed to generate scene from custom choice: {e}")
            update_session(session_id, story_session)
            return templates.TemplateResponse(
                request,
                "error.html",
                _ctx({
                    "error_message": f"Failed to generate the next scene: {e}",
                    "retry_url": f"{url_prefix}/story/scene/{scene_id}",
                }),
            )

    @router.post("/story/back")
    async def go_back(request: Request):
        """Navigate backward to the previous choice point."""
        story_session = _get_story_session(request)
        session_id = _get_session_id(request)
        if not story_session or not session_id:
            return RedirectResponse(url=f"{url_prefix}/", status_code=303)

        previous = story_session.navigate_backward()
        if previous:
            update_session(session_id, story_session)
            gallery_service.save_progress(tier_config.name, story_session)
            return RedirectResponse(
                url=f"{url_prefix}/story/scene/{previous.scene_id}",
                status_code=303,
            )

        return RedirectResponse(url=f"{url_prefix}/", status_code=303)

    @router.get("/story/tree")
    async def story_tree(request: Request):
        """Return the story tree as JSON for the tree map component."""
        story_session = _get_story_session(request)
        if not story_session:
            return JSONResponse({"tree": {}, "current_id": ""})

        tree = build_tree(
            story_session.scenes,
            story_session.story.current_scene_id,
            story_session.path_history,
        )
        return JSONResponse({
            "tree": tree,
            "current_id": story_session.story.current_scene_id,
        })

    @router.post("/story/navigate/{scene_id}")
    async def navigate_to_scene(request: Request, scene_id: str):
        """Navigate the active story to any explored scene in the tree."""
        story_session = _get_story_session(request)
        session_id = _get_session_id(request)
        if not story_session or not session_id:
            return RedirectResponse(url=f"{url_prefix}/", status_code=303)

        result = story_session.navigate_to(scene_id)
        if not result:
            # Scene not found, redirect to current scene
            return RedirectResponse(
                url=f"{url_prefix}/story/scene/{story_session.story.current_scene_id}",
                status_code=303,
            )

        update_session(session_id, story_session)
        gallery_service.save_progress(tier_config.name, story_session)
        return RedirectResponse(
            url=f"{url_prefix}/story/scene/{scene_id}",
            status_code=303,
        )

    @router.get("/story/resume")
    async def resume_story(request: Request):
        """Restore an in-progress story from disk and redirect to current scene."""
        progress = gallery_service.load_progress(tier_config.name)
        if not progress:
            return RedirectResponse(url=f"{url_prefix}/", status_code=303)

        session_id = create_session(progress)
        redirect = RedirectResponse(
            url=f"{url_prefix}/story/scene/{progress.story.current_scene_id}?resumed=1",
            status_code=303,
        )
        redirect.set_cookie(
            key=session_cookie, value=session_id,
            httponly=True, path=cookie_path,
        )
        return redirect

    @router.post("/story/abandon")
    async def abandon_story(request: Request):
        """Explicitly abandon the current in-progress story."""
        gallery_service.delete_progress(tier_config.name)

        # Clear in-memory session and uploads if one exists
        session_id = _get_session_id(request)
        if session_id:
            upload_service.cleanup_session(session_id)
            delete_session(session_id)

        redirect = RedirectResponse(url=f"{url_prefix}/", status_code=303)
        redirect.delete_cookie(key=session_cookie, path=cookie_path)
        return redirect

    @router.post("/story/image/{scene_id}/retry")
    async def retry_image(request: Request, scene_id: str):
        """Retry a failed image or regenerate an existing one."""
        story_session = _get_story_session(request)
        if not story_session:
            return JSONResponse({"status": "failed"})

        scene = story_session.scenes.get(scene_id)
        if not scene or not scene.image:
            return JSONResponse({"status": "failed"})

        image = scene.image

        # No-op if already generating
        if image.status == ImageStatus.GENERATING:
            return JSONResponse({"status": "generating"})

        # If the image was already complete, add a variation hint so the
        # model produces a different composition instead of the same image
        was_complete = image.status == ImageStatus.COMPLETE
        if was_complete:
            import random as _rng
            _variations = [
                "Use a different camera angle and composition.",
                "Try a different lighting setup and color palette.",
                "Change the character's pose and expression.",
                "Use a different artistic framing and perspective.",
                "Vary the background details and atmosphere.",
                "Shift the mood with different lighting and shadows.",
            ]
            variation_hint = _rng.choice(_variations)
            image.prompt = f"{image.prompt} [{variation_hint}]"

        # Reset image state
        image.status = ImageStatus.PENDING
        image.url = None
        image.error = None

        # Start new background generation with reference images
        ref_images = _build_reference_images(story_session)
        asyncio.create_task(
            _generate_and_track_reference(
                image, scene_id, story_session.story.image_model,
                ref_images, story_session.story,
            )
        )

        # Persist progress
        gallery_service.save_progress(tier_config.name, story_session)

        return JSONResponse({"status": "generating"})

    @router.post("/story/image/{scene_id}/regenerate")
    async def regenerate_image(request: Request, scene_id: str):
        """Regenerate a scene image with a user-edited prompt."""
        story_session = _get_story_session(request)
        if not story_session:
            return JSONResponse({"status": "failed", "error": "No active story"})

        scene = story_session.scenes.get(scene_id)
        if not scene or not scene.image:
            return JSONResponse({"status": "failed", "error": "Scene not found"})

        try:
            body = await request.json()
        except Exception:
            return JSONResponse({"status": "failed", "error": "Invalid request"})

        new_prompt = (body.get("prompt") or "").strip()
        if not new_prompt:
            return JSONResponse({"status": "failed", "error": "Prompt cannot be empty"})

        image = scene.image

        # No-op if already generating
        if image.status == ImageStatus.GENERATING:
            return JSONResponse({"status": "generating"})

        # Update prompt and reset image state
        image.prompt = new_prompt
        image.status = ImageStatus.PENDING
        image.url = None
        image.error = None

        # Start new background generation with reference images
        ref_images = _build_reference_images(story_session)
        asyncio.create_task(
            _generate_and_track_reference(
                image, scene_id, story_session.story.image_model,
                ref_images, story_session.story,
            )
        )

        # Persist progress
        gallery_service.save_progress(tier_config.name, story_session)

        return JSONResponse({"status": "generating"})

    @router.post("/story/image/{scene_id}/retry-extra/{index}")
    async def retry_extra_image(request: Request, scene_id: str, index: int):
        """Retry a failed extra image by index."""
        story_session = _get_story_session(request)
        if not story_session:
            return JSONResponse({"status": "failed"})

        scene = story_session.scenes.get(scene_id)
        if not scene or index < 0 or index >= len(scene.extra_images):
            return JSONResponse({"status": "failed"})

        extra_img = scene.extra_images[index]

        if extra_img.status == ImageStatus.GENERATING:
            return JSONResponse({"status": "generating"})

        # Reset and regenerate using the original prompt
        original_prompt = extra_img.prompt
        extra_img.status = ImageStatus.PENDING
        extra_img.url = None
        extra_img.error = None

        # Determine fast model
        available_image_keys = [m.key for m in get_available_image_models()]
        fast_model = FAST_IMAGE_MODEL if FAST_IMAGE_MODEL in available_image_keys else story_session.story.image_model

        # Generate directly using the image service
        asyncio.create_task(
            image_service.generate_image(
                extra_img, f"{scene_id}_extra_{index}", fast_model,
            )
        )
        # Restore the prompt (generate_image doesn't change it but be safe)
        extra_img.prompt = original_prompt

        gallery_service.save_progress(tier_config.name, story_session)

        return JSONResponse({"status": "generating"})

    @router.get("/story/image/{scene_id}")
    async def image_status(request: Request, scene_id: str):
        """Check image generation status for a scene."""
        story_session = _get_story_session(request)
        if not story_session:
            return JSONResponse({"status": "failed"})

        scene = story_session.scenes.get(scene_id)
        if not scene:
            return JSONResponse({"status": "failed"})

        image = scene.image
        extra_images_data = []
        for i, ei in enumerate(scene.extra_images):
            ei_type = "close-up" if i == 0 else "wide-shot"
            extra_images_data.append({
                "index": i,
                "status": ei.status.value,
                "url": ei.url if ei.status == ImageStatus.COMPLETE else None,
                "type": ei_type,
            })

        if image.status == ImageStatus.COMPLETE and image.url:
            return JSONResponse({"status": "complete", "url": image.url, "extra_images": extra_images_data})
        elif image.status == ImageStatus.FAILED:
            return JSONResponse({"status": "failed", "extra_images": extra_images_data})
        else:
            return JSONResponse({"status": "generating", "extra_images": extra_images_data})

    @router.get("/story/video/{scene_id}")
    async def video_status(request: Request, scene_id: str):
        """Check video generation status for a scene."""
        story_session = _get_story_session(request)
        if not story_session:
            return JSONResponse({"status": "failed"})

        scene = story_session.scenes.get(scene_id)
        if not scene or not scene.image:
            return JSONResponse({"status": "failed"})

        image = scene.image
        if image.video_status == "complete" and image.video_url:
            return JSONResponse({"status": "complete", "url": image.video_url})
        elif image.video_status == "failed":
            return JSONResponse({"status": "failed"})
        else:
            return JSONResponse({"status": image.video_status})

    @router.post("/story/video/{scene_id}/retry")
    async def retry_video(request: Request, scene_id: str):
        """Retry a failed video generation."""
        story_session = _get_story_session(request)
        if not story_session:
            return JSONResponse({"status": "failed"})

        scene = story_session.scenes.get(scene_id)
        if not scene or not scene.image:
            return JSONResponse({"status": "failed"})

        image = scene.image

        if image.video_status == "generating":
            return JSONResponse({"status": "generating"})

        image.video_status = "pending"
        image.video_url = None
        image.video_error = None

        asyncio.create_task(
            image_service.generate_video(image, scene_id)
        )

        gallery_service.save_progress(tier_config.name, story_session)

        return JSONResponse({"status": "generating"})

    @router.get("/voice/status")
    async def voice_status():
        """Check if server-side voice transcription is available."""
        from app.config import settings
        return JSONResponse({"available": bool(settings.openai_api_key)})

    @router.post("/voice/transcribe")
    async def voice_transcribe(audio: UploadFile):
        """Transcribe uploaded audio using server-side Whisper API."""
        from app.config import settings

        if not settings.openai_api_key:
            return JSONResponse(
                {"error": "Transcription service unavailable"},
                status_code=503,
            )

        if audio is None or audio.filename is None:
            return JSONResponse(
                {"error": "No audio file provided"},
                status_code=400,
            )

        # Read audio and check size (25 MB limit)
        audio_bytes = await audio.read()
        max_size = 25 * 1024 * 1024
        if len(audio_bytes) > max_size:
            return JSONResponse(
                {"error": "Audio file too large (max 25 MB)"},
                status_code=400,
            )

        try:
            from app.services.voice import transcribe_audio
            text = await transcribe_audio(audio_bytes, audio.filename)
            return JSONResponse({"text": text})
        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            return JSONResponse(
                {"error": "Transcription failed"},
                status_code=500,
            )

    # --- Profile Management Routes ---

    @router.get("/profiles")
    async def profiles_page(request: Request):
        """Display profile management page for this tier."""
        error = request.query_params.get("error")
        profiles = profile_service.list_profiles(tier_config.name)
        return templates.TemplateResponse(
            request, "profiles.html", _ctx({
                "profiles": profiles,
                "error": error,
            })
        )

    @router.post("/profiles/create")
    async def create_profile(
        request: Request,
        name: str = Form(...),
        themes: str = Form(""),
        art_style: str = Form(""),
        tone: str = Form(""),
        story_elements: str = Form(""),
    ):
        """Create a new profile in this tier."""
        if not name or not name.strip():
            return RedirectResponse(
                url=f"{url_prefix}/profiles?error=Profile+name+is+required",
                status_code=303,
            )
        themes_list = [t.strip() for t in themes.split(",") if t.strip()] if themes else []
        elements_list = [e.strip() for e in story_elements.split(",") if e.strip()] if story_elements else []
        profile_service.create_profile(
            tier=tier_config.name,
            name=name,
            themes=themes_list,
            art_style=art_style,
            tone=tone,
            story_elements=elements_list,
        )
        return RedirectResponse(url=f"{url_prefix}/profiles", status_code=303)

    @router.get("/profiles/{profile_id}")
    async def edit_profile_page(request: Request, profile_id: str):
        """Display edit form for a profile."""
        error = request.query_params.get("error")
        warning = request.query_params.get("warning")
        profile = profile_service.get_profile(tier_config.name, profile_id)
        if not profile:
            return RedirectResponse(url=f"{url_prefix}/profiles", status_code=303)
        other_profiles = [
            p for p in profile_service.list_profiles(tier_config.name)
            if p.profile_id != profile_id
        ]
        roster_characters = []
        selected_character_ids = []
        return templates.TemplateResponse(
            request, "profile_edit.html", _ctx({
                "profile": profile,
                "other_profiles": other_profiles,
                "roster_characters": roster_characters,
                "selected_character_ids": selected_character_ids,
                "error": error,
                "warning": warning,
            })
        )

    @router.post("/profiles/{profile_id}/update")
    async def update_profile(
        request: Request,
        profile_id: str,
        name: str = Form(...),
        themes: str = Form(""),
        art_style: str = Form(""),
        tone: str = Form(""),
        story_elements: str = Form(""),
    ):
        """Update a profile's preferences."""
        themes_list = [t.strip() for t in themes.split(",") if t.strip()] if themes else []
        elements_list = [e.strip() for e in story_elements.split(",") if e.strip()] if story_elements else []
        profile_service.update_profile(
            tier=tier_config.name,
            profile_id=profile_id,
            name=name,
            themes=themes_list,
            art_style=art_style,
            tone=tone,
            story_elements=elements_list,
        )
        return RedirectResponse(
            url=f"{url_prefix}/profiles/{profile_id}", status_code=303
        )

    @router.post("/profiles/{profile_id}/characters/update")
    async def update_profile_characters(
        request: Request,
        profile_id: str,
        character_ids: list[str] = Form(default=[]),
    ):
        """Update which roster characters are associated with a profile."""
        profile = profile_service.get_profile(tier_config.name, profile_id)
        if not profile:
            return RedirectResponse(url=f"{url_prefix}/profiles", status_code=303)
        # Validate that all character_ids actually exist
        valid_ids = []
        for cid in character_ids:
            if character_service.get_character(tier_config.name, cid):
                valid_ids.append(cid)
        profile.character_ids = valid_ids
        from datetime import datetime
        profile.updated_at = datetime.now()
        profile_service._save_profile(profile)
        return RedirectResponse(
            url=f"{url_prefix}/profiles/{profile_id}", status_code=303
        )

    @router.post("/profiles/{profile_id}/delete")
    async def delete_profile(request: Request, profile_id: str):
        """Delete a profile and clean up references."""
        profile_service.delete_profile(tier_config.name, profile_id)
        return RedirectResponse(url=f"{url_prefix}/profiles", status_code=303)

    @router.post("/profiles/{profile_id}/characters/add")
    async def add_character(
        request: Request,
        profile_id: str,
        name: str = Form(...),
        description: str = Form(...),
        linked_profile_id: str = Form(""),
    ):
        """Add a character to a profile."""
        link_id = linked_profile_id if linked_profile_id else None
        result = profile_service.add_character(
            tier=tier_config.name,
            profile_id=profile_id,
            name=name,
            description=description,
            linked_profile_id=link_id,
        )
        if result is None:
            return RedirectResponse(
                url=f"{url_prefix}/profiles/{profile_id}?error=Could+not+add+character+(max+10)",
                status_code=303,
            )
        return RedirectResponse(
            url=f"{url_prefix}/profiles/{profile_id}", status_code=303
        )

    @router.post("/profiles/{profile_id}/characters/{character_id}/update")
    async def update_character(
        request: Request,
        profile_id: str,
        character_id: str,
        name: str = Form(...),
        description: str = Form(...),
        linked_profile_id: str = Form(""),
    ):
        """Update a character's details."""
        link_id = linked_profile_id if linked_profile_id else None
        profile_service.update_character(
            tier=tier_config.name,
            profile_id=profile_id,
            character_id=character_id,
            name=name,
            description=description,
            linked_profile_id=link_id,
        )
        return RedirectResponse(
            url=f"{url_prefix}/profiles/{profile_id}", status_code=303
        )

    @router.post("/profiles/{profile_id}/characters/{character_id}/delete")
    async def delete_character(
        request: Request, profile_id: str, character_id: str
    ):
        """Remove a character from a profile."""
        profile_service.delete_character(
            tier_config.name, profile_id, character_id
        )
        return RedirectResponse(
            url=f"{url_prefix}/profiles/{profile_id}", status_code=303
        )

    # --- Character Photo Routes ---

    @router.post("/profiles/{profile_id}/characters/{character_id}/photo")
    async def upload_character_photo(
        request: Request, profile_id: str, character_id: str,
        photo: UploadFile = None,
    ):
        """Upload or replace a reference photo for a character."""
        if not photo or not photo.filename:
            return RedirectResponse(
                url=f"{url_prefix}/profiles/{profile_id}?error=No+file+selected",
                status_code=303,
            )

        photo_bytes = await photo.read()
        content_type = photo.content_type or ""

        ok, message = profile_service.save_character_photo(
            tier_config.name, profile_id, character_id,
            photo_bytes, content_type,
        )

        if not ok:
            from urllib.parse import quote
            return RedirectResponse(
                url=f"{url_prefix}/profiles/{profile_id}?error={quote(message or 'Upload failed')}",
                status_code=303,
            )

        if message:  # Warning (e.g., small image)
            from urllib.parse import quote
            return RedirectResponse(
                url=f"{url_prefix}/profiles/{profile_id}?warning={quote(message)}",
                status_code=303,
            )

        return RedirectResponse(
            url=f"{url_prefix}/profiles/{profile_id}", status_code=303
        )

    @router.post("/profiles/{profile_id}/characters/{character_id}/photo/delete")
    async def delete_character_photo(
        request: Request, profile_id: str, character_id: str,
    ):
        """Remove a character's reference photo."""
        profile_service.delete_character_photo(
            tier_config.name, profile_id, character_id
        )
        return RedirectResponse(
            url=f"{url_prefix}/profiles/{profile_id}", status_code=303
        )

    @router.get("/photos/{profile_id}/{character_id}")
    async def serve_character_photo(
        request: Request, profile_id: str, character_id: str,
    ):
        """Serve a character's reference photo (tier-isolated)."""
        photo_path = profile_service.get_character_photo_path(
            tier_config.name, profile_id, character_id
        )
        if not photo_path or not photo_path.exists():
            return Response(status_code=404)

        content_type = "image/jpeg" if photo_path.suffix == ".jpg" else "image/png"
        return Response(
            content=photo_path.read_bytes(),
            media_type=content_type,
        )

    # --- Character Roster Routes ---

    @router.get("/characters")
    async def characters_page(request: Request):
        """Display character management page."""
        import json as _json
        from app.story_options import get_attributes_for_tier
        error = request.query_params.get("error")
        success = request.query_params.get("success")
        edit_id = request.query_params.get("edit")
        edit_outfit_id = request.query_params.get("edit_outfit")
        characters = character_service.list_characters(tier_config.name)
        edit_character = None
        editing_outfit = None
        if edit_id:
            edit_character = character_service.get_character(tier_config.name, edit_id)
            if edit_character and edit_outfit_id:
                for o in edit_character.outfits:
                    if o.outfit_id == edit_outfit_id:
                        editing_outfit = o
                        break
        # Build grouped attributes config for JS
        tier_attrs = get_attributes_for_tier(tier_config.name)
        grouped_attrs: dict[str, list] = {}
        for key, attr in tier_attrs.items():
            group = attr["group"]
            if group not in grouped_attrs:
                grouped_attrs[group] = []
            grouped_attrs[group].append({
                "key": key,
                "label": attr["label"],
                "options": attr["options"],
            })
        preselected = edit_character.attributes if edit_character else {}
        return templates.TemplateResponse(
            request, "characters.html", _ctx({
                "characters": characters,
                "max_characters": character_service.MAX_CHARACTERS,
                "edit_character": edit_character,
                "editing_outfit": editing_outfit,
                "error": error,
                "success": success,
                "attributes_config_json": _json.dumps(grouped_attrs),
                "preselected_attrs_json": _json.dumps(preselected),
            })
        )

    @router.post("/characters/create")
    async def create_character_route(
        request: Request,
        name: str = Form(...),
        description: str = Form(default=""),
        reference_photos: list[UploadFile] = File(default=[]),
    ):
        """Create a new roster character."""
        if not name or not name.strip():
            return RedirectResponse(
                url=f"{url_prefix}/characters?error=Character+name+is+required",
                status_code=303,
            )
        # Collect structured attributes from attr_* form fields
        from app.story_options import get_attributes_for_tier
        form_data = await request.form()
        tier_attrs = get_attributes_for_tier(tier_config.name)
        attributes: dict[str, str] = {}
        for attr_key in tier_attrs:
            val = form_data.get(f"attr_{attr_key}", "")
            if val and isinstance(val, str) and val.strip():
                attributes[attr_key] = val.strip()

        character = character_service.create_character(
            tier_config.name, name, description, attributes=attributes
        )
        if not character:
            if character_service.name_exists(tier_config.name, name):
                return RedirectResponse(
                    url=f"{url_prefix}/characters?error=A+character+with+that+name+already+exists",
                    status_code=303,
                )
            return RedirectResponse(
                url=f"{url_prefix}/characters?error=Character+limit+reached+(20+max)",
                status_code=303,
            )
        # Save photos if provided
        photo_files = [f for f in reference_photos if f.filename]
        if photo_files:
            character_service.save_character_photos(
                tier_config.name, character.character_id, photo_files
            )
        return RedirectResponse(
            url=f"{url_prefix}/characters?success=Character+created",
            status_code=303,
        )

    @router.post("/characters/{character_id}/update")
    async def update_character_route(
        request: Request,
        character_id: str,
        name: str = Form(...),
        description: str = Form(default=""),
        reference_photos: list[UploadFile] = File(default=[]),
        remove_photos: list[str] = Form(default=[]),
    ):
        """Update a roster character."""
        # Remove photos first
        for filename in remove_photos:
            character_service.remove_character_photo(
                tier_config.name, character_id, filename
            )
        # Collect structured attributes from attr_* form fields
        from app.story_options import get_attributes_for_tier
        form_data = await request.form()
        tier_attrs = get_attributes_for_tier(tier_config.name)
        attributes: dict[str, str] = {}
        for attr_key in tier_attrs:
            val = form_data.get(f"attr_{attr_key}", "")
            if val and isinstance(val, str) and val.strip():
                attributes[attr_key] = val.strip()

        # Update name/description/attributes
        updated = character_service.update_character(
            tier_config.name, character_id, name, description, attributes=attributes
        )
        if not updated:
            if character_service.name_exists(tier_config.name, name, exclude_id=character_id):
                return RedirectResponse(
                    url=f"{url_prefix}/characters?error=A+character+with+that+name+already+exists",
                    status_code=303,
                )
            return RedirectResponse(
                url=f"{url_prefix}/characters?error=Character+not+found",
                status_code=303,
            )
        # Save new photos if provided
        photo_files = [f for f in reference_photos if f.filename]
        if photo_files:
            character_service.save_character_photos(
                tier_config.name, character_id, photo_files
            )
        return RedirectResponse(
            url=f"{url_prefix}/characters?success=Character+updated",
            status_code=303,
        )

    @router.post("/characters/{character_id}/delete")
    async def delete_character_route(request: Request, character_id: str):
        """Delete a roster character."""
        character_service.delete_character(tier_config.name, character_id)
        return RedirectResponse(
            url=f"{url_prefix}/characters?success=Character+deleted",
            status_code=303,
        )

    @router.post("/characters/{character_id}/relationship")
    async def update_relationship_route(
        request: Request,
        character_id: str,
        relationship_stage: str = Form(...),
    ):
        """Manually set a character's relationship stage (NSFW only)."""
        from app.story_options import RELATIONSHIP_STAGES
        if relationship_stage not in RELATIONSHIP_STAGES:
            return RedirectResponse(
                url=f"{url_prefix}/characters?edit={character_id}&error=Invalid+relationship+stage",
                status_code=303,
            )
        character = character_service.get_character(tier_config.name, character_id)
        if not character:
            return RedirectResponse(
                url=f"{url_prefix}/characters?error=Character+not+found",
                status_code=303,
            )
        character.relationship_stage = relationship_stage
        character.updated_at = datetime.now()
        character_service._save_character(character)
        return RedirectResponse(
            url=f"{url_prefix}/characters?edit={character_id}&success=Relationship+updated",
            status_code=303,
        )

    @router.get("/characters/{character_id}/photo/{filename}")
    async def serve_roster_photo(
        request: Request, character_id: str, filename: str,
    ):
        """Serve a roster character's reference photo."""
        photo_path = character_service.get_character_photo_path(
            tier_config.name, character_id, filename
        )
        if not photo_path:
            return Response(status_code=404)
        content_type = "image/jpeg" if photo_path.suffix == ".jpg" else "image/png"
        return Response(
            content=photo_path.read_bytes(),
            media_type=content_type,
        )

    # --- Outfit CRUD routes ---

    @router.post("/characters/{character_id}/outfits/create")
    async def create_outfit_route(
        request: Request,
        character_id: str,
        outfit_name: str = Form(...),
        outfit_description: str = Form(...),
        outfit_photo: UploadFile = File(default=None),
    ):
        """Create a new outfit for a character."""
        redir = f"{url_prefix}/characters?edit={character_id}"
        if not outfit_name or not outfit_name.strip():
            return RedirectResponse(url=f"{redir}&error=Outfit+name+is+required", status_code=303)
        if not outfit_description or not outfit_description.strip():
            return RedirectResponse(url=f"{redir}&error=Outfit+description+is+required", status_code=303)
        outfit = character_service.add_outfit(tier_config.name, character_id, outfit_name, outfit_description)
        if not outfit:
            return RedirectResponse(url=f"{redir}&error=An+outfit+with+that+name+already+exists", status_code=303)
        if outfit_photo and outfit_photo.filename:
            character_service.save_outfit_photo(tier_config.name, character_id, outfit.outfit_id, outfit_photo)
        return RedirectResponse(url=f"{redir}&success=Outfit+created", status_code=303)

    @router.post("/characters/{character_id}/outfits/{outfit_id}/update")
    async def update_outfit_route(
        request: Request,
        character_id: str,
        outfit_id: str,
        outfit_name: str = Form(...),
        outfit_description: str = Form(...),
        outfit_photo: UploadFile = File(default=None),
        remove_outfit_photo: str = Form(default=""),
    ):
        """Update an existing outfit."""
        redir = f"{url_prefix}/characters?edit={character_id}"
        if remove_outfit_photo:
            character_service.remove_outfit_photo(tier_config.name, character_id, outfit_id)
        updated = character_service.update_outfit(tier_config.name, character_id, outfit_id, outfit_name, outfit_description)
        if not updated:
            return RedirectResponse(url=f"{redir}&error=Outfit+not+found+or+duplicate+name", status_code=303)
        if outfit_photo and outfit_photo.filename:
            character_service.save_outfit_photo(tier_config.name, character_id, outfit_id, outfit_photo)
        return RedirectResponse(url=f"{redir}&success=Outfit+updated", status_code=303)

    @router.post("/characters/{character_id}/outfits/{outfit_id}/delete")
    async def delete_outfit_route(request: Request, character_id: str, outfit_id: str):
        """Delete an outfit."""
        character_service.delete_outfit(tier_config.name, character_id, outfit_id)
        redir = f"{url_prefix}/characters?edit={character_id}"
        return RedirectResponse(url=f"{redir}&success=Outfit+deleted", status_code=303)

    @router.get("/characters/{character_id}/outfits/{outfit_id}/photo/{filename}")
    async def serve_outfit_photo(request: Request, character_id: str, outfit_id: str, filename: str):
        """Serve an outfit reference photo."""
        photo_path = character_service.get_outfit_photo_path(tier_config.name, character_id, outfit_id, filename)
        if not photo_path:
            return Response(status_code=404)
        content_type = "image/jpeg" if photo_path.suffix == ".jpg" else "image/png"
        return Response(content=photo_path.read_bytes(), media_type=content_type)

    @router.get("/characters/api/list")
    async def list_characters_api(request: Request):
        """Return all roster characters as JSON."""
        characters = character_service.list_characters(tier_config.name)
        result = []
        for char in characters:
            photo_urls = []
            for photo_path in char.photo_paths:
                filename = photo_path.split("/")[-1]
                photo_urls.append(
                    f"{url_prefix}/characters/{char.character_id}/photo/{filename}"
                )
            result.append({
                "character_id": char.character_id,
                "name": char.name,
                "description": char.description,
                "photo_urls": photo_urls,
                "photo_count": len(char.photo_paths),
                "attributes": char.attributes,
                "relationship_stage": char.relationship_stage,
                "story_count": char.story_count,
            })
        return JSONResponse(result)

    @router.get("/characters/api/attributes")
    async def list_attributes_api(request: Request):
        """Return tier-filtered attribute options as JSON."""
        from app.story_options import get_attributes_for_tier
        tier_attrs = get_attributes_for_tier(tier_config.name)
        grouped: dict[str, list] = {}
        for key, attr in tier_attrs.items():
            group = attr["group"]
            if group not in grouped:
                grouped[group] = []
            grouped[group].append({
                "key": key,
                "label": attr["label"],
                "options": attr["options"],
            })
        return JSONResponse(grouped)


    @router.get("/gallery")
    async def gallery(request: Request):
        """Display gallery of completed stories and agent mode chats."""
        stories = gallery_service.list_stories(tier_config.name)
        saved_chats = []
        return templates.TemplateResponse(
            request, "gallery.html", _ctx({
                "stories": stories,
                "saved_chats": saved_chats,
            })
        )

    @router.get("/gallery/{story_id}")
    async def gallery_story(request: Request, story_id: str):
        """Redirect to root scene of a saved story."""
        saved = gallery_service.get_story(story_id)
        if not saved or saved.tier != tier_config.name:
            return RedirectResponse(
                url=f"{url_prefix}/gallery", status_code=303
            )
        # Find root scene (parent_scene_id is None)
        root_scene_id = None
        for sid, scene in saved.scenes.items():
            if scene.parent_scene_id is None:
                root_scene_id = sid
                break
        if not root_scene_id:
            # Fallback: use first in path_history
            root_scene_id = saved.path_history[0] if saved.path_history else None
        if not root_scene_id:
            return RedirectResponse(
                url=f"{url_prefix}/gallery", status_code=303
            )
        return RedirectResponse(
            url=f"{url_prefix}/gallery/{story_id}/{root_scene_id}",
            status_code=303,
        )

    @router.get("/gallery/{story_id}/export/html")
    async def export_story_html(request: Request, story_id: str):
        """Download a completed story as a self-contained HTML file."""
        saved = gallery_service.get_story(story_id)
        if not saved or saved.tier != tier_config.name:
            return RedirectResponse(
                url=f"{url_prefix}/gallery", status_code=303
            )
        html_content = export_html(saved)
        filename = f"{saved.title}.html"
        return Response(
            content=html_content,
            media_type="text/html",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )

    @router.get("/gallery/{story_id}/export/pdf")
    async def export_story_pdf(request: Request, story_id: str):
        """Download a completed story as a PDF document."""
        saved = gallery_service.get_story(story_id)
        if not saved or saved.tier != tier_config.name:
            return RedirectResponse(
                url=f"{url_prefix}/gallery", status_code=303
            )
        pdf_bytes = export_pdf(saved)
        filename = f"{saved.title}.pdf"
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )

    @router.post("/gallery/{story_id}/regenerate-cover")
    async def regenerate_cover(request: Request, story_id: str):
        """Regenerate cover art for a saved story."""
        saved = gallery_service.get_story(story_id)
        if not saved or saved.tier != tier_config.name:
            return RedirectResponse(
                url=f"{url_prefix}/gallery", status_code=303
            )
        saved.cover_art_status = "generating"
        gallery_service.update_story(saved)
        asyncio.create_task(
            gallery_service.generate_cover_art(
                image_service=image_service,
                story_id=saved.story_id,
                title=saved.title,
                prompt=saved.prompt,
                image_model=saved.image_model,
                tier=tier_config.name,
                art_style=saved.art_style,
            )
        )
        # Find root scene to redirect to reader
        root_scene_id = None
        for sid, scene in saved.scenes.items():
            if scene.parent_scene_id is None:
                root_scene_id = sid
                break
        if not root_scene_id:
            root_scene_id = saved.path_history[0] if saved.path_history else None
        if root_scene_id:
            return RedirectResponse(
                url=f"{url_prefix}/gallery/{story_id}/{root_scene_id}",
                status_code=303,
            )
        return RedirectResponse(
            url=f"{url_prefix}/gallery", status_code=303
        )

    # --- Family Mode Routes ---

    @router.get("/family")
    async def family_page(request: Request):
        """Family settings page."""
        family = family_service.get_family(tier_config.name)
        error = request.query_params.get("error")
        success = request.query_params.get("success")
        return templates.TemplateResponse(
            request, "family.html", _ctx({
                "family": family,
                "error": error,
                "success": success,
            })
        )

    @router.post("/family/save")
    async def save_family(
        request: Request,
        child_name: str = Form(""),
        child_gender: str = Form("girl"),
        child_age: int | None = Form(None),
        parent_name: str = Form(""),
    ):
        """Save a new child or parent to the family."""
        from app.models import Family, FamilyChild, FamilyParent

        family = family_service.get_family(tier_config.name)
        if not family:
            family = Family(tier=tier_config.name)

        added = False

        # Add child if name provided
        if child_name.strip() and child_age is not None:
            if len(family.children) < 6:
                gender = child_gender if child_gender in ("girl", "boy", "other") else "other"
                age = max(1, min(17, child_age))
                family.children.append(FamilyChild(
                    name=child_name.strip(), gender=gender, age=age
                ))
                added = True

        # Add parent if name provided
        if parent_name.strip():
            if len(family.parents) < 2:
                family.parents.append(FamilyParent(name=parent_name.strip()))
                added = True

        if added:
            family_service.save_family(family)
            return RedirectResponse(
                url=f"{url_prefix}/family?success=Family+updated!", status_code=303
            )

        return RedirectResponse(
            url=f"{url_prefix}/family?error=Please+fill+in+a+name", status_code=303
        )

    @router.post("/family/remove-child/{index}")
    async def remove_child(request: Request, index: int):
        """Remove a child by index."""
        family = family_service.get_family(tier_config.name)
        if family and 0 <= index < len(family.children):
            family.children.pop(index)
            family_service.save_family(family)
        return RedirectResponse(
            url=f"{url_prefix}/family?success=Child+removed", status_code=303
        )

    @router.post("/family/remove-parent/{index}")
    async def remove_parent(request: Request, index: int):
        """Remove a parent by index."""
        family = family_service.get_family(tier_config.name)
        if family and 0 <= index < len(family.parents):
            family.parents.pop(index)
            family_service.save_family(family)
        return RedirectResponse(
            url=f"{url_prefix}/family?success=Parent+removed", status_code=303
        )

    @router.post("/family/delete")
    async def delete_family(request: Request):
        """Delete the entire family."""
        family_service.delete_family(tier_config.name)
        return RedirectResponse(
            url=f"{url_prefix}/family?success=Family+deleted", status_code=303
        )

    # --- Sequel / Continue Story ---
    # NOTE: These must be declared BEFORE /gallery/{story_id}/{scene_id}
    # to avoid the catch-all scene_id parameter matching "continue".

    @router.get("/gallery/{story_id}/continue")
    async def continue_story_form(request: Request, story_id: str):
        """Show sequel customization form pre-filled with original story settings."""
        saved = gallery_service.get_story(story_id)
        if not saved or saved.tier != tier_config.name:
            return RedirectResponse(
                url=f"{url_prefix}/gallery", status_code=303
            )

        available_models = get_available_models()
        available_image_models = get_available_image_models()
        art_styles = get_art_styles(tier_config.name)
        kink_toggles = {}
        story_option_groups = get_option_groups()

        return templates.TemplateResponse(
            request,
            "sequel_customize.html",
            _ctx({
                "story": saved,
                "available_models": available_models,
                "default_model": saved.model,
                "available_image_models": available_image_models,
                "default_image_model": saved.image_model,
                "art_styles": art_styles,
                "default_art_style": saved.art_style,
                "kink_toggles": kink_toggles,
                "selected_kinks": saved.kinks,
                "default_intensity": "",
                "story_option_groups": story_option_groups,
            }),
        )

    @router.post("/gallery/{story_id}/continue")
    async def continue_story(
        request: Request,
        story_id: str,
        length: str = Form(""),
        sequel_prompt: str = Form(""),
        model: str = Form(""),
        image_model: str = Form(""),
        art_style: str = Form(""),
        kinks: list[str] = Form([]),
        intensity: str = Form(""),
    ):
        """Start a sequel from a completed gallery story."""
        saved = gallery_service.get_story(story_id)
        if not saved or saved.tier != tier_config.name:
            return RedirectResponse(
                url=f"{url_prefix}/gallery", status_code=303
            )

        # Find the ending scene (last in path_history)
        ending_scene = None
        if saved.path_history:
            ending_scene = saved.scenes.get(saved.path_history[-1])
        if not ending_scene:
            # Fallback: find any ending scene
            for s in saved.scenes.values():
                if s.is_ending:
                    ending_scene = s
                    break
        if not ending_scene:
            # Use last scene by highest depth
            ending_scene = max(saved.scenes.values(), key=lambda s: s.depth)

        # Use form values if provided, otherwise inherit from original
        effective_length = length if length else saved.length
        effective_model = model if model else saved.model
        effective_image_model = image_model if image_model else saved.image_model
        effective_art_style = art_style if art_style else saved.art_style
        effective_kinks = kinks if kinks else list(saved.kinks)
        effective_intensity = intensity if intensity else ""

        # Build content guidelines from tier
        content_guidelines = tier_config.content_guidelines
        image_style = tier_config.image_style

        # Apply art style
        art_style_prompt = get_art_style_prompt(effective_art_style)
        if art_style_prompt:
            image_style = (image_style + ", " + art_style_prompt) if image_style else art_style_prompt

        # Rebuild story flavor from inherited fields
        story_flavor = build_story_flavor_prompt(
            protagonist_gender=saved.protagonist_gender,
            protagonist_age=saved.protagonist_age,
            character_type=saved.character_type,
            num_characters=saved.num_characters,
            writing_style=saved.writing_style,
            conflict_type=saved.conflict_type,
        )
        if story_flavor:
            content_guidelines = content_guidelines + "\n\n" + story_flavor


        # Rebuild character prompt
        if saved.character_name:
            char_block = f"CHARACTER:\nName: {saved.character_name}"
            if saved.character_description:
                char_block += f"\nAppearance: {saved.character_description}"
            char_block += "\nThis character MUST appear in every scene. Use their name consistently. Maintain their physical description across all scenes."
            content_guidelines = content_guidelines + "\n\n" + char_block
            if saved.character_description:
                image_style = (image_style + ", " + saved.character_description) if image_style else saved.character_description

        # Rebuild roster character context
        choice_photo_paths: list[str] = []
        valid_roster_ids: list[str] = []
        for rc_id in saved.roster_character_ids:
            rc = character_service.get_character(tier_config.name, rc_id)
            if rc:
                valid_roster_ids.append(rc_id)
                char_block = f"CHARACTER:\nName: {rc.name}"
                if rc.description:
                    char_block += f"\nAppearance: {rc.description}"
                char_block += "\nThis character MUST appear in every scene. Use their name consistently. Maintain their physical description across all scenes."
                content_guidelines = content_guidelines + "\n\n" + char_block
                if rc.description:
                    image_style = (image_style + ", " + rc.description) if image_style else rc.description
                if len(choice_photo_paths) < 3:
                    rc_photos = character_service.get_absolute_photo_paths(rc)
                    for rp in rc_photos:
                        if len(choice_photo_paths) < 3:
                            choice_photo_paths.append(rp)

        # Add sequel context prompt
        sequel_context_block = "SEQUEL CONTEXT:\nThis is a sequel to a previous story. Here is how the previous story ended:\n\n---\n"
        sequel_context_block += ending_scene.content
        sequel_context_block += "\n---\n"
        if sequel_prompt.strip():
            sequel_context_block += f"\nThe user wants the sequel to go in this direction: \"{sequel_prompt.strip()}\"\n"
        sequel_context_block += "\nContinue the narrative from this point. Start a new chapter in the same world with the same characters. Reference events from the ending above but introduce a new plot thread."
        content_guidelines = content_guidelines + "\n\n" + sequel_context_block

        # Clean up previous session
        old_session_id = _get_session_id(request)
        if old_session_id:
            upload_service.cleanup_session(old_session_id)
        gallery_service.delete_progress(tier_config.name)

        try:
            story_length = StoryLength(effective_length)
        except ValueError:
            story_length = StoryLength.MEDIUM

        target_depth = story_length.target_depth

        try:
            scene_data = await story_service.generate_scene(
                prompt=saved.prompt,
                story_length=story_length,
                context_scenes=[],
                current_depth=0,
                target_depth=target_depth,
                content_guidelines=content_guidelines,
                image_style=image_style,
                model=effective_model,
            )

            image = Image(prompt=scene_data["image_prompt"])
            choices = [Choice(text=c["text"]) for c in scene_data.get("choices", [])]
            scene = Scene(
                content=scene_data["content"],
                image=image,
                choices=choices,
                is_ending=scene_data.get("is_ending", False),
                depth=0,
            )

            story = Story(
                title=scene_data.get("title", f"Sequel: {saved.title}"),
                prompt=saved.prompt,
                length=story_length,
                target_depth=target_depth,
                tier=tier_config.name,
                model=effective_model,
                image_model=effective_image_model,
                art_style=effective_art_style,
                protagonist_gender=saved.protagonist_gender,
                protagonist_age=saved.protagonist_age,
                character_type=saved.character_type,
                num_characters=saved.num_characters,
                writing_style=saved.writing_style,
                conflict_type=saved.conflict_type,
                kinks=effective_kinks,
                intensity=effective_intensity,
                character_name=saved.character_name,
                character_description=saved.character_description,
                roster_character_ids=valid_roster_ids,
                parent_story_id=saved.story_id,
                sequel_context=ending_scene.content,
                current_scene_id=scene.scene_id,
            )

            story_session = StorySession(story=story)
            story_session.navigate_forward(scene)
            session_id = create_session(story_session)

            ref_images = _build_reference_images(story_session)
            asyncio.create_task(
                _generate_and_track_reference(
                    image, scene.scene_id, effective_image_model,
                    ref_images, story,
                )
            )

            if scene.is_ending:
                gallery_service.save_story(story_session)
                _start_cover_art(story_session)
                _advance_relationships_for_story(story_session)
            else:
                gallery_service.save_progress(tier_config.name, story_session)

            redirect = RedirectResponse(
                url=f"{url_prefix}/story/scene/{scene.scene_id}", status_code=303
            )
            redirect.set_cookie(
                key=session_cookie, value=session_id,
                path=cookie_path, httponly=True,
            )
            return redirect

        except Exception as e:
            logger.error(f"Sequel generation failed: {e}")
            return RedirectResponse(
                url=f"{url_prefix}/gallery/{story_id}?error=Sequel+generation+failed",
                status_code=303,
            )

    # --- Coloring Page ---

    @router.get("/gallery/{story_id}/{scene_id}/coloring/pdf")
    async def coloring_page_pdf(
        request: Request, story_id: str, scene_id: str
    ):
        """Download a coloring page as a print-ready PDF."""
        saved = gallery_service.get_story(story_id)
        if not saved or saved.tier != tier_config.name:
            return JSONResponse({"error": "Story not found"}, status_code=404)

        scene = saved.scenes.get(scene_id)
        if not scene or not scene.image_prompt:
            return JSONResponse({"error": "Scene or image prompt not found"}, status_code=404)

        # Check if the coloring page PNG exists on disk
        coloring_path = Path(__file__).resolve().parent.parent / "static" / "images" / f"{scene_id}_coloring.png"
        if not coloring_path.exists() or coloring_path.stat().st_size == 0:
            return JSONResponse({"error": "Coloring page not yet generated. Generate it first."}, status_code=404)

        from app.services.export import export_coloring_pdf
        pdf_bytes = bytes(export_coloring_pdf(coloring_path))
        filename = f"{saved.title}_coloring_{scene_id}.pdf"
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )

    @router.get("/gallery/{story_id}/{scene_id}/coloring")
    async def coloring_page(
        request: Request, story_id: str, scene_id: str
    ):
        """Generate a coloring page for a scene and return the URL as JSON."""
        saved = gallery_service.get_story(story_id)
        if not saved or saved.tier != tier_config.name:
            return JSONResponse({"error": "Story not found"}, status_code=404)

        scene = saved.scenes.get(scene_id)
        if not scene or not scene.image_prompt:
            return JSONResponse({"error": "Scene has no image prompt"}, status_code=404)

        try:
            coloring_url = await image_service.generate_coloring_page(
                image_prompt=scene.image_prompt,
                scene_id=scene_id,
                image_model=saved.image_model,
            )
            return JSONResponse({"url": coloring_url})
        except Exception as e:
            logger.error(f"Coloring page generation failed for scene {scene_id}: {e}")
            return JSONResponse(
                {"error": "Coloring page generation failed. Try again."},
                status_code=500,
            )

    # --- Gallery Image Regeneration ---

    @router.post("/gallery/{story_id}/{scene_id}/regenerate-image")
    async def gallery_regenerate_image(
        request: Request, story_id: str, scene_id: str
    ):
        """Regenerate a scene image with a user-edited prompt in the gallery."""
        saved = gallery_service.get_story(story_id)
        if not saved or saved.tier != tier_config.name:
            return JSONResponse(
                {"status": "failed", "error": "Story not found"}, status_code=404
            )

        scene = saved.scenes.get(scene_id)
        if not scene:
            return JSONResponse(
                {"status": "failed", "error": "Scene not found"}, status_code=404
            )

        try:
            body = await request.json()
        except Exception:
            return JSONResponse(
                {"status": "failed", "error": "Invalid request"}, status_code=400
            )

        new_prompt = (body.get("prompt") or "").strip()
        if not new_prompt:
            return JSONResponse(
                {"status": "failed", "error": "Prompt cannot be empty"}, status_code=400
            )

        # Create temporary Image object for generation
        temp_image = Image(prompt=new_prompt)

        try:
            await image_service.generate_image(
                temp_image, scene_id, saved.image_model
            )
        except Exception as e:
            return JSONResponse(
                {"status": "failed", "error": str(e)}
            )

        if temp_image.status != ImageStatus.COMPLETE or not temp_image.url:
            return JSONResponse(
                {"status": "failed", "error": temp_image.error or "Image generation failed"}
            )

        # Update saved scene with new prompt and image URL (cache-bust)
        scene.image_prompt = new_prompt
        scene.image_url = temp_image.url + "?t=" + str(int(time.time()))

        # Persist updated story
        try:
            gallery_service.update_story(saved)
        except Exception as e:
            return JSONResponse(
                {"status": "failed", "error": "Failed to save updated story"}
            )

        return JSONResponse(
            {"status": "complete", "image_url": scene.image_url}
        )

    # --- Gallery Reader (catch-all, must be AFTER /continue and /coloring routes) ---

    @router.get("/gallery/{story_id}/{scene_id}")
    async def gallery_reader(
        request: Request, story_id: str, scene_id: str
    ):
        """Read a specific scene of a saved story by scene ID."""
        saved = gallery_service.get_story(story_id)
        if not saved or saved.tier != tier_config.name:
            return RedirectResponse(
                url=f"{url_prefix}/gallery", status_code=303
            )

        scene = saved.scenes.get(scene_id)
        if not scene:
            return RedirectResponse(
                url=f"{url_prefix}/gallery", status_code=303
            )

        # Build tree data for the gallery reader tree map
        tree_data = build_tree(
            saved.scenes,
            scene_id,
            saved.path_history,
        )

        # Look up sequel chain data
        parent_story = None
        if saved.parent_story_id:
            parent_story = gallery_service.get_story(saved.parent_story_id)
        sequel_stories = []
        for sid in saved.sequel_story_ids:
            sq = gallery_service.get_story(sid)
            if sq:
                sequel_stories.append(sq)

        return templates.TemplateResponse(
            request,
            "reader.html",
            _ctx({
                "story": saved,
                "scene": scene,
                "scene_id": scene_id,
                "tree_data": tree_data,
                "tts_available": bool(app_settings.openai_api_key),
                "tts_voices": tier_config.tts_voices,
                "tts_current_voice": request.cookies.get(f"tts_voice_{tier_config.prefix}", tier_config.tts_default_voice),
                "parent_story": parent_story,
                "sequel_stories": sequel_stories,
            }),
        )

    # --- TTS Narration Endpoints ---

    @router.get("/story/tts/{scene_id}")
    async def story_tts(request: Request, scene_id: str, voice: str | None = None):
        """Generate TTS audio for a scene in the active story."""
        story_session = _get_story_session(request)
        if not story_session:
            return JSONResponse({"detail": "No active story"}, status_code=404)

        scene = story_session.scenes.get(scene_id)
        if not scene:
            return JSONResponse({"detail": "Scene not found"}, status_code=404)

        effective_voice = voice or request.cookies.get(
            f"tts_voice_{tier_config.prefix}", tier_config.tts_default_voice
        )

        try:
            audio_bytes = await generate_speech(
                text=scene.content,
                voice=effective_voice,
                instructions=tier_config.tts_instructions,
            )
        except Exception as e:
            logger.error(f"TTS generation failed: {e}")
            return JSONResponse({"detail": "TTS generation failed"}, status_code=502)

        response = Response(content=audio_bytes, media_type="audio/mpeg")
        if voice:
            response.set_cookie(
                f"tts_voice_{tier_config.prefix}", voice,
                path=cookie_path, httponly=False,
            )
        return response

    @router.get("/gallery/tts/{story_id}/{scene_id}")
    async def gallery_tts(request: Request, story_id: str, scene_id: str, voice: str | None = None):
        """Generate TTS audio for a scene in a saved gallery story."""
        saved = gallery_service.get_story(story_id)
        if not saved or saved.tier != tier_config.name:
            return JSONResponse({"detail": "Story not found"}, status_code=404)

        scene = saved.scenes.get(scene_id)
        if not scene:
            return JSONResponse({"detail": "Scene not found"}, status_code=404)

        effective_voice = voice or request.cookies.get(
            f"tts_voice_{tier_config.prefix}", tier_config.tts_default_voice
        )

        try:
            audio_bytes = await generate_speech(
                text=scene.content,
                voice=effective_voice,
                instructions=tier_config.tts_instructions,
            )
        except Exception as e:
            logger.error(f"TTS generation failed: {e}")
            return JSONResponse({"detail": "TTS generation failed"}, status_code=502)

        response = Response(content=audio_bytes, media_type="audio/mpeg")
        if voice:
            response.set_cookie(
                f"tts_voice_{tier_config.prefix}", voice,
                path=cookie_path, httponly=False,
            )
        return response

    @router.get("/tts/voices")
    async def tts_voices(request: Request):
        """Return available TTS voices for this tier."""
        current_voice = request.cookies.get(
            f"tts_voice_{tier_config.prefix}", tier_config.tts_default_voice
        )
        autoplay = request.cookies.get(
            f"tts_autoplay_{tier_config.prefix}", str(tier_config.tts_autoplay_default).lower()
        )
        return JSONResponse({
            "voices": [{"id": v[0], "name": v[1]} for v in tier_config.tts_voices],
            "current": current_voice,
            "autoplay": autoplay == "true",
        })

    @router.post("/tts/preferences")
    async def tts_preferences(request: Request):
        """Update TTS voice and auto-play preferences."""
        body = await request.json()
        response = JSONResponse({"status": "ok"})

        if "voice" in body:
            response.set_cookie(
                f"tts_voice_{tier_config.prefix}", body["voice"],
                path=cookie_path, httponly=False,
            )
        if "autoplay" in body:
            response.set_cookie(
                f"tts_autoplay_{tier_config.prefix}",
                "true" if body["autoplay"] else "false",
                path=cookie_path, httponly=False,
            )
        return response


    return router
