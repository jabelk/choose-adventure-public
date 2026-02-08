"""Export service for generating self-contained HTML and PDF story files."""

import base64
import logging
from pathlib import Path

from fpdf import FPDF
from jinja2 import Environment, FileSystemLoader

from app.models import SavedStory

logger = logging.getLogger(__name__)

STATIC_IMAGES_DIR = Path(__file__).resolve().parent.parent.parent / "static" / "images"

PLACEHOLDER_SVG = """<svg xmlns="http://www.w3.org/2000/svg" width="400" height="400" viewBox="0 0 400 400">
  <rect width="400" height="400" fill="#2a2a4a"/>
  <text x="200" y="200" text-anchor="middle" dominant-baseline="middle"
        font-family="Georgia, serif" font-size="18" fill="#606080">
    Image unavailable
  </text>
</svg>"""


def _get_placeholder_data_uri() -> str:
    """Return a base64 data URI for the placeholder SVG."""
    encoded = base64.b64encode(PLACEHOLDER_SVG.encode("utf-8")).decode("ascii")
    return f"data:image/svg+xml;base64,{encoded}"


def _read_image_as_base64(image_url: str | None) -> str:
    """Resolve an image URL to a base64 data URI.

    Reads the PNG file from static/images/ and returns a data URI.
    Returns placeholder SVG if the file is missing or unreadable.
    """
    if not image_url:
        return _get_placeholder_data_uri()

    # Strip /static/ prefix to get relative path
    relative = image_url.lstrip("/")
    if relative.startswith("static/"):
        relative = relative[len("static/"):]

    filepath = STATIC_IMAGES_DIR.parent / relative
    if not filepath.exists() or filepath.stat().st_size == 0:
        return _get_placeholder_data_uri()

    try:
        img_bytes = filepath.read_bytes()
        encoded = base64.b64encode(img_bytes).decode("ascii")
        return f"data:image/png;base64,{encoded}"
    except Exception as e:
        logger.warning(f"Failed to read image {filepath}: {e}")
        return _get_placeholder_data_uri()


def _order_scenes_by_branch(saved_story: SavedStory) -> list[tuple[str, str]]:
    """Order scenes: main path first, then alternate branches depth-first.

    Returns list of (scene_id, branch_label) tuples.
    branch_label is empty string for main path scenes.
    """
    scenes = saved_story.scenes
    path_history = saved_story.path_history

    if not scenes:
        return []

    # Build children map
    children_map: dict[str | None, list[str]] = {}
    for sid, scene in scenes.items():
        children_map.setdefault(scene.parent_scene_id, []).append(sid)

    # Find root
    root_id = None
    for sid, scene in scenes.items():
        if scene.parent_scene_id is None:
            root_id = sid
            break
    if not root_id:
        root_id = path_history[0] if path_history else next(iter(scenes))

    main_path_set = set(path_history)
    result: list[tuple[str, str]] = []

    def _collect_branch(scene_id: str, branch_label: str) -> None:
        """Depth-first collection of a branch."""
        result.append((scene_id, branch_label))
        for child_id in children_map.get(scene_id, []):
            if child_id not in main_path_set:
                # Find which choice led to this child
                scene = scenes[scene_id]
                choice_text = ""
                for c in scene.choices:
                    if c.next_scene_id == child_id:
                        choice_text = c.text
                        break
                child_label = f"Branch from Ch. {scene.depth + 1}: \"{choice_text}\""
                _collect_branch(child_id, child_label)

    # 1) Main path in order
    for sid in path_history:
        if sid in scenes:
            result.append((sid, ""))

    # 2) Alternate branches: walk main path, collect non-main children
    for sid in path_history:
        if sid not in scenes:
            continue
        for child_id in children_map.get(sid, []):
            if child_id not in main_path_set:
                scene = scenes[sid]
                choice_text = ""
                for c in scene.choices:
                    if c.next_scene_id == child_id:
                        choice_text = c.text
                        break
                label = f"Branch from Ch. {scene.depth + 1}: \"{choice_text}\""
                _collect_branch(child_id, label)

    # 3) Any orphan scenes not yet collected (safety net)
    collected_ids = {sid for sid, _ in result}
    for sid in scenes:
        if sid not in collected_ids:
            result.append((sid, "Other"))

    return result


def _build_scene_data(saved_story: SavedStory) -> list[dict]:
    """Build ordered list of scene data dicts with base64 images.

    Each dict has: scene_id, scene, image_data_uri, branch_label, chapter_num.
    """
    ordered = _order_scenes_by_branch(saved_story)
    scene_data = []
    chapter_num = 0

    for scene_id, branch_label in ordered:
        scene = saved_story.scenes[scene_id]
        chapter_num += 1
        scene_data.append({
            "scene_id": scene_id,
            "scene": scene,
            "image_data_uri": _read_image_as_base64(scene.image_url),
            "branch_label": branch_label,
            "chapter_num": chapter_num,
        })

    return scene_data


TEMPLATES_DIR = Path(__file__).resolve().parent.parent.parent / "templates"

_jinja_env = Environment(
    loader=FileSystemLoader(str(TEMPLATES_DIR)),
    autoescape=False,
)


def export_html(saved_story: SavedStory) -> str:
    """Export a saved story as a self-contained HTML string.

    Builds scene data with base64 images and renders the export.html template.
    """
    scenes_data = _build_scene_data(saved_story)
    template = _jinja_env.get_template("export.html")
    return template.render(
        story=saved_story,
        scenes_data=scenes_data,
    )


def _resolve_image_path(image_url: str | None) -> Path | None:
    """Resolve an image URL to a filesystem path, or None if missing."""
    if not image_url:
        return None

    relative = image_url.lstrip("/")
    if relative.startswith("static/"):
        relative = relative[len("static/"):]

    filepath = STATIC_IMAGES_DIR.parent / relative
    if filepath.exists() and filepath.stat().st_size > 0:
        return filepath
    return None


def export_pdf(saved_story: SavedStory) -> bytes:
    """Export a saved story as a PDF document.

    Uses fpdf2 to build a PDF with title page, branch overview,
    and scenes with embedded images.
    """
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=20)

    # Title page
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 28)
    pdf.ln(40)
    pdf.cell(0, 15, saved_story.title, new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.ln(10)
    pdf.set_font("Helvetica", "I", 14)
    pdf.cell(
        0, 10,
        f'"{saved_story.prompt}"',
        new_x="LMARGIN", new_y="NEXT", align="C",
    )
    pdf.ln(5)
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(
        0, 8,
        saved_story.completed_at.strftime("%B %d, %Y"),
        new_x="LMARGIN", new_y="NEXT", align="C",
    )

    # Branch overview
    ordered = _order_scenes_by_branch(saved_story)
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 18)
    pdf.cell(0, 12, "Story Overview", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)
    pdf.set_font("Helvetica", "", 11)

    current_branch = ""
    chapter_num = 0
    for scene_id, branch_label in ordered:
        scene = saved_story.scenes[scene_id]
        chapter_num += 1

        if branch_label != current_branch:
            if branch_label:
                pdf.ln(3)
                pdf.set_font("Helvetica", "B", 10)
                pdf.cell(0, 7, branch_label, new_x="LMARGIN", new_y="NEXT")
                pdf.set_font("Helvetica", "", 11)
            current_branch = branch_label

        label = f"  Chapter {chapter_num}"
        if scene.is_ending:
            label += " (Ending)"
        # Truncate content for overview
        preview = scene.content[:80].replace("\n", " ")
        if len(scene.content) > 80:
            preview += "..."
        pdf.cell(0, 7, f"{label}: {preview}", new_x="LMARGIN", new_y="NEXT")

    # Scene pages
    chapter_num = 0
    for scene_id, branch_label in ordered:
        scene = saved_story.scenes[scene_id]
        chapter_num += 1

        pdf.add_page()

        # Chapter heading
        pdf.set_font("Helvetica", "B", 20)
        pdf.cell(0, 12, f"Chapter {chapter_num}", new_x="LMARGIN", new_y="NEXT")

        if branch_label:
            pdf.set_font("Helvetica", "I", 10)
            pdf.set_text_color(128, 128, 128)
            pdf.cell(0, 7, branch_label, new_x="LMARGIN", new_y="NEXT")
            pdf.set_text_color(0, 0, 0)

        pdf.ln(5)

        # Image
        img_path = _resolve_image_path(scene.image_url)
        if img_path:
            try:
                # Scale image to fit page width (max ~170mm)
                pdf.image(str(img_path), w=170)
                pdf.ln(5)
            except Exception as e:
                logger.warning(f"Failed to embed image in PDF: {e}")
                pdf.set_font("Helvetica", "I", 10)
                pdf.cell(0, 8, "[Image unavailable]", new_x="LMARGIN", new_y="NEXT")
        else:
            pdf.set_font("Helvetica", "I", 10)
            pdf.set_text_color(128, 128, 128)
            pdf.cell(0, 8, "[Image unavailable]", new_x="LMARGIN", new_y="NEXT")
            pdf.set_text_color(0, 0, 0)

        pdf.ln(3)

        # Scene text
        pdf.set_font("Helvetica", "", 12)
        pdf.multi_cell(0, 7, scene.content)

        if scene.is_ending:
            pdf.ln(10)
            pdf.set_font("Helvetica", "B", 16)
            pdf.cell(0, 10, "The End", new_x="LMARGIN", new_y="NEXT", align="C")

        # Choices
        if scene.choices:
            pdf.ln(5)
            pdf.set_font("Helvetica", "I", 10)
            pdf.cell(0, 7, "Choices:", new_x="LMARGIN", new_y="NEXT")
            pdf.set_font("Helvetica", "", 10)
            for choice in scene.choices:
                explored = " (explored)" if choice.next_scene_id else ""
                pdf.cell(
                    0, 6,
                    f"  -> {choice.text}{explored}",
                    new_x="LMARGIN", new_y="NEXT",
                )

    return pdf.output()


def export_coloring_pdf(coloring_image_path: Path) -> bytes:
    """Export a coloring page image as a single-page print-ready PDF.

    Creates a US Letter sized PDF with the image centered and scaled to
    fit the page width with margins. Returns PDF bytes.
    """
    pdf = FPDF(orientation="P", unit="mm", format="Letter")
    pdf.set_auto_page_break(auto=False)
    pdf.add_page()

    # US Letter: 215.9mm x 279.4mm, 20mm margins → 175.9mm usable width
    page_w = 215.9
    page_h = 279.4
    margin = 20
    usable_w = page_w - 2 * margin
    usable_h = page_h - 2 * margin

    try:
        pdf.image(str(coloring_image_path), x=margin, y=margin, w=usable_w)
    except Exception as e:
        logger.warning(f"Failed to embed coloring page image in PDF: {e}")
        pdf.set_font("Helvetica", "I", 14)
        pdf.text(page_w / 2 - 20, page_h / 2, "[Image unavailable]")

    return pdf.output()
