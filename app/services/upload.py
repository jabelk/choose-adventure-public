import logging
import shutil
from pathlib import Path

from fastapi import UploadFile

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent.parent
UPLOADS_DIR = BASE_DIR / "data" / "uploads"

MAX_FILES = 3
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
ALLOWED_TYPES = {"image/jpeg", "image/png"}


class UploadService:
    def __init__(self):
        UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

    async def save_upload_files(
        self, session_id: str, files: list[UploadFile]
    ) -> list[str]:
        """Save uploaded files to temp directory. Returns list of absolute paths.

        Validates file count, types, and sizes. Raises ValueError on failure.
        """
        if len(files) > MAX_FILES:
            raise ValueError(f"Maximum {MAX_FILES} photos allowed")

        session_dir = UPLOADS_DIR / session_id
        session_dir.mkdir(parents=True, exist_ok=True)

        saved_paths: list[str] = []

        for i, file in enumerate(files):
            if not file.filename:
                continue

            content_type = file.content_type or ""
            if content_type not in ALLOWED_TYPES:
                # Clean up already saved files
                shutil.rmtree(session_dir, ignore_errors=True)
                raise ValueError(
                    f"Invalid file type: {content_type}. Only JPEG and PNG are allowed."
                )

            data = await file.read()

            if len(data) > MAX_FILE_SIZE:
                shutil.rmtree(session_dir, ignore_errors=True)
                raise ValueError(
                    f"File '{file.filename}' is too large ({len(data) / (1024*1024):.1f} MB). "
                    f"Maximum is {MAX_FILE_SIZE / (1024*1024):.0f} MB."
                )

            # Sanitize filename: keep extension, prefix with index
            ext = Path(file.filename).suffix.lower()
            if ext not in (".jpg", ".jpeg", ".png"):
                ext = ".jpg" if "jpeg" in content_type else ".png"
            safe_name = f"{i}_{session_id[:8]}{ext}"
            filepath = session_dir / safe_name

            filepath.write_bytes(data)
            saved_paths.append(str(filepath.resolve()))
            logger.info(f"Saved upload: {filepath} ({len(data)} bytes)")

        return saved_paths

    def get_upload_paths(self, session_id: str) -> list[str]:
        """Get list of uploaded file paths for a session."""
        session_dir = UPLOADS_DIR / session_id
        if not session_dir.exists():
            return []
        return [str(f.resolve()) for f in sorted(session_dir.iterdir()) if f.is_file()]

    def cleanup_session(self, session_id: str) -> None:
        """Remove temporary upload directory for a session."""
        session_dir = UPLOADS_DIR / session_id
        if session_dir.exists():
            shutil.rmtree(session_dir, ignore_errors=True)
            logger.info(f"Cleaned up uploads for session {session_id}")
