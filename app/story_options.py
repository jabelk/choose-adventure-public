"""Story flavor options — tier-aware selectors that shape story generation.

Each option group defines choices per tier. The build_story_flavor_prompt()
function combines selections into a prompt addition for the AI.
"""
from dataclasses import dataclass, field


@dataclass
class OptionChoice:
    key: str
    display_name: str


@dataclass
class OptionGroup:
    name: str          # form field name
    label: str         # display label
    kids: list[OptionChoice] = field(default_factory=list)
    nsfw: list[OptionChoice] = field(default_factory=list)
    bible: list[OptionChoice] = field(default_factory=list)

    def choices_for_tier(self, tier: str) -> list[OptionChoice]:
        if tier == "kids":
            return self.kids
        if tier == "bible":
            return self.bible
        return self.nsfw


OPTION_GROUPS: list[OptionGroup] = [
    OptionGroup(
        name="protagonist_gender",
        label="Protagonist",
        kids=[
            OptionChoice("", "Any"),
            OptionChoice("boy", "Boy"),
            OptionChoice("girl", "Girl"),
        ],
    ),
    OptionGroup(
        name="protagonist_age",
        label="Age",
        kids=[
            OptionChoice("", "Any"),
            OptionChoice("toddler", "Toddler (3-4)"),
            OptionChoice("young-child", "Young Child (5-6)"),
            OptionChoice("older-child", "Older Child (7-9)"),
        ],
    ),
    OptionGroup(
        name="character_type",
        label="Character Type",
        kids=[
            OptionChoice("", "Any"),
            OptionChoice("human", "Human Kids"),
            OptionChoice("animal", "Animals"),
            OptionChoice("fantasy", "Fantasy Creatures"),
            OptionChoice("robot", "Robots"),
        ],
    ),
    OptionGroup(
        name="num_characters",
        label="Cast Size",
        kids=[
            OptionChoice("", "Any"),
            OptionChoice("solo", "Solo Hero"),
            OptionChoice("duo", "Best Friends (2)"),
            OptionChoice("group", "Friend Group (3+)"),
        ],
        bible=[
            OptionChoice("", "Any"),
            OptionChoice("solo", "Solo Hero"),
            OptionChoice("duo", "Best Friends (2)"),
            OptionChoice("group", "Friend Group (3+)"),
        ],
    ),
    OptionGroup(
        name="writing_style",
        label="Writing Style",
        kids=[
            OptionChoice("", "Default"),
            OptionChoice("narrator", "Storyteller Narrator"),
            OptionChoice("second-person", "You Are The Hero"),
            OptionChoice("simple", "Extra Simple Words"),
        ],
        bible=[
            OptionChoice("", "Default"),
            OptionChoice("narrator", "Storyteller Narrator"),
            OptionChoice("second-person", "You Are The Hero"),
            OptionChoice("simple", "Extra Simple Words"),
        ],
    ),
    OptionGroup(
        name="conflict_type",
        label="Story Type",
        kids=[
            OptionChoice("", "Any"),
            OptionChoice("adventure", "Adventure"),
            OptionChoice("mystery", "Mystery / Puzzle"),
            OptionChoice("friendship", "Friendship"),
            OptionChoice("rescue", "Rescue Mission"),
            OptionChoice("discovery", "Discovery / Exploration"),
        ],
    ),
]


# --- Prompt text mappings ---

_GENDER_PROMPT = {
    "boy": "boy",
    "girl": "girl",
}

_AGE_PROMPT = {
    "toddler": "3-4 year old",
    "young-child": "5-6 year old",
    "older-child": "7-9 year old",
}

_CHARACTER_TYPE_PROMPT = {
    "human": "human characters",
    "animal": "animal characters (talking animals with personalities)",
    "fantasy": "fantasy creatures (dragons, fairies, elves, magical beings)",
    "robot": "robots or mechanical characters",
}

_NUM_CHARACTERS_PROMPT = {
    "solo": "Focus on a single protagonist on their own journey.",
    "duo": "Feature two main characters (friends, partners, or rivals) working together.",
    "group": "Feature a small group of friends (3-4 characters) on the adventure together.",
}

_WRITING_STYLE_PROMPT = {
    "narrator": "Write in a warm storyteller narrator voice, as if reading aloud to a child at bedtime.",
    "second-person": 'Write in second person ("You walk into the cave...") to make the reader the hero.',
    "simple": "Use very simple vocabulary and very short sentences. Suitable for pre-readers being read to.",
}

_CONFLICT_TYPE_PROMPT = {
    "adventure": "The story centers on an exciting adventure with exploration and brave choices.",
    "mystery": "The story is a mystery — clues, puzzles, and figuring things out.",
    "friendship": "The story focuses on friendship, teamwork, and kindness.",
    "rescue": "The story is a rescue mission — someone or something needs saving.",
    "discovery": "The story is about discovering something new and wonderful.",
    "thriller": "The story is a tense thriller with suspense, danger, and high stakes.",
    "horror": "The story is horror — dread, atmosphere, and terrifying revelations.",
    "political": "The story involves political intrigue, power struggles, and shifting alliances.",
    "survival": "The story is about survival against harsh conditions or relentless threats.",
    "heist": "The story is a heist or caper — planning, execution, and unexpected complications.",
}


KINK_TOGGLES: dict[str, tuple[str, str, str]] = {}
def build_kink_prompt(kinks: list[str]) -> tuple[str, str]: return "", ""


# --- Structured character attribute definitions ---

CHARACTER_ATTRIBUTES: dict[str, dict] = {
    # Physical attributes
    "hair_color": {
        "label": "Hair Color",
        "options": ["Blonde", "Brunette", "Black", "Red", "Auburn", "Silver", "Pink", "Blue"],
        "tier_restrict": None,
        "group": "physical",
    },
    "hair_length": {
        "label": "Hair Length",
        "options": ["Short", "Medium", "Long", "Very Long"],
        "tier_restrict": None,
        "group": "physical",
    },
    "eye_color": {
        "label": "Eye Color",
        "options": ["Brown", "Blue", "Green", "Hazel", "Gray", "Amber"],
        "tier_restrict": None,
        "group": "physical",
    },
    "skin_tone": {
        "label": "Skin Tone",
        "options": ["Fair", "Light", "Medium", "Olive", "Tan", "Dark"],
        "tier_restrict": None,
        "group": "physical",
    },
    "height": {
        "label": "Height",
        "options": ["Short", "Average", "Tall", "Very Tall"],
        "tier_restrict": None,
        "group": "physical",
    },
    # Personality attributes
    "temperament": {
        "label": "Temperament",
        "options": ["Shy", "Bold", "Playful", "Dominant", "Gentle", "Fierce"],
        "tier_restrict": None,
        "group": "personality",
    },
    "energy": {
        "label": "Energy",
        "options": ["Calm", "Bubbly", "Intense", "Mysterious"],
        "tier_restrict": None,
        "group": "personality",
    },
    # Style attributes
    "clothing_style": {
        "label": "Clothing Style",
        "options": ["Casual", "Sporty", "Elegant", "Gothic", "Bohemian", "Streetwear"],
        "tier_restrict": None,
        "group": "style",
    },
    "aesthetic_vibe": {
        "label": "Aesthetic Vibe",
        "options": ["Natural", "Glamorous", "Edgy", "Vintage"],
        "tier_restrict": None,
        "group": "style",
    },
}


def get_attributes_for_tier(tier_name: str) -> dict[str, dict]:
    """Return CHARACTER_ATTRIBUTES filtered for the given tier.

    Removes categories where tier_restrict doesn't match (e.g., body_type
    is NSFW-only and won't appear on kids or bible tiers).
    """
    return {
        key: attr for key, attr in CHARACTER_ATTRIBUTES.items()
        if attr["tier_restrict"] is None or attr["tier_restrict"] == tier_name
    }


_PICTURE_BOOK_AGES = {"toddler", "young-child"}


def is_picture_book_age(protagonist_age: str) -> bool:
    """Return True if the protagonist age triggers picture book mode (3 images per scene)."""
    return protagonist_age in _PICTURE_BOOK_AGES


def get_option_groups() -> list[OptionGroup]:
    """Return all option groups."""
    return OPTION_GROUPS


def build_intensity_prompt(intensity: str) -> str: return ""


def build_story_flavor_prompt(
    protagonist_gender: str = "",
    protagonist_age: str = "",
    character_type: str = "",
    num_characters: str = "",
    writing_style: str = "",
    conflict_type: str = "",
) -> str:
    """Build a story setup prompt string from selected options.

    Returns empty string if no options are selected (uses AI defaults).
    """
    parts = []

    # Protagonist description
    protagonist_desc = []
    if protagonist_age and protagonist_age in _AGE_PROMPT:
        protagonist_desc.append(_AGE_PROMPT[protagonist_age])
    if protagonist_gender and protagonist_gender in _GENDER_PROMPT:
        protagonist_desc.append(_GENDER_PROMPT[protagonist_gender])
    if protagonist_desc:
        parts.append(f"The protagonist is a {' '.join(protagonist_desc)}.")

    if character_type and character_type in _CHARACTER_TYPE_PROMPT:
        parts.append(f"Use {_CHARACTER_TYPE_PROMPT[character_type]}.")

    if num_characters and num_characters in _NUM_CHARACTERS_PROMPT:
        parts.append(_NUM_CHARACTERS_PROMPT[num_characters])

    if writing_style and writing_style in _WRITING_STYLE_PROMPT:
        parts.append(_WRITING_STYLE_PROMPT[writing_style])

    if conflict_type and conflict_type in _CONFLICT_TYPE_PROMPT:
        parts.append(_CONFLICT_TYPE_PROMPT[conflict_type])

    if not parts:
        return ""

    return "STORY SETUP:\n" + "\n".join(parts)
