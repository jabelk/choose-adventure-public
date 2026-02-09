import uuid
from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class ImageStatus(str, Enum):
    PENDING = "pending"
    GENERATING = "generating"
    COMPLETE = "complete"
    FAILED = "failed"


class SenderType(str, Enum):
    USER = "user"
    CHARACTER = "character"
    NARRATOR = "narrator"


class SessionStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"


class Pacing(str, Enum):
    SLOW = "slow"
    NORMAL = "normal"
    FAST = "fast"


class Focus(str, Enum):
    DIALOGUE = "dialogue"
    DESCRIPTION = "description"
    ACTION = "action"
    BALANCED = "balanced"


class Tone(str, Enum):
    PLAYFUL = "playful"
    INTENSE = "intense"


SCENES_PER_CHAPTER = 5  # Number of scenes per chapter in epic stories


class StoryLength(str, Enum):
    SHORT = "short"
    MEDIUM = "medium"
    LONG = "long"
    EPIC = "epic"

    @property
    def target_depth(self) -> int:
        return {"short": 3, "medium": 5, "long": 7, "epic": 25}[self.value]

    @property
    def description(self) -> str:
        return {
            "short": "Quick 5-minute story (~3 chapters)",
            "medium": "Standard 10-15 minute story (~5 chapters)",
            "long": "Extended 20+ minute story (~7 chapters)",
            "epic": "Epic saga (~5 chapters, ~25 scenes)",
        }[self.value]


class Image(BaseModel):
    prompt: str
    status: ImageStatus = ImageStatus.PENDING
    url: Optional[str] = None
    error: Optional[str] = None
    video_url: Optional[str] = None
    video_status: str = "none"
    video_error: Optional[str] = None


class Choice(BaseModel):
    choice_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    text: str
    next_scene_id: Optional[str] = None


class Scene(BaseModel):
    scene_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    parent_scene_id: Optional[str] = None
    choice_taken_id: Optional[str] = None
    content: str
    image: Image
    extra_images: list[Image] = Field(default_factory=list)
    choices: list[Choice] = Field(default_factory=list)
    is_ending: bool = False
    depth: int = 0
    chapter_number: Optional[int] = None
    chapter_title: Optional[str] = None


class Character(BaseModel):
    """Legacy character model (embedded in profiles). Kept for migration compatibility."""
    character_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str = Field(..., max_length=100)
    description: str = Field(..., max_length=500)
    linked_profile_id: Optional[str] = None
    photo_path: Optional[str] = None


class CharacterOutfit(BaseModel):
    """A named clothing configuration belonging to a character."""
    outfit_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str = Field(..., max_length=100)
    description: str = Field(..., max_length=500)
    photo_path: Optional[str] = None


class RosterCharacter(BaseModel):
    """Standalone character entity for the reusable character roster."""
    character_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str = Field(..., max_length=100)
    description: str = Field(default="", max_length=500)
    tier: str
    photo_paths: list[str] = Field(default_factory=list)
    outfits: list[CharacterOutfit] = Field(default_factory=list)
    attributes: dict[str, str] = Field(default_factory=dict)
    relationship_stage: str = Field(default="strangers")
    story_count: int = Field(default=0)
    last_story_date: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class Profile(BaseModel):
    profile_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str = Field(..., max_length=100)
    tier: str
    themes: list[str] = Field(default_factory=list)
    art_style: str = ""
    tone: str = ""
    story_elements: list[str] = Field(default_factory=list)
    characters: list[Character] = Field(default_factory=list, max_length=10)
    character_ids: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class FamilyChild(BaseModel):
    name: str = Field(..., max_length=50)
    gender: str = Field(..., pattern=r"^(girl|boy|other)$")
    age: int = Field(..., ge=1, le=17)


class FamilyParent(BaseModel):
    name: str = Field(..., max_length=50)


class Family(BaseModel):
    tier: str
    children: list[FamilyChild] = Field(default_factory=list, max_length=6)
    parents: list[FamilyParent] = Field(default_factory=list, max_length=2)


class Story(BaseModel):
    story_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    prompt: str
    length: StoryLength
    target_depth: int
    tier: str = ""
    model: str = "claude"
    image_model: str = "dalle"
    video_mode: bool = False
    bedtime_mode: bool = False
    intensity: str = ""
    art_style: str = ""
    protagonist_gender: str = ""
    protagonist_age: str = ""
    character_type: str = ""
    num_characters: str = ""
    writing_style: str = ""
    conflict_type: str = ""
    kinks: list[str] = Field(default_factory=list)
    character_name: str = ""
    character_description: str = ""
    profile_id: Optional[str] = None
    roster_character_ids: list[str] = Field(default_factory=list)
    reference_photo_paths: list[str] = Field(default_factory=list)
    generated_reference_path: str = Field(default="")
    parent_story_id: Optional[str] = None
    sequel_context: str = ""
    created_at: datetime = Field(default_factory=datetime.now)
    current_scene_id: str = ""


class StorySession(BaseModel):
    story: Story
    scenes: dict[str, Scene] = Field(default_factory=dict)
    path_history: list[str] = Field(default_factory=list)
    error_message: Optional[str] = None
    recap_cache: dict[str, str] = Field(default_factory=dict)

    @property
    def current_scene(self) -> Optional[Scene]:
        if self.path_history:
            return self.scenes.get(self.path_history[-1])
        return None

    def add_scene(self, scene: Scene) -> None:
        self.scenes[scene.scene_id] = scene

    def navigate_forward(self, scene: Scene) -> None:
        self.add_scene(scene)
        self.path_history.append(scene.scene_id)
        self.story.current_scene_id = scene.scene_id

    def navigate_backward(self) -> Optional[Scene]:
        if len(self.path_history) > 1:
            self.path_history.pop()
            current_id = self.path_history[-1]
            self.story.current_scene_id = current_id
            return self.scenes.get(current_id)
        return None

    def navigate_to(self, scene_id: str) -> Optional[Scene]:
        """Navigate to any explored scene by rebuilding path_history from root."""
        if scene_id not in self.scenes:
            return None
        # Walk from scene_id up to root via parent_scene_id
        path = []
        current = scene_id
        while current:
            path.append(current)
            scene = self.scenes.get(current)
            if not scene:
                break
            current = scene.parent_scene_id
        path.reverse()
        self.path_history = path
        self.story.current_scene_id = scene_id
        return self.scenes.get(scene_id)

    def get_full_context(self) -> list[Scene]:
        return [
            self.scenes[sid]
            for sid in self.path_history
            if sid in self.scenes
        ]


# --- Saved/Archived Story Models ---


class SavedChoice(BaseModel):
    choice_id: str
    text: str
    next_scene_id: Optional[str] = None


class SavedScene(BaseModel):
    scene_id: str
    parent_scene_id: Optional[str] = None
    choice_taken_id: Optional[str] = None
    content: str
    image_url: Optional[str] = None
    image_prompt: str = ""
    video_url: Optional[str] = None
    extra_image_urls: list[str] = Field(default_factory=list)
    extra_image_prompts: list[str] = Field(default_factory=list)
    choices: list[SavedChoice] = Field(default_factory=list)
    is_ending: bool = False
    depth: int = 0
    chapter_number: Optional[int] = None
    chapter_title: Optional[str] = None


class SavedStory(BaseModel):
    story_id: str
    title: str
    prompt: str
    tier: str
    length: str
    target_depth: int
    model: str = "claude"
    image_model: str = "dalle"
    video_mode: bool = False
    bedtime_mode: bool = False
    intensity: str = ""
    art_style: str = ""
    protagonist_gender: str = ""
    protagonist_age: str = ""
    character_type: str = ""
    num_characters: str = ""
    writing_style: str = ""
    conflict_type: str = ""
    kinks: list[str] = Field(default_factory=list)
    character_name: str = ""
    character_description: str = ""
    roster_character_ids: list[str] = Field(default_factory=list)
    parent_story_id: Optional[str] = None
    sequel_story_ids: list[str] = Field(default_factory=list)
    created_at: datetime
    completed_at: datetime = Field(default_factory=datetime.now)
    cover_art_url: Optional[str] = None
    cover_art_status: str = "none"
    scenes: dict[str, SavedScene] = Field(default_factory=dict)
    path_history: list[str] = Field(default_factory=list)


# --- Agent Mode (Chat Roleplay) Models ---


