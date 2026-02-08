"""Bible verse service — fetches scripture text from YouVersion Platform API.

Uses the NIrV (New International Reader's Version, translation ID 110) for
child-friendly verse text. Falls back gracefully if API is unreachable.
"""

import logging
import re

import httpx

from app.config import settings

logger = logging.getLogger(__name__)

# Known Bible book names for validation
BIBLE_BOOKS = [
    "Genesis", "Exodus", "Leviticus", "Numbers", "Deuteronomy",
    "Joshua", "Judges", "Ruth",
    "1 Samuel", "2 Samuel", "1 Kings", "2 Kings",
    "1 Chronicles", "2 Chronicles",
    "Ezra", "Nehemiah", "Esther",
    "Job", "Psalms", "Psalm", "Proverbs", "Ecclesiastes", "Song of Solomon",
    "Isaiah", "Jeremiah", "Lamentations", "Ezekiel", "Daniel",
    "Hosea", "Joel", "Amos", "Obadiah", "Jonah", "Micah",
    "Nahum", "Habakkuk", "Zephaniah", "Haggai", "Zechariah", "Malachi",
    "Matthew", "Mark", "Luke", "John",
    "Acts",
    "Romans", "1 Corinthians", "2 Corinthians",
    "Galatians", "Ephesians", "Philippians", "Colossians",
    "1 Thessalonians", "2 Thessalonians",
    "1 Timothy", "2 Timothy", "Titus", "Philemon",
    "Hebrews", "James", "1 Peter", "2 Peter",
    "1 John", "2 John", "3 John", "Jude", "Revelation",
]

# YouVersion API book abbreviations (OSIS format)
_BOOK_TO_OSIS = {
    "genesis": "GEN", "exodus": "EXO", "leviticus": "LEV", "numbers": "NUM",
    "deuteronomy": "DEU", "joshua": "JOS", "judges": "JDG", "ruth": "RUT",
    "1 samuel": "1SA", "2 samuel": "2SA", "1 kings": "1KI", "2 kings": "2KI",
    "1 chronicles": "1CH", "2 chronicles": "2CH", "ezra": "EZR", "nehemiah": "NEH",
    "esther": "EST", "job": "JOB", "psalms": "PSA", "psalm": "PSA",
    "proverbs": "PRO", "ecclesiastes": "ECC", "song of solomon": "SNG",
    "isaiah": "ISA", "jeremiah": "JER", "lamentations": "LAM", "ezekiel": "EZK",
    "daniel": "DAN", "hosea": "HOS", "joel": "JOL", "amos": "AMO",
    "obadiah": "OBA", "jonah": "JON", "micah": "MIC", "nahum": "NAM",
    "habakkuk": "HAB", "zephaniah": "ZEP", "haggai": "HAG", "zechariah": "ZEC",
    "malachi": "MAL", "matthew": "MAT", "mark": "MRK", "luke": "LUK",
    "john": "JHN", "acts": "ACT", "romans": "ROM", "1 corinthians": "1CO",
    "2 corinthians": "2CO", "galatians": "GAL", "ephesians": "EPH",
    "philippians": "PHP", "colossians": "COL", "1 thessalonians": "1TH",
    "2 thessalonians": "2TH", "1 timothy": "1TI", "2 timothy": "2TI",
    "titus": "TIT", "philemon": "PHM", "hebrews": "HEB", "james": "JAS",
    "1 peter": "1PE", "2 peter": "2PE", "1 john": "1JN", "2 john": "2JN",
    "3 john": "3JN", "jude": "JUD", "revelation": "REV",
}

# Lowercase set for fast lookup
_BOOKS_LOWER = {b.lower() for b in BIBLE_BOOKS}

# Regex: "Book Chapter" or "Book Chapter:Verse" or "Book Chapter:V1-V2" or "Book C1-C2"
_REF_PATTERN = re.compile(
    r"^((?:\d\s+)?[A-Za-z]+(?:\s+of\s+[A-Za-z]+)?)"  # book name
    r"(?:\s+(\d+))?$"                                    # optional chapter
    r"|"
    r"^((?:\d\s+)?[A-Za-z]+(?:\s+of\s+[A-Za-z]+)?)"  # book name
    r"\s+(\d+)"                                          # chapter
    r"(?::(\d+)(?:-(\d+))?)?"                            # optional verse or range
    r"(?:-(\d+))?$",                                     # optional chapter range end
    re.IGNORECASE,
)

YOUVERSION_BASE_URL = "https://developers.youversion.com/1.0"
NIRV_TRANSLATION_ID = "110"


class BibleService:
    """Fetches Bible verse text from the YouVersion Platform API."""

    def validate_reference(self, user_input: str) -> bool:
        """Check if input resembles a valid Bible reference.

        Returns True if the input starts with a recognized Bible book name.
        """
        text = user_input.strip()
        if not text:
            return False

        # Try matching against known book names
        text_lower = text.lower()
        for book in _BOOKS_LOWER:
            if text_lower == book or text_lower.startswith(book + " "):
                return True
        return False

    def parse_reference(self, user_input: str) -> tuple[str, str, str]:
        """Parse a user reference like 'Genesis 6:1-22' into components.

        Returns (osis_book, chapter, verse_range) where verse_range may be empty.
        Returns ('', '', '') if parsing fails.
        """
        text = user_input.strip()
        if not text:
            return ("", "", "")

        # Split into book part and chapter/verse part
        text_lower = text.lower()
        matched_book = ""
        remainder = ""
        for book in sorted(_BOOKS_LOWER, key=len, reverse=True):
            if text_lower == book:
                matched_book = book
                remainder = ""
                break
            if text_lower.startswith(book + " "):
                matched_book = book
                remainder = text[len(book):].strip()
                break

        if not matched_book:
            return ("", "", "")

        osis = _BOOK_TO_OSIS.get(matched_book, "")
        if not osis:
            return ("", "", "")

        if not remainder:
            return (osis, "", "")

        # Parse chapter and optional verse range
        ch_match = re.match(r"^(\d+)(?::(\d+(?:-\d+)?))?(?:-(\d+))?$", remainder)
        if not ch_match:
            return (osis, "", "")

        chapter = ch_match.group(1)
        verse_range = ch_match.group(2) or ""
        chapter_end = ch_match.group(3) or ""

        if chapter_end:
            # "Genesis 6-9" means chapters 6 through 9
            verse_range = ""  # chapter range, not verse range

        return (osis, chapter, verse_range)

    async def fetch_verses(self, scripture_reference: str) -> str:
        """Fetch NIrV verse text from YouVersion Platform API.

        Returns the verse text as a string, or empty string on failure.
        Falls back gracefully — the AI uses its training data when this returns empty.
        """
        if not settings.bible_api_key:
            return ""

        osis, chapter, verse_range = self.parse_reference(scripture_reference)
        if not osis:
            return ""

        # Build the passage reference for YouVersion API
        if chapter and verse_range:
            passage_ref = f"{osis}.{chapter}.{verse_range.replace('-', f'-{osis}.{chapter}.')}"
        elif chapter:
            passage_ref = f"{osis}.{chapter}"
        else:
            passage_ref = f"{osis}.1"

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{YOUVERSION_BASE_URL}/verses",
                    params={
                        "references": passage_ref,
                        "version_id": NIRV_TRANSLATION_ID,
                    },
                    headers={
                        "accept": "application/json",
                        "x-youversion-developer-token": settings.bible_api_key,
                    },
                )
                if response.status_code == 200:
                    data = response.json()
                    # Extract verse text from response
                    verses = data.get("data", {}).get("verses", [])
                    if verses:
                        text_parts = []
                        for verse in verses:
                            content = verse.get("content", "")
                            if content:
                                # Strip HTML tags if any
                                clean = re.sub(r"<[^>]+>", "", content).strip()
                                if clean:
                                    text_parts.append(clean)
                        return " ".join(text_parts)
                else:
                    logger.warning(
                        f"YouVersion API returned {response.status_code} for {passage_ref}"
                    )
        except Exception as e:
            logger.warning(f"Failed to fetch verses for {scripture_reference}: {e}")

        return ""
