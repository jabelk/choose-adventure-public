from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path

from app.services.admin import AdminService

BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

router = APIRouter(prefix="/admin")
admin_service = AdminService()


@router.get("/")
async def admin_dashboard(request: Request, msg: str = ""):
    stats = admin_service.get_storage_stats()
    stories = admin_service.list_all_stories()
    orphans = admin_service.get_orphaned_files()
    in_progress = admin_service.list_in_progress()

    return templates.TemplateResponse(request, "admin.html", {
        "stats": stats,
        "stories": stories,
        "orphans": orphans,
        "in_progress": in_progress,
        "msg": msg,
    })


@router.post("/delete-story/{story_id}")
async def delete_story(story_id: str):
    result = admin_service.delete_story(story_id)
    msg = f"Story deleted. Removed {result['images_deleted']} image(s) and {result['videos_deleted']} video(s)."
    return RedirectResponse(url=f"/admin?msg={msg}", status_code=303)


@router.post("/cleanup-orphans")
async def cleanup_orphans():
    result = admin_service.cleanup_orphans()
    msg = f"Cleaned up {result['deleted']} orphaned file(s), freed {result['freed_display']}."
    return RedirectResponse(url=f"/admin?msg={msg}", status_code=303)


@router.post("/delete-progress/{tier_name}")
async def delete_progress(tier_name: str):
    result = admin_service.delete_in_progress(tier_name)
    msg = f"In-progress save for '{tier_name}' deleted. Removed {result['images_deleted']} image(s) and {result['videos_deleted']} video(s)."
    return RedirectResponse(url=f"/admin?msg={msg}", status_code=303)
