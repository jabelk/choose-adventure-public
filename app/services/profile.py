import json
import logging
import shutil
from datetime import datetime
from io import BytesIO
from pathlib import Path

from PIL import Image as PILImage

from app.models import Profile, Character

logger = logging.getLogger(__name__)

PROFILES_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "profiles"
PHOTOS_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "photos"

ALLOWED_PHOTO_TYPES = {"image/jpeg": "jpg", "image/png": "png"}
MAX_PHOTO_SIZE = 5 * 1024 * 1024  # 5 MB
MIN_DIMENSION_WARNING = 256  # pixels


class ProfileService:
    def __init__(self):
        PROFILES_DIR.mkdir(parents=True, exist_ok=True)
        PHOTOS_DIR.mkdir(parents=True, exist_ok=True)

    def _tier_dir(self, tier: str) -> Path:
        d = PROFILES_DIR / tier
        d.mkdir(parents=True, exist_ok=True)
        return d

    def _photo_dir(self, tier: str, profile_id: str) -> Path:
        d = PHOTOS_DIR / tier / profile_id
        d.mkdir(parents=True, exist_ok=True)
        return d

    def create_profile(
        self,
        tier: str,
        name: str,
        themes: list[str] | None = None,
        art_style: str = "",
        tone: str = "",
        story_elements: list[str] | None = None,
    ) -> Profile:
        """Create a new profile and save to disk."""
        profile = Profile(
            name=name.strip(),
            tier=tier,
            themes=themes or [],
            art_style=art_style.strip(),
            tone=tone.strip(),
            story_elements=story_elements or [],
        )
        self._save_profile(profile)
        logger.info(f"Created profile {profile.profile_id} in tier {tier}")
        return profile

    def get_profile(self, tier: str, profile_id: str) -> Profile | None:
        """Load a single profile by ID."""
        filepath = self._tier_dir(tier) / f"{profile_id}.json"
        if not filepath.exists():
            return None
        try:
            data = json.loads(filepath.read_text(encoding="utf-8"))
            return Profile.model_validate(data)
        except Exception as e:
            logger.warning(f"Failed to load profile {profile_id}: {e}")
            return None

    def list_profiles(self, tier: str) -> list[Profile]:
        """Load all profiles for a tier, sorted by name."""
        profiles: list[Profile] = []
        tier_dir = self._tier_dir(tier)
        for filepath in tier_dir.glob("*.json"):
            try:
                data = json.loads(filepath.read_text(encoding="utf-8"))
                profiles.append(Profile.model_validate(data))
            except Exception as e:
                logger.warning(f"Skipping corrupted profile {filepath}: {e}")
        profiles.sort(key=lambda p: p.name.lower())
        return profiles

    def update_profile(
        self,
        tier: str,
        profile_id: str,
        name: str,
        themes: list[str] | None = None,
        art_style: str = "",
        tone: str = "",
        story_elements: list[str] | None = None,
    ) -> Profile | None:
        """Update an existing profile's preferences."""
        profile = self.get_profile(tier, profile_id)
        if not profile:
            return None
        profile.name = name.strip()
        profile.themes = themes or []
        profile.art_style = art_style.strip()
        profile.tone = tone.strip()
        profile.story_elements = story_elements or []
        profile.updated_at = datetime.now()
        self._save_profile(profile)
        logger.info(f"Updated profile {profile_id}")
        return profile

    def delete_profile(self, tier: str, profile_id: str) -> bool:
        """Delete a profile, its photos, and clean up cross-references."""
        filepath = self._tier_dir(tier) / f"{profile_id}.json"
        if not filepath.exists():
            return False
        try:
            filepath.unlink()
            logger.info(f"Deleted profile {profile_id}")
        except Exception as e:
            logger.error(f"Failed to delete profile {profile_id}: {e}")
            return False

        # Delete all photos for this profile
        photo_dir = PHOTOS_DIR / tier / profile_id
        if photo_dir.exists():
            shutil.rmtree(photo_dir, ignore_errors=True)
            logger.info(f"Deleted photo directory for profile {profile_id}")

        # Clean up references in other profiles in the same tier
        for other_profile in self.list_profiles(tier):
            changed = False
            for character in other_profile.characters:
                if character.linked_profile_id == profile_id:
                    character.linked_profile_id = None
                    changed = True
            if changed:
                other_profile.updated_at = datetime.now()
                self._save_profile(other_profile)
                logger.info(
                    f"Cleaned up references to deleted profile {profile_id} "
                    f"in profile {other_profile.profile_id}"
                )
        return True

    def add_character(
        self,
        tier: str,
        profile_id: str,
        name: str,
        description: str,
        linked_profile_id: str | None = None,
    ) -> Character | None:
        """Add a character to a profile."""
        profile = self.get_profile(tier, profile_id)
        if not profile:
            return None
        if len(profile.characters) >= 10:
            return None

        # Validate linked_profile_id is same tier
        if linked_profile_id:
            linked = self.get_profile(tier, linked_profile_id)
            if not linked:
                linked_profile_id = None

        character = Character(
            name=name.strip(),
            description=description.strip(),
            linked_profile_id=linked_profile_id,
        )
        profile.characters.append(character)
        profile.updated_at = datetime.now()
        self._save_profile(profile)
        logger.info(f"Added character {character.character_id} to profile {profile_id}")
        return character

    def update_character(
        self,
        tier: str,
        profile_id: str,
        character_id: str,
        name: str,
        description: str,
        linked_profile_id: str | None = None,
    ) -> bool:
        """Update a character's details."""
        profile = self.get_profile(tier, profile_id)
        if not profile:
            return False

        # Validate linked_profile_id is same tier
        if linked_profile_id:
            linked = self.get_profile(tier, linked_profile_id)
            if not linked:
                linked_profile_id = None

        for char in profile.characters:
            if char.character_id == character_id:
                char.name = name.strip()
                char.description = description.strip()
                char.linked_profile_id = linked_profile_id
                profile.updated_at = datetime.now()
                self._save_profile(profile)
                return True
        return False

    def delete_character(self, tier: str, profile_id: str, character_id: str) -> bool:
        """Remove a character from a profile and delete its photo."""
        profile = self.get_profile(tier, profile_id)
        if not profile:
            return False
        original_count = len(profile.characters)
        # Delete the character's photo file if it exists
        self.delete_character_photo(tier, profile_id, character_id)
        # Reload profile after photo deletion may have modified it
        profile = self.get_profile(tier, profile_id)
        if not profile:
            return False
        profile.characters = [
            c for c in profile.characters if c.character_id != character_id
        ]
        if len(profile.characters) < original_count:
            profile.updated_at = datetime.now()
            self._save_profile(profile)
            return True
        return False

    def save_character_photo(
        self,
        tier: str,
        profile_id: str,
        character_id: str,
        photo_bytes: bytes,
        content_type: str,
    ) -> tuple[bool, str | None]:
        """Save a reference photo for a character.

        Returns:
            (success, warning) — warning is set if image < 256x256.
        """
        # Validate content type
        if content_type not in ALLOWED_PHOTO_TYPES:
            return False, "Only JPEG and PNG files are supported."

        # Validate file size
        if len(photo_bytes) > MAX_PHOTO_SIZE:
            return False, f"Photo must be under {MAX_PHOTO_SIZE // (1024*1024)} MB."

        # Check dimensions for warning
        warning = None
        try:
            img = PILImage.open(BytesIO(photo_bytes))
            w, h = img.size
            if w < MIN_DIMENSION_WARNING or h < MIN_DIMENSION_WARNING:
                warning = (
                    f"Image is {w}x{h} pixels — smaller than {MIN_DIMENSION_WARNING}x"
                    f"{MIN_DIMENSION_WARNING}. AI results may be poor."
                )
        except Exception:
            pass  # Can't read dimensions — proceed anyway

        ext = ALLOWED_PHOTO_TYPES[content_type]
        photo_dir = self._photo_dir(tier, profile_id)

        # Delete any existing photo for this character (may have different extension)
        for old_file in photo_dir.glob(f"{character_id}.*"):
            old_file.unlink()

        # Save new photo
        filepath = photo_dir / f"{character_id}.{ext}"
        filepath.write_bytes(photo_bytes)

        # Update character's photo_path in the profile
        relative_path = f"photos/{tier}/{profile_id}/{character_id}.{ext}"
        profile = self.get_profile(tier, profile_id)
        if profile:
            for char in profile.characters:
                if char.character_id == character_id:
                    char.photo_path = relative_path
                    break
            profile.updated_at = datetime.now()
            self._save_profile(profile)

        logger.info(f"Saved photo for character {character_id} at {relative_path}")
        return True, warning

    def delete_character_photo(
        self, tier: str, profile_id: str, character_id: str
    ) -> None:
        """Delete a character's reference photo from disk and clear photo_path."""
        photo_dir = PHOTOS_DIR / tier / profile_id
        if photo_dir.exists():
            for photo_file in photo_dir.glob(f"{character_id}.*"):
                photo_file.unlink()
                logger.info(f"Deleted photo {photo_file}")

        # Clear photo_path in the profile
        profile = self.get_profile(tier, profile_id)
        if profile:
            for char in profile.characters:
                if char.character_id == character_id:
                    if char.photo_path:
                        char.photo_path = None
                        profile.updated_at = datetime.now()
                        self._save_profile(profile)
                    break

    def get_character_photo_path(
        self, tier: str, profile_id: str, character_id: str
    ) -> Path | None:
        """Return the absolute file path to a character's photo, or None."""
        photo_dir = PHOTOS_DIR / tier / profile_id
        if not photo_dir.exists():
            return None
        for photo_file in photo_dir.glob(f"{character_id}.*"):
            if photo_file.is_file() and photo_file.stat().st_size > 0:
                return photo_file
        return None

    def build_profile_context(
        self, profile: Profile, tier: str
    ) -> tuple[str, str, list[str]]:
        """Build prompt context from a profile's preferences and characters.

        Returns:
            A tuple of (content_guidelines_addition, image_style_addition,
            photo_paths) where photo_paths is a list of absolute file paths
            for characters that have reference photos.
        """
        guidelines_parts = []
        image_style = ""
        photo_paths: list[str] = []

        # Preferences
        if profile.themes:
            guidelines_parts.append(
                f"Preferred themes: {', '.join(profile.themes)}"
            )
        if profile.tone:
            guidelines_parts.append(f"Preferred tone: {profile.tone}")
        if profile.story_elements:
            guidelines_parts.append(
                f"Favorite story elements: {', '.join(profile.story_elements)}"
            )
        if profile.art_style:
            image_style = profile.art_style

        # Roster characters (new system — character_ids references)
        if profile.character_ids:
            from app.services.character import CharacterService
            char_svc = CharacterService()
            char_lines = []
            for rc_id in profile.character_ids:
                rc = char_svc.get_character(tier, rc_id)
                if rc:
                    char_lines.append(f"- {rc.name}: {rc.description}")
                    rc_photos = char_svc.get_absolute_photo_paths(rc)
                    for rp in rc_photos:
                        if len(photo_paths) < 3:
                            photo_paths.append(rp)
            if char_lines:
                guidelines_parts.append(
                    "The following characters should appear naturally in the story:\n"
                    + "\n".join(char_lines)
                )

        # Legacy inline characters (backward compat for unmigrated profiles)
        elif profile.characters:
            all_characters: list[tuple[Character, str]] = [
                (c, profile.profile_id) for c in profile.characters
            ]

            # Linked profile characters (one level deep)
            seen_profiles = {profile.profile_id}
            for char in profile.characters:
                if char.linked_profile_id and char.linked_profile_id not in seen_profiles:
                    seen_profiles.add(char.linked_profile_id)
                    linked_profile = self.get_profile(tier, char.linked_profile_id)
                    if linked_profile:
                        all_characters.extend(
                            (c, linked_profile.profile_id)
                            for c in linked_profile.characters
                        )

            char_lines = []
            for c, pid in all_characters:
                char_lines.append(f"- {c.name}: {c.description}")
                photo_file = self.get_character_photo_path(tier, pid, c.character_id)
                if photo_file:
                    photo_paths.append(str(photo_file))
            if char_lines:
                guidelines_parts.append(
                    "The following characters should appear naturally in the story:\n"
                    + "\n".join(char_lines)
                )

        if guidelines_parts:
            content_addition = (
                "USER PREFERENCES (incorporate these naturally into the story):\n"
                + "\n".join(guidelines_parts)
                + "\n"
            )
        else:
            content_addition = ""

        return content_addition, image_style, photo_paths

    def _save_profile(self, profile: Profile) -> None:
        """Write a profile to disk."""
        filepath = self._tier_dir(profile.tier) / f"{profile.profile_id}.json"
        try:
            filepath.write_text(
                profile.model_dump_json(indent=2),
                encoding="utf-8",
            )
        except Exception as e:
            logger.error(f"Failed to save profile {profile.profile_id}: {e}")
