import json
import logging
from pathlib import Path

from app.models import Family

logger = logging.getLogger(__name__)

FAMILY_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "family"


class FamilyService:
    def __init__(self):
        FAMILY_DIR.mkdir(parents=True, exist_ok=True)

    def _tier_dir(self, tier: str) -> Path:
        d = FAMILY_DIR / tier
        d.mkdir(parents=True, exist_ok=True)
        return d

    def _family_path(self, tier: str) -> Path:
        return self._tier_dir(tier) / "family.json"

    def get_family(self, tier: str) -> Family | None:
        """Load the family for a tier, or None if not set."""
        filepath = self._family_path(tier)
        if not filepath.exists():
            return None
        try:
            data = json.loads(filepath.read_text(encoding="utf-8"))
            return Family.model_validate(data)
        except Exception as e:
            logger.warning(f"Failed to load family for tier {tier}: {e}")
            return None

    def save_family(self, family: Family) -> Family:
        """Save/overwrite the family for a tier."""
        filepath = self._family_path(family.tier)
        filepath.write_text(
            family.model_dump_json(indent=2),
            encoding="utf-8",
        )
        logger.info(f"Saved family for tier {family.tier}")
        return family

    def delete_family(self, tier: str) -> bool:
        """Delete the family for a tier."""
        filepath = self._family_path(tier)
        if not filepath.exists():
            return False
        try:
            filepath.unlink()
            logger.info(f"Deleted family for tier {tier}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete family for tier {tier}: {e}")
            return False

    def build_family_context(self, family: Family) -> str:
        """Build prompt addition text from a family."""
        if not family.children and not family.parents:
            return ""

        lines = [
            "FAMILY MODE — The following family members should appear as characters in this story:"
        ]

        if family.children:
            lines.append("")
            lines.append("Children (main characters):")
            for child in family.children:
                lines.append(
                    f"- {child.name} ({child.gender}, age {child.age}) "
                    f"— feature as a main character"
                )

        if family.parents:
            lines.append("")
            lines.append(
                "Parents (supporting characters, include naturally when appropriate):"
            )
            for parent in family.parents:
                lines.append(f"- {parent.name}")

        return "\n".join(lines) + "\n"
