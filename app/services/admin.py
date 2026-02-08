import json
import logging
import shutil
from pathlib import Path

from app.models import SavedStory, StorySession

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent.parent
STORIES_DIR = BASE_DIR / "data" / "stories"
PROGRESS_DIR = BASE_DIR / "data" / "progress"
UPLOADS_DIR = BASE_DIR / "data" / "uploads"
IMAGES_DIR = BASE_DIR / "static" / "images"
VIDEOS_DIR = BASE_DIR / "static" / "videos"


def _format_size(size_bytes: int) -> str:
    """Format bytes as human-readable string."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"


def _dir_stats(directory: Path, pattern: str) -> tuple[int, int]:
    """Return (file_count, total_bytes) for files matching pattern in directory."""
    if not directory.exists():
        return 0, 0
    count = 0
    total = 0
    for f in directory.glob(pattern):
        if f.is_file():
            count += 1
            total += f.stat().st_size
    return count, total


class AdminService:
    def get_storage_stats(self) -> dict:
        """Return file counts and sizes for all storage directories."""
        story_count, story_bytes = _dir_stats(STORIES_DIR, "*.json")
        progress_count, progress_bytes = _dir_stats(PROGRESS_DIR, "*.json")
        image_count, image_bytes = _dir_stats(IMAGES_DIR, "*.png")
        video_count, video_bytes = _dir_stats(VIDEOS_DIR, "*.mp4")

        return {
            "stories": {"count": story_count, "bytes": story_bytes, "display": _format_size(story_bytes)},
            "progress": {"count": progress_count, "bytes": progress_bytes, "display": _format_size(progress_bytes)},
            "images": {"count": image_count, "bytes": image_bytes, "display": _format_size(image_bytes)},
            "videos": {"count": video_count, "bytes": video_bytes, "display": _format_size(video_bytes)},
            "total_bytes": story_bytes + progress_bytes + image_bytes + video_bytes,
            "total_display": _format_size(story_bytes + progress_bytes + image_bytes + video_bytes),
        }

    def list_all_stories(self) -> list[dict]:
        """Load all saved stories across all tiers. Returns list of metadata dicts."""
        stories = []
        if not STORIES_DIR.exists():
            return stories

        for filepath in sorted(STORIES_DIR.glob("*.json"), reverse=True):
            try:
                data = json.loads(filepath.read_text(encoding="utf-8"))
                saved = SavedStory.model_validate(data)
                stories.append({
                    "story_id": saved.story_id,
                    "title": saved.title,
                    "prompt": saved.prompt[:80],
                    "tier": saved.tier,
                    "model": saved.model,
                    "image_model": saved.image_model,
                    "created_at": saved.created_at,
                    "completed_at": saved.completed_at,
                    "scene_count": len(saved.scenes),
                    "error": False,
                })
            except Exception as e:
                logger.warning(f"Corrupted story file {filepath.name}: {e}")
                stories.append({
                    "story_id": filepath.stem,
                    "title": f"[Corrupted] {filepath.name}",
                    "prompt": "",
                    "tier": "unknown",
                    "model": "",
                    "image_model": "",
                    "created_at": None,
                    "completed_at": None,
                    "scene_count": 0,
                    "error": True,
                })

        return stories

    def delete_story(self, story_id: str) -> dict:
        """Delete a story and all associated media files. Returns summary."""
        filepath = STORIES_DIR / f"{story_id}.json"
        images_deleted = 0
        videos_deleted = 0

        # Try to load story to find scene IDs
        if filepath.exists():
            try:
                data = json.loads(filepath.read_text(encoding="utf-8"))
                saved = SavedStory.model_validate(data)
                for scene_id in saved.scenes:
                    img = IMAGES_DIR / f"{scene_id}.png"
                    if img.exists():
                        img.unlink()
                        images_deleted += 1
                    vid = VIDEOS_DIR / f"{scene_id}.mp4"
                    if vid.exists():
                        vid.unlink()
                        videos_deleted += 1
            except Exception as e:
                logger.warning(f"Could not parse story for media cleanup: {e}")

            filepath.unlink()
            logger.info(f"Deleted story {story_id} ({images_deleted} images, {videos_deleted} videos)")
        else:
            logger.warning(f"Story file not found: {story_id}")

        return {
            "images_deleted": images_deleted,
            "videos_deleted": videos_deleted,
        }

    def _collect_valid_scene_ids(self) -> set[str]:
        """Collect all scene IDs from saved stories and in-progress saves."""
        scene_ids = set()

        # From saved stories
        if STORIES_DIR.exists():
            for filepath in STORIES_DIR.glob("*.json"):
                try:
                    data = json.loads(filepath.read_text(encoding="utf-8"))
                    saved = SavedStory.model_validate(data)
                    scene_ids.update(saved.scenes.keys())
                except Exception:
                    pass

        # From in-progress saves
        if PROGRESS_DIR.exists():
            for filepath in PROGRESS_DIR.glob("*.json"):
                try:
                    data = json.loads(filepath.read_text(encoding="utf-8"))
                    session = StorySession.model_validate(data)
                    scene_ids.update(session.scenes.keys())
                except Exception:
                    pass

        return scene_ids

    def _collect_active_upload_session_ids(self) -> set[str]:
        """Collect session IDs that have active uploads from in-progress saves."""
        active_ids = set()
        if not PROGRESS_DIR.exists():
            return active_ids
        for filepath in PROGRESS_DIR.glob("*.json"):
            try:
                data = json.loads(filepath.read_text(encoding="utf-8"))
                session = StorySession.model_validate(data)
                for photo_path in session.story.reference_photo_paths:
                    p = Path(photo_path)
                    if p.parent.parent == UPLOADS_DIR:
                        active_ids.add(p.parent.name)
                        break
            except Exception:
                pass
        return active_ids

    def get_orphaned_files(self) -> dict:
        """Find image/video files not referenced by any story or in-progress save.
        Also detects orphaned upload directories."""
        valid_ids = self._collect_valid_scene_ids()

        orphan_images = []
        orphan_videos = []
        orphan_uploads = []
        orphan_bytes = 0

        if IMAGES_DIR.exists():
            for f in IMAGES_DIR.glob("*.png"):
                if f.stem not in valid_ids:
                    size = f.stat().st_size
                    orphan_images.append({"path": str(f), "name": f.name, "size": size})
                    orphan_bytes += size

        if VIDEOS_DIR.exists():
            for f in VIDEOS_DIR.glob("*.mp4"):
                if f.stem not in valid_ids:
                    size = f.stat().st_size
                    orphan_videos.append({"path": str(f), "name": f.name, "size": size})
                    orphan_bytes += size

        # Check for orphaned upload directories
        if UPLOADS_DIR.exists():
            active_upload_ids = self._collect_active_upload_session_ids()
            for d in UPLOADS_DIR.iterdir():
                if d.is_dir() and d.name not in active_upload_ids:
                    dir_size = sum(f.stat().st_size for f in d.iterdir() if f.is_file())
                    orphan_uploads.append({"path": str(d), "name": d.name, "size": dir_size})
                    orphan_bytes += dir_size

        return {
            "images": orphan_images,
            "videos": orphan_videos,
            "uploads": orphan_uploads,
            "total_count": len(orphan_images) + len(orphan_videos) + len(orphan_uploads),
            "total_bytes": orphan_bytes,
            "total_display": _format_size(orphan_bytes),
        }

    def cleanup_orphans(self) -> dict:
        """Delete all orphaned files and upload directories. Returns summary."""
        orphans = self.get_orphaned_files()
        deleted = 0
        freed = 0

        for item in orphans["images"] + orphans["videos"]:
            path = Path(item["path"])
            if path.exists():
                freed += item["size"]
                path.unlink()
                deleted += 1

        for item in orphans.get("uploads", []):
            path = Path(item["path"])
            if path.exists():
                freed += item["size"]
                shutil.rmtree(path, ignore_errors=True)
                deleted += 1

        logger.info(f"Cleaned up {deleted} orphaned files/dirs ({_format_size(freed)})")
        return {
            "deleted": deleted,
            "freed_bytes": freed,
            "freed_display": _format_size(freed),
        }

    def list_in_progress(self) -> list[dict]:
        """List all in-progress story saves."""
        entries = []
        if not PROGRESS_DIR.exists():
            return entries

        for filepath in PROGRESS_DIR.glob("*.json"):
            tier_name = filepath.stem
            try:
                data = json.loads(filepath.read_text(encoding="utf-8"))
                session = StorySession.model_validate(data)
                entries.append({
                    "tier_name": tier_name,
                    "prompt": session.story.prompt[:80],
                    "scene_count": len(session.scenes),
                    "model": session.story.model,
                    "error": False,
                })
            except Exception as e:
                logger.warning(f"Corrupted progress file {filepath.name}: {e}")
                entries.append({
                    "tier_name": tier_name,
                    "prompt": "[Corrupted]",
                    "scene_count": 0,
                    "model": "",
                    "error": True,
                })

        return entries

    def delete_in_progress(self, tier_name: str) -> dict:
        """Delete an in-progress save and its associated media and uploads."""
        filepath = PROGRESS_DIR / f"{tier_name}.json"
        images_deleted = 0
        videos_deleted = 0
        uploads_cleaned = False

        if filepath.exists():
            try:
                data = json.loads(filepath.read_text(encoding="utf-8"))
                session = StorySession.model_validate(data)
                for scene_id in session.scenes:
                    img = IMAGES_DIR / f"{scene_id}.png"
                    if img.exists():
                        img.unlink()
                        images_deleted += 1
                    vid = VIDEOS_DIR / f"{scene_id}.mp4"
                    if vid.exists():
                        vid.unlink()
                        videos_deleted += 1

                # Clean up reference photo uploads if any
                for photo_path in session.story.reference_photo_paths:
                    p = Path(photo_path)
                    if p.parent.exists() and p.parent.parent == UPLOADS_DIR:
                        shutil.rmtree(p.parent, ignore_errors=True)
                        uploads_cleaned = True
                        break  # All photos are in the same session dir
            except Exception as e:
                logger.warning(f"Could not parse progress for media cleanup: {e}")

            filepath.unlink()
            logger.info(f"Deleted in-progress save for {tier_name}" +
                        (" (uploads cleaned)" if uploads_cleaned else ""))

        return {
            "images_deleted": images_deleted,
            "videos_deleted": videos_deleted,
        }
