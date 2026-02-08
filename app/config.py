import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Application settings loaded from environment variables."""

    def __init__(self):
        self.anthropic_api_key: str = os.getenv("ANTHROPIC_API_KEY", "")
        self.openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
        self.gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
        self.xai_api_key: str = os.getenv("XAI_API_KEY", "")
        self.bible_api_key: str = os.getenv("BIBLE_API_KEY", "")
        self.host: str = os.getenv("HOST", "0.0.0.0")
        self.port: int = int(os.getenv("PORT", "8000"))
        self.context_char_threshold: int = int(
            os.getenv("CONTEXT_CHAR_THRESHOLD", "50000")
        )

    def validate(self):
        """Validate API key configuration."""
        missing_required = []
        if not self.anthropic_api_key:
            missing_required.append("ANTHROPIC_API_KEY")
        if not self.openai_api_key:
            missing_required.append("OPENAI_API_KEY")
        if missing_required:
            print(
                f"WARNING: Missing required API keys: {', '.join(missing_required)}. "
                "Copy .env.example to .env and fill in your keys."
            )

        optional = []
        if not self.gemini_api_key:
            optional.append("GEMINI_API_KEY")
        if not self.xai_api_key:
            optional.append("XAI_API_KEY")
        if optional:
            print(
                f"INFO: Optional API keys not configured: {', '.join(optional)}. "
                "These models will not be available for story generation."
            )


settings = Settings()
