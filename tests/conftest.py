"""Shared fixtures for integration tests.

Mocks all external AI services so tests run fast without API keys.
"""
import io
import os
import shutil
import socket
import subprocess
import sys
import time
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest
from PIL import Image as PILImage

# Set dummy API keys before any app imports
os.environ.setdefault("ANTHROPIC_API_KEY", "test-key")
os.environ.setdefault("OPENAI_API_KEY", "test-key")

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402
from app.session import _sessions  # noqa: E402


def _make_scene_response(
    title="Test Adventure",
    is_ending=False,
    num_choices=3,
):
    """Build a mock generate_scene return dict."""
    choices = [{"text": f"Choice {i+1}"} for i in range(num_choices)]
    if is_ending:
        choices = []
    return {
        "title": title,
        "content": "Once upon a time in a test land, something happened.",
        "image_prompt": "A whimsical test scene",
        "is_ending": is_ending,
        "choices": choices,
    }


class SceneGenerator:
    """Callable mock that tracks calls and returns scene dicts.

    Not async — AsyncMock wraps this and handles the coroutine layer.
    """

    def __init__(self, end_after=99):
        self.call_count = 0
        self.end_after = end_after
        self.calls = []

    def __call__(self, **kwargs):
        self.call_count += 1
        self.calls.append(kwargs)
        is_ending = self.call_count >= self.end_after
        return _make_scene_response(
            title=f"Chapter {self.call_count}",
            is_ending=is_ending,
        )


@pytest.fixture
def scene_generator():
    """A controllable scene generator mock."""
    return SceneGenerator(end_after=99)


@pytest.fixture
def mock_services(scene_generator):
    """Patch all external AI services with mocks."""
    mock_generate = AsyncMock(side_effect=scene_generator)
    mock_image = AsyncMock()
    mock_video = AsyncMock()
    mock_extra_images = AsyncMock()

    mock_tts = AsyncMock(return_value=b"fake-mp3-audio-data")

    with (
        patch("app.routes.story_service.generate_scene", mock_generate),
        patch("app.routes.image_service.generate_image", mock_image),
        patch("app.routes.image_service.generate_video", mock_video),
        patch("app.routes.image_service.generate_extra_images", mock_extra_images),
        patch("app.routes.generate_speech", mock_tts),
    ):
        yield scene_generator


@pytest.fixture
def client(mock_services):
    """TestClient with all external services mocked."""
    _sessions.clear()
    with TestClient(app, follow_redirects=False) as c:
        yield c
    _sessions.clear()


@pytest.fixture
def client_follow(mock_services):
    """TestClient that follows redirects (for full page assertions)."""
    _sessions.clear()
    with TestClient(app, follow_redirects=True) as c:
        yield c
    _sessions.clear()


def make_test_jpeg():
    """Create a minimal valid JPEG in memory."""
    img = PILImage.new("RGB", (10, 10), color="red")
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    buf.seek(0)
    return buf.read()


def make_test_png():
    """Create a minimal valid PNG in memory."""
    img = PILImage.new("RGB", (10, 10), color="blue")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf.read()


@pytest.fixture(autouse=True)
def cleanup_uploads():
    """Clean up any upload directories created during tests."""
    uploads_dir = Path("data/uploads")
    yield
    if uploads_dir.exists():
        for child in uploads_dir.iterdir():
            if child.is_dir():
                shutil.rmtree(child, ignore_errors=True)


def start_story(client, tier="kids", prompt="A test adventure", **extra_form):
    """Helper: start a story via multipart form post."""
    form_data = {
        "prompt": prompt,
        "length": "short",
        "model": "claude",
        "image_model": "gpt-image-1",
        **extra_form,
    }
    resp = client.post(f"/{tier}/story/start", data=form_data)
    return resp


def start_story_with_photo(client, tier="kids", prompt="A test adventure", **extra_form):
    """Helper: start a story with a photo upload."""
    photo_bytes = make_test_jpeg()
    form_data = {
        "prompt": prompt,
        "length": "short",
        "model": "claude",
        "image_model": "gpt-image-1",
        **extra_form,
    }
    files = {"reference_photos": ("test.jpg", io.BytesIO(photo_bytes), "image/jpeg")}
    resp = client.post(f"/{tier}/story/start", data=form_data, files=files)
    return resp


def _find_free_port():
    """Find a free TCP port on localhost."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture(scope="session")
def live_server():
    """Start a live uvicorn server for browser tests.

    Launches the real app on a random port and waits until it's ready.
    """
    port = _find_free_port()
    env = os.environ.copy()
    env.setdefault("ANTHROPIC_API_KEY", "test-key")
    env.setdefault("OPENAI_API_KEY", "test-key")

    proc = subprocess.Popen(
        [
            sys.executable, "-m", "uvicorn",
            "app.main:app",
            "--host", "127.0.0.1",
            "--port", str(port),
        ],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    # Wait for server to be ready (up to 10s)
    url = f"http://127.0.0.1:{port}"
    deadline = time.time() + 10
    while time.time() < deadline:
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=1):
                break
        except OSError:
            time.sleep(0.2)
    else:
        proc.kill()
        raise RuntimeError(f"Live server failed to start on port {port}")

    yield url

    proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()


def _find_chrome_binary():
    """Find a Chrome-compatible browser binary (Chrome or Brave)."""
    candidates = [
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
        # Linux paths
        "/usr/bin/google-chrome",
        "/usr/bin/chromium-browser",
        "/usr/bin/brave-browser",
    ]
    for path in candidates:
        if os.path.isfile(path):
            return path
    return None


@pytest.fixture(scope="session")
def browser():
    """Create a headless Chrome-compatible WebDriver for browser tests.

    Supports Chrome and Brave Browser.  Relies on Selenium 4.10+'s built-in
    driver manager (SeleniumManager) to auto-download the correct ChromeDriver.
    """
    from selenium import webdriver

    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1280,1024")

    chrome_bin = _find_chrome_binary()
    if chrome_bin:
        options.binary_location = chrome_bin

    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(5)

    yield driver

    driver.quit()


def extract_scene_id(redirect_url):
    """Extract scene_id from a redirect URL like /kids/story/scene/{id}."""
    parts = redirect_url.rstrip("/").split("/")
    return parts[-1]


def get_choice_ids(client, tier, scene_id):
    """Fetch a scene page and extract choice IDs from the form actions."""
    resp = client.get(f"/{tier}/story/scene/{scene_id}")
    assert resp.status_code == 200
    text = resp.text
    choice_ids = []
    marker = f"/{tier}/story/choose/{scene_id}/"
    idx = 0
    while True:
        pos = text.find(marker, idx)
        if pos == -1:
            break
        start = pos + len(marker)
        end = text.find('"', start)
        choice_id = text[start:end]
        if choice_id and choice_id not in choice_ids:
            choice_ids.append(choice_id)
        idx = end
    return choice_ids
