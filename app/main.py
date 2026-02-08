import logging
import os
import re
from pathlib import Path

from fastapi import FastAPI, Request

# Configure root logger so all app.* loggers output to stdout
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(name)s - %(message)s")
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.config import settings
from app.tiers import TIERS, get_public_tiers
from app.models_registry import get_model_display_name, get_image_model_display_name

BASE_DIR = Path(__file__).resolve().parent.parent

app = FastAPI(title="Choose Your Own Adventure")

# Ensure runtime directories exist
os.makedirs(BASE_DIR / "static" / "images", exist_ok=True)
os.makedirs(BASE_DIR / "data" / "stories", exist_ok=True)
os.makedirs(BASE_DIR / "data" / "progress", exist_ok=True)
os.makedirs(BASE_DIR / "data" / "uploads", exist_ok=True)
os.makedirs(BASE_DIR / "static" / "images" / "anchors", exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

# Configure Jinja2 templates
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
templates.env.globals["get_model_display_name"] = get_model_display_name
templates.env.globals["get_image_model_display_name"] = get_image_model_display_name
templates.env.filters["regex_split"] = lambda value, pattern: re.split(pattern, value) if value else []

# Validate settings on startup
settings.validate()


# Serve service worker from root path for full scope
@app.get("/sw.js")
async def service_worker():
    return FileResponse(
        str(BASE_DIR / "static" / "sw.js"),
        media_type="application/javascript",
        headers={"Cache-Control": "no-cache"},
    )


# Serve manifest from root path for PWA detection
@app.get("/manifest.json")
async def manifest():
    return FileResponse(
        str(BASE_DIR / "static" / "manifest.json"),
        media_type="application/json",
    )


# Landing page — shows only public tiers
@app.get("/")
async def landing(request: Request):
    return templates.TemplateResponse(
        request, "landing.html", {"tiers": get_public_tiers()}
    )


# Import and mount tier routers after app is created to avoid circular imports
from app.routes import create_tier_router  # noqa: E402

for tier_config in TIERS.values():
    app.include_router(create_tier_router(tier_config))

# Mount admin router (tier-independent)
from app.admin_routes import router as admin_router  # noqa: E402

app.include_router(admin_router)
