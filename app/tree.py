"""Tree building helper for D3.js visualization."""

from __future__ import annotations
from typing import Any


def build_tree(
    scenes: dict[str, Any],
    current_scene_id: str,
    path_history: list[str],
) -> dict:
    """Convert a flat scenes dict into a nested tree structure for D3.js.

    Args:
        scenes: Dict mapping scene_id to Scene (or SavedScene) objects.
        current_scene_id: The ID of the currently active scene.
        path_history: List of scene IDs from root to current position.

    Returns:
        Nested dict with id, label, is_ending, is_current, on_path,
        choice_text, children.
    """
    path_set = set(path_history)

    # Group scenes by parent
    children_map: dict[str | None, list[str]] = {}
    for scene_id, scene in scenes.items():
        parent = scene.parent_scene_id if hasattr(scene, "parent_scene_id") else getattr(scene, "parent_scene_id", None)
        children_map.setdefault(parent, []).append(scene_id)

    # Find root (parent_scene_id is None)
    roots = children_map.get(None, [])
    if not roots:
        return {}

    def _build_node(scene_id: str) -> dict:
        scene = scenes[scene_id]
        # Get the choice text that led to this scene
        choice_text = ""
        if scene.parent_scene_id and scene.choice_taken_id:
            parent = scenes.get(scene.parent_scene_id)
            if parent:
                for choice in parent.choices:
                    cid = choice.choice_id if hasattr(choice, "choice_id") else choice.choice_id
                    if cid == scene.choice_taken_id:
                        choice.text if hasattr(choice, "text") else ""
                        choice_text = choice.text
                        break

        node = {
            "id": scene_id,
            "label": f"Ch. {scene.depth + 1}",
            "is_ending": scene.is_ending,
            "is_current": scene_id == current_scene_id,
            "on_path": scene_id in path_set,
            "choice_text": choice_text,
            "children": [],
        }

        for child_id in children_map.get(scene_id, []):
            node["children"].append(_build_node(child_id))

        # Sort children by depth then by label for stable ordering
        node["children"].sort(key=lambda c: c["id"])

        return node

    return _build_node(roots[0])
