import json
import logging
import shutil
from datetime import datetime
from io import BytesIO
from pathlib import Path

from PIL import Image as PILImage

from app.models import CharacterOutfit, RosterCharacter

logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "characters"
MAX_CHARACTERS = 20
MAX_PHOTOS = 3
MAX_PHOTO_SIZE = 10 * 1024 * 1024  # 10 MB
ALLOWED_PHOTO_TYPES = {"image/jpeg": "jpg", "image/png": "png"}


class CharacterService:
    MAX_CHARACTERS = MAX_CHARACTERS

    def __init__(self):
        DATA_DIR.mkdir(parents=True, exist_ok=True)

    def _tier_dir(self, tier: str) -> Path:
        d = DATA_DIR / tier
        d.mkdir(parents=True, exist_ok=True)
        return d

    def _photo_dir(self, tier: str, character_id: str) -> Path:
        d = DATA_DIR / tier / character_id / "photos"
        d.mkdir(parents=True, exist_ok=True)
        return d

    def create_character(self, tier: str, name: str, description: str) -> RosterCharacter | None:
        """Create a new roster character. Returns None if limit reached or name conflict."""
        if len(self.list_characters(tier)) >= MAX_CHARACTERS:
            return None
        if self.name_exists(tier, name):
            return None

        character = RosterCharacter(
            name=name.strip(),
            description=description.strip(),
            tier=tier,
        )
        self._save_character(character)
        logger.info(f"Created character {character.character_id} '{name}' in tier {tier}")
        return character

    def get_character(self, tier: str, character_id: str) -> RosterCharacter | None:
        """Load a single character by ID."""
        filepath = self._tier_dir(tier) / f"{character_id}.json"
        if not filepath.exists():
            return None
        try:
            data = json.loads(filepath.read_text(encoding="utf-8"))
            return RosterCharacter.model_validate(data)
        except Exception as e:
            logger.warning(f"Failed to load character {character_id}: {e}")
            return None

    def list_characters(self, tier: str) -> list[RosterCharacter]:
        """Load all characters for a tier, sorted by name."""
        characters: list[RosterCharacter] = []
        tier_dir = self._tier_dir(tier)
        for filepath in tier_dir.glob("*.json"):
            try:
                data = json.loads(filepath.read_text(encoding="utf-8"))
                characters.append(RosterCharacter.model_validate(data))
            except Exception as e:
                logger.warning(f"Skipping corrupted character {filepath}: {e}")
        characters.sort(key=lambda c: c.name.lower())
        return characters

    def update_character(
        self, tier: str, character_id: str, name: str, description: str
    ) -> RosterCharacter | None:
        """Update a character's name and description."""
        character = self.get_character(tier, character_id)
        if not character:
            return None
        if self.name_exists(tier, name, exclude_id=character_id):
            return None
        character.name = name.strip()
        character.description = description.strip()
        character.updated_at = datetime.now()
        self._save_character(character)
        logger.info(f"Updated character {character_id}")
        return character

    def delete_character(self, tier: str, character_id: str) -> bool:
        """Delete a character and all its photos."""
        filepath = self._tier_dir(tier) / f"{character_id}.json"
        if not filepath.exists():
            return False
        try:
            filepath.unlink()
        except Exception as e:
            logger.error(f"Failed to delete character {character_id}: {e}")
            return False

        # Remove photos directory
        photo_dir = DATA_DIR / tier / character_id
        if photo_dir.exists():
            shutil.rmtree(photo_dir, ignore_errors=True)

        logger.info(f"Deleted character {character_id}")
        return True

    def name_exists(self, tier: str, name: str, exclude_id: str | None = None) -> bool:
        """Check if a character name already exists (case-insensitive)."""
        name_lower = name.strip().lower()
        for char in self.list_characters(tier):
            if char.name.lower() == name_lower:
                if exclude_id and char.character_id == exclude_id:
                    continue
                return True
        return False

    def save_character_photos(
        self, tier: str, character_id: str, files: list
    ) -> list[str]:
        """Save uploaded photos for a character. Returns list of relative paths."""
        character = self.get_character(tier, character_id)
        if not character:
            return []

        current_count = len(character.photo_paths)
        saved_paths: list[str] = []

        for i, file in enumerate(files):
            if current_count + len(saved_paths) >= MAX_PHOTOS:
                break
            if not file.filename:
                continue

            content_type = file.content_type or ""
            if content_type not in ALLOWED_PHOTO_TYPES:
                continue

            photo_bytes = file.file.read()
            if len(photo_bytes) > MAX_PHOTO_SIZE:
                continue

            ext = ALLOWED_PHOTO_TYPES[content_type]
            photo_dir = self._photo_dir(tier, character_id)
            index = current_count + len(saved_paths)
            filename = f"{index}_{character_id[:8]}.{ext}"
            filepath = photo_dir / filename
            filepath.write_bytes(photo_bytes)

            relative_path = f"characters/{tier}/{character_id}/photos/{filename}"
            saved_paths.append(relative_path)

        if saved_paths:
            character.photo_paths.extend(saved_paths)
            character.updated_at = datetime.now()
            self._save_character(character)

        return saved_paths

    def remove_character_photo(self, tier: str, character_id: str, filename: str) -> bool:
        """Remove a specific photo from a character."""
        character = self.get_character(tier, character_id)
        if not character:
            return False

        photo_path = DATA_DIR / tier / character_id / "photos" / filename
        if photo_path.exists():
            photo_path.unlink()

        # Remove from photo_paths list
        relative = f"characters/{tier}/{character_id}/photos/{filename}"
        character.photo_paths = [p for p in character.photo_paths if p != relative]
        character.updated_at = datetime.now()
        self._save_character(character)
        return True

    def get_character_photo_path(self, tier: str, character_id: str, filename: str) -> Path | None:
        """Return absolute path to a character photo file, or None."""
        photo_path = DATA_DIR / tier / character_id / "photos" / filename
        if photo_path.exists() and photo_path.is_file():
            return photo_path
        return None

    def get_absolute_photo_paths(self, character: RosterCharacter) -> list[str]:
        """Return list of absolute file paths for a character's photos."""
        paths = []
        for rel_path in character.photo_paths:
            abs_path = DATA_DIR.parent / rel_path
            if abs_path.exists():
                paths.append(str(abs_path))
        return paths

    def _save_character(self, character: RosterCharacter) -> None:
        """Write a character to disk."""
        filepath = self._tier_dir(character.tier) / f"{character.character_id}.json"
        try:
            filepath.write_text(
                character.model_dump_json(indent=2),
                encoding="utf-8",
            )
        except Exception as e:
            logger.error(f"Failed to save character {character.character_id}: {e}")

    # --- Outfit CRUD ---

    def _outfit_dir(self, tier: str, character_id: str) -> Path:
        d = DATA_DIR / tier / character_id / "outfits"
        d.mkdir(parents=True, exist_ok=True)
        return d

    def add_outfit(
        self, tier: str, character_id: str, name: str, description: str
    ) -> CharacterOutfit | None:
        """Add an outfit to a character. Returns None if character not found or duplicate name."""
        character = self.get_character(tier, character_id)
        if not character:
            return None
        name_lower = name.strip().lower()
        for o in character.outfits:
            if o.name.lower() == name_lower:
                return None
        outfit = CharacterOutfit(name=name.strip(), description=description.strip())
        character.outfits.append(outfit)
        character.updated_at = datetime.now()
        self._save_character(character)
        logger.info(f"Added outfit '{name}' to character {character_id}")
        return outfit

    def get_outfit(
        self, tier: str, character_id: str, outfit_id: str
    ) -> CharacterOutfit | None:
        """Look up a single outfit by ID."""
        character = self.get_character(tier, character_id)
        if not character:
            return None
        for o in character.outfits:
            if o.outfit_id == outfit_id:
                return o
        return None

    def update_outfit(
        self, tier: str, character_id: str, outfit_id: str, name: str, description: str
    ) -> CharacterOutfit | None:
        """Update an outfit's name and description."""
        character = self.get_character(tier, character_id)
        if not character:
            return None
        name_lower = name.strip().lower()
        target = None
        for o in character.outfits:
            if o.outfit_id == outfit_id:
                target = o
            elif o.name.lower() == name_lower:
                return None  # duplicate name
        if not target:
            return None
        target.name = name.strip()
        target.description = description.strip()
        character.updated_at = datetime.now()
        self._save_character(character)
        logger.info(f"Updated outfit {outfit_id} on character {character_id}")
        return target

    def delete_outfit(self, tier: str, character_id: str, outfit_id: str) -> bool:
        """Delete an outfit and its photo."""
        character = self.get_character(tier, character_id)
        if not character:
            return False
        outfit = None
        for o in character.outfits:
            if o.outfit_id == outfit_id:
                outfit = o
                break
        if not outfit:
            return False
        # Remove photo file if exists
        if outfit.photo_path:
            filename = outfit.photo_path.split("/")[-1]
            photo_path = DATA_DIR / tier / character_id / "outfits" / filename
            if photo_path.exists():
                photo_path.unlink()
        character.outfits = [o for o in character.outfits if o.outfit_id != outfit_id]
        character.updated_at = datetime.now()
        self._save_character(character)
        logger.info(f"Deleted outfit {outfit_id} from character {character_id}")
        return True

    def save_outfit_photo(
        self, tier: str, character_id: str, outfit_id: str, file
    ) -> str | None:
        """Save a single photo for an outfit (replaces existing). Returns relative path or None."""
        character = self.get_character(tier, character_id)
        if not character:
            return None
        outfit = None
        for o in character.outfits:
            if o.outfit_id == outfit_id:
                outfit = o
                break
        if not outfit:
            return None
        if not file.filename:
            return None
        content_type = file.content_type or ""
        if content_type not in ALLOWED_PHOTO_TYPES:
            return None
        photo_bytes = file.file.read()
        if len(photo_bytes) > MAX_PHOTO_SIZE:
            return None
        # Remove old photo if exists
        if outfit.photo_path:
            old_filename = outfit.photo_path.split("/")[-1]
            old_path = DATA_DIR / tier / character_id / "outfits" / old_filename
            if old_path.exists():
                old_path.unlink()
        ext = ALLOWED_PHOTO_TYPES[content_type]
        outfit_dir = self._outfit_dir(tier, character_id)
        filename = f"{outfit_id[:8]}.{ext}"
        filepath = outfit_dir / filename
        filepath.write_bytes(photo_bytes)
        relative_path = f"characters/{tier}/{character_id}/outfits/{filename}"
        outfit.photo_path = relative_path
        character.updated_at = datetime.now()
        self._save_character(character)
        return relative_path

    def remove_outfit_photo(self, tier: str, character_id: str, outfit_id: str) -> bool:
        """Remove the photo from an outfit."""
        character = self.get_character(tier, character_id)
        if not character:
            return False
        for o in character.outfits:
            if o.outfit_id == outfit_id and o.photo_path:
                filename = o.photo_path.split("/")[-1]
                photo_path = DATA_DIR / tier / character_id / "outfits" / filename
                if photo_path.exists():
                    photo_path.unlink()
                o.photo_path = None
                character.updated_at = datetime.now()
                self._save_character(character)
                return True
        return False

    def get_outfit_photo_path(
        self, tier: str, character_id: str, outfit_id: str, filename: str
    ) -> Path | None:
        """Return absolute path to an outfit photo file, or None."""
        photo_path = DATA_DIR / tier / character_id / "outfits" / filename
        if photo_path.exists() and photo_path.is_file():
            return photo_path
        return None
