import logging
import re

from openai import AsyncOpenAI

from app.config import settings

logger = logging.getLogger(__name__)

client = AsyncOpenAI(api_key=settings.openai_api_key)

# Max characters per TTS request (gpt-4o-mini-tts has ~2000 token limit)
MAX_CHARS_PER_CHUNK = 4000


def _split_text_at_sentences(text: str, max_chars: int = MAX_CHARS_PER_CHUNK) -> list[str]:
    """Split text into chunks at sentence boundaries, each under max_chars."""
    if len(text) <= max_chars:
        return [text]

    # Split on sentence-ending punctuation followed by whitespace
    sentences = re.split(r'(?<=[.!?])\s+', text)
    chunks = []
    current_chunk = ""

    for sentence in sentences:
        if current_chunk and len(current_chunk) + len(sentence) + 1 > max_chars:
            chunks.append(current_chunk.strip())
            current_chunk = sentence
        else:
            current_chunk = current_chunk + " " + sentence if current_chunk else sentence

    if current_chunk.strip():
        chunks.append(current_chunk.strip())

    return chunks


async def generate_speech(text: str, voice: str = "nova", instructions: str = "") -> bytes:
    """Generate TTS audio from text using OpenAI gpt-4o-mini-tts.

    Args:
        text: The text to convert to speech.
        voice: Voice identifier (e.g., "nova", "onyx", "shimmer").
        instructions: Optional voice style instructions.

    Returns:
        MP3 audio bytes.
    """
    chunks = _split_text_at_sentences(text)
    audio_parts = []

    for chunk in chunks:
        kwargs = {
            "model": "gpt-4o-mini-tts",
            "voice": voice,
            "input": chunk,
            "response_format": "mp3",
        }
        if instructions:
            kwargs["instructions"] = instructions

        response = await client.audio.speech.create(**kwargs)
        audio_parts.append(response.content)

    # Concatenate MP3 chunks (MP3 is concatenation-safe)
    return b"".join(audio_parts)
