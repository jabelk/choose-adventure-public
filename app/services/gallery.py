import json
import logging
from datetime import datetime
from pathlib import Path

from app.models import (
    SavedChoice,
    SavedScene,
    SavedStory,
    StorySession,
)

logger = logging.getLogger(__name__)

STORIES_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "stories"
PROGRESS_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "progress"


class GalleryService:
    def __init__(self):
        STORIES_DIR.mkdir(parents=True, exist_ok=True)
        PROGRESS_DIR.mkdir(parents=True, exist_ok=True)

    def save_story(self, story_session: StorySession) -> None:
        """Convert a completed StorySession to SavedStory and write to disk."""
        story = story_session.story

        # Convert scenes
        saved_scenes: dict[str, SavedScene] = {}
        for sid, scene in story_session.scenes.items():
            # Collect extra image URLs and prompts from picture book mode
            extra_urls = [
                ei.url for ei in scene.extra_images
                if ei.status.value == "complete" and ei.url
            ]
            extra_prompts = [
                ei.prompt for ei in scene.extra_images
                if ei.status.value == "complete" and ei.url
            ]

            saved_scenes[sid] = SavedScene(
                scene_id=scene.scene_id,
                parent_scene_id=scene.parent_scene_id,
                choice_taken_id=scene.choice_taken_id,
                content=scene.content,
                image_url=scene.image.url if scene.image else None,
                image_prompt=scene.image.prompt if scene.image else "",
                video_url=scene.image.video_url if scene.image and scene.image.video_url else None,
                extra_image_urls=extra_urls,
                extra_image_prompts=extra_prompts,
                choices=[
                    SavedChoice(
                        choice_id=c.choice_id,
                        text=c.text,
                        next_scene_id=c.next_scene_id,
                    )
                    for c in scene.choices
                ],
                is_ending=scene.is_ending,
                depth=scene.depth,
            )

        saved = SavedStory(
            story_id=story.story_id,
            title=story.title,
            prompt=story.prompt,
            tier=story.tier,
            length=story.length.value,
            target_depth=story.target_depth,
            model=story.model,
            image_model=story.image_model,
            video_mode=story.video_mode,
            bedtime_mode=story.bedtime_mode,
            intensity=story.intensity,
            art_style=story.art_style,
            protagonist_gender=story.protagonist_gender,
            protagonist_age=story.protagonist_age,
            character_type=story.character_type,
            num_characters=story.num_characters,
            writing_style=story.writing_style,
            conflict_type=story.conflict_type,
            kinks=story.kinks,
            character_name=story.character_name,
            character_description=story.character_description,
            parent_story_id=story.parent_story_id,
            roster_character_ids=list(story.roster_character_ids),
            created_at=story.created_at,
            completed_at=datetime.now(),
            scenes=saved_scenes,
            path_history=list(story_session.path_history),
        )

        filepath = STORIES_DIR / f"{story.story_id}.json"
        try:
            filepath.write_text(
                saved.model_dump_json(indent=2),
                encoding="utf-8",
            )
            logger.info(f"Saved story {story.story_id} to {filepath}")

            # Update parent story's forward reference if this is a sequel
            if story.parent_story_id:
                self.update_sequel_link(story.parent_story_id, story.story_id)
        except Exception as e:
            logger.error(f"Failed to save story {story.story_id}: {e}")

    def list_stories(self, tier: str) -> list[SavedStory]:
        """Load all saved stories for a tier, sorted newest first."""
        stories: list[SavedStory] = []
        if not STORIES_DIR.exists():
            return stories

        for filepath in STORIES_DIR.glob("*.json"):
            try:
                data = json.loads(filepath.read_text(encoding="utf-8"))
                saved = SavedStory.model_validate(data)
                if saved.tier == tier:
                    stories.append(saved)
            except Exception as e:
                logger.warning(f"Skipping corrupted story file {filepath}: {e}")

        stories.sort(key=lambda s: s.completed_at, reverse=True)
        return stories

    def get_story(self, story_id: str) -> SavedStory | None:
        """Load a single saved story by ID."""
        filepath = STORIES_DIR / f"{story_id}.json"
        if not filepath.exists():
            return None

        try:
            data = json.loads(filepath.read_text(encoding="utf-8"))
            return SavedStory.model_validate(data)
        except Exception as e:
            logger.warning(f"Failed to load story {story_id}: {e}")
            return None

    def update_story(self, saved: SavedStory) -> None:
        """Write an updated SavedStory back to disk."""
        filepath = STORIES_DIR / f"{saved.story_id}.json"
        try:
            filepath.write_text(
                saved.model_dump_json(indent=2),
                encoding="utf-8",
            )
            logger.info(f"Updated story {saved.story_id}")
        except Exception as e:
            logger.error(f"Failed to update story {saved.story_id}: {e}")
            raise

    def save_progress(self, tier_name: str, story_session: StorySession) -> None:
        """Save an in-progress story session to disk."""
        filepath = PROGRESS_DIR / f"{tier_name}.json"
        try:
            filepath.write_text(
                story_session.model_dump_json(indent=2),
                encoding="utf-8",
            )
            logger.info(f"Saved progress for tier {tier_name}")
        except Exception as e:
            logger.error(f"Failed to save progress for tier {tier_name}: {e}")

    def load_progress(self, tier_name: str) -> StorySession | None:
        """Load an in-progress story session from disk."""
        filepath = PROGRESS_DIR / f"{tier_name}.json"
        if not filepath.exists():
            return None

        try:
            data = json.loads(filepath.read_text(encoding="utf-8"))
            return StorySession.model_validate(data)
        except Exception as e:
            logger.warning(f"Corrupted progress file for tier {tier_name}: {e}")
            self.delete_progress(tier_name)
            return None

    def delete_progress(self, tier_name: str) -> None:
        """Delete the in-progress save file for a tier."""
        filepath = PROGRESS_DIR / f"{tier_name}.json"
        if filepath.exists():
            try:
                filepath.unlink()
                logger.info(f"Deleted progress for tier {tier_name}")
            except Exception as e:
                logger.error(f"Failed to delete progress for tier {tier_name}: {e}")

    def update_sequel_link(self, parent_story_id: str, sequel_story_id: str) -> None:
        """Add a sequel's ID to the parent story's sequel_story_ids list."""
        filepath = STORIES_DIR / f"{parent_story_id}.json"
        if not filepath.exists():
            logger.warning(f"Parent story {parent_story_id} not found for sequel link")
            return

        try:
            data = json.loads(filepath.read_text(encoding="utf-8"))
            sequel_ids = data.get("sequel_story_ids", [])
            if sequel_story_id not in sequel_ids:
                sequel_ids.append(sequel_story_id)
                data["sequel_story_ids"] = sequel_ids
                filepath.write_text(
                    json.dumps(data, indent=2, default=str),
                    encoding="utf-8",
                )
                logger.info(f"Added sequel link {sequel_story_id} to parent {parent_story_id}")
        except Exception as e:
            logger.error(f"Failed to update sequel link for {parent_story_id}: {e}")

