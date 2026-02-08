from dataclasses import dataclass

from app.config import settings


@dataclass
class ModelProvider:
    key: str
    display_name: str
    api_key_env: str


PROVIDERS = [
    ModelProvider(key="claude", display_name="Claude", api_key_env="ANTHROPIC_API_KEY"),
    ModelProvider(key="gpt", display_name="GPT-4o", api_key_env="OPENAI_API_KEY"),
    ModelProvider(key="gpt5", display_name="GPT-5.2", api_key_env="OPENAI_API_KEY"),
    ModelProvider(key="gemini", display_name="Gemini", api_key_env="GEMINI_API_KEY"),
    ModelProvider(key="grok", display_name="Grok", api_key_env="XAI_API_KEY"),
]

# Map env var names to settings attributes
_ENV_TO_ATTR = {
    "ANTHROPIC_API_KEY": "anthropic_api_key",
    "OPENAI_API_KEY": "openai_api_key",
    "GEMINI_API_KEY": "gemini_api_key",
    "XAI_API_KEY": "xai_api_key",
}


def get_available_models() -> list[ModelProvider]:
    """Return providers that have a configured API key."""
    available = []
    for provider in PROVIDERS:
        attr = _ENV_TO_ATTR.get(provider.api_key_env, "")
        if attr and getattr(settings, attr, ""):
            available.append(provider)
    return available


def get_provider(key: str) -> ModelProvider | None:
    """Look up a provider by key."""
    for provider in PROVIDERS:
        if provider.key == key:
            return provider
    return None


def get_model_display_name(key: str) -> str:
    """Return display name for a provider key, defaults to key.title()."""
    provider = get_provider(key)
    return provider.display_name if provider else key.title()


# --- Image Provider Registry ---


@dataclass
class ImageModel:
    key: str
    display_name: str
    provider: str
    api_key_env: str
    supports_input_fidelity: bool = False
    supports_references: bool = True


IMAGE_PROVIDERS = [
    ImageModel(key="gpt-image-1", display_name="GPT Image 1", provider="OpenAI", api_key_env="OPENAI_API_KEY", supports_input_fidelity=True),
    ImageModel(key="gpt-image-1-mini", display_name="GPT Image 1 Mini", provider="OpenAI", api_key_env="OPENAI_API_KEY"),
    ImageModel(key="gpt-image-1.5", display_name="GPT Image 1.5", provider="OpenAI", api_key_env="OPENAI_API_KEY", supports_input_fidelity=True),
    ImageModel(key="grok-imagine", display_name="Grok Imagine", provider="xAI", api_key_env="XAI_API_KEY"),
    ImageModel(key="gemini", display_name="Gemini", provider="Google", api_key_env="GEMINI_API_KEY"),
]

# Legacy alias for old saved stories
_LEGACY_IMAGE_NAMES = {
    "dalle": "DALL-E",
}


def get_available_image_models() -> list[ImageModel]:
    """Return image models that have a configured API key."""
    available = []
    for model in IMAGE_PROVIDERS:
        attr = _ENV_TO_ATTR.get(model.api_key_env, "")
        if attr and getattr(settings, attr, ""):
            available.append(model)
    return available


def get_image_provider(key: str) -> ImageModel | None:
    """Look up an image model by key."""
    for model in IMAGE_PROVIDERS:
        if model.key == key:
            return model
    return None


def get_image_model_display_name(key: str) -> str:
    """Return display name for an image model key, with legacy alias support."""
    model = get_image_provider(key)
    if model:
        return model.display_name
    if key in _LEGACY_IMAGE_NAMES:
        return _LEGACY_IMAGE_NAMES[key]
    return key.title()


# --- Art Style Registry ---


@dataclass
class ArtStyle:
    key: str
    display_name: str
    category: str
    prompt_addition: str
    tier: str = ""  # empty = all tiers, otherwise only shown for this tier


ART_STYLES = [
    # General
    ArtStyle("none", "Default", "General", ""),
    # Illustration styles
    ArtStyle("oil-painting", "Oil Painting", "Illustration",
             "rich oil painting style, textured brushstrokes, dramatic lighting, classical fine art aesthetic"),
    ArtStyle("watercolor", "Watercolor", "Illustration",
             "delicate watercolor painting style, soft washes of color, paper texture, flowing transparent layers"),
    ArtStyle("anime", "Anime", "Illustration",
             "anime illustration style, vibrant colors, expressive characters, detailed backgrounds, Japanese animation aesthetic"),
    ArtStyle("comic-book", "Comic Book", "Illustration",
             "bold comic book art style, strong ink outlines, dynamic composition, vivid colors, graphic novel aesthetic"),
    ArtStyle("pixel-art", "Pixel Art", "Illustration",
             "retro pixel art style, 16-bit aesthetic, crisp edges, limited color palette, nostalgic video game look"),
    # Photorealistic styles
    ArtStyle("photo-cinematic", "Cinematic", "Photorealistic",
             "photorealistic cinematic photography, movie-like composition, dramatic lighting, film grain, widescreen feel"),
    ArtStyle("photo-instagram", "Instagram", "Photorealistic",
             "photorealistic Instagram photography, perfect lighting, glamorous, curated aesthetic, high-end fashion look"),
    ArtStyle("photo-selfie", "Selfie", "Photorealistic",
             "photorealistic selfie style, natural casual phone photography, authentic candid moment"),
    ArtStyle("photo-casual", "Casual", "Photorealistic",
             "photorealistic casual lifestyle photography, candid moments, natural lighting, everyday settings"),
]


def get_art_styles(tier: str = "") -> list[ArtStyle]:
    """Return art styles available for a tier. If no tier specified, return all."""
    if not tier:
        return ART_STYLES
    return [s for s in ART_STYLES if not s.tier or s.tier == tier]


def get_art_style(key: str) -> ArtStyle | None:
    """Look up an art style by key."""
    for style in ART_STYLES:
        if style.key == key:
            return style
    return None


def get_art_style_prompt(key: str) -> str:
    """Return the prompt addition for an art style key, empty string if not found."""
    style = get_art_style(key)
    return style.prompt_addition if style else ""
