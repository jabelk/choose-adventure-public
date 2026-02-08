import logging
from io import BytesIO

from openai import AsyncOpenAI

from app.config import settings

logger = logging.getLogger(__name__)

client = AsyncOpenAI(api_key=settings.openai_api_key)


async def transcribe_audio(audio_bytes: bytes, filename: str) -> str:
    """Transcribe audio bytes using OpenAI Whisper API.

    Args:
        audio_bytes: Raw audio data from the browser MediaRecorder.
        filename: Original filename with extension for format detection.

    Returns:
        Transcribed text string.
    """
    audio_file = BytesIO(audio_bytes)
    audio_file.name = filename

    response = await client.audio.transcriptions.create(
        model="whisper-1",
        file=audio_file,
        response_format="text",
        language="en",
    )
    return response.strip()
