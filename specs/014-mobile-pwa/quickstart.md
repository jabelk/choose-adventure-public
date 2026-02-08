# Quickstart: Mobile-Optimized PWA

## Prerequisites

- Chrome browser with `chrome://flags/#unsafely-treat-insecure-origin-as-secure` set to your LAN IP (e.g., `http://192.168.1.100:8080`)
- Server running: `venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8080`

## Validation Steps

### Step 1: Manifest Detection
1. Open `http://<LAN_IP>:8080/kids/` in Chrome
2. Open DevTools → Application → Manifest
3. Verify manifest is detected with name, icons, start_url, display mode
4. Expected: All manifest fields populated, no errors

### Step 2: Service Worker Registration
1. Open DevTools → Application → Service Workers
2. Verify a service worker is registered and active
3. Expected: Service worker status shows "activated and running"

### Step 3: Install Prompt
1. Look for the install banner/button on the page
2. Click "Install" or use Chrome menu → "Install app"
3. Expected: App installs and opens in standalone mode (no address bar)

### Step 4: Offline Static Assets
1. In DevTools → Network, check "Offline"
2. Refresh the page
3. Expected: App shell loads (CSS, JS, basic layout) from cache

### Step 5: Offline Gallery Reading
1. While online, browse to gallery and open 2-3 saved stories
2. Navigate through several scenes in each story
3. Check "Offline" in DevTools
4. Navigate back to gallery and open a previously browsed story
5. Expected: Story loads with text and images from cache

### Step 6: Offline Fallback
1. While offline, try to start a new story
2. Expected: Friendly offline message appears (not a browser error page)

### Step 7: Touch Targets (Mobile)
1. Open the app on a phone or use Chrome responsive mode (375px width)
2. Navigate through home → story → gallery
3. Expected: All buttons are easily tappable, no horizontal overflow, text readable

### Step 8: Swipe Navigation
1. Start a story and progress through 2-3 chapters
2. On the scene view, swipe right
3. Expected: Navigate to previous chapter
4. Swipe left
5. Expected: Navigate forward to the chapter you came from

### Step 9: Pull-to-Refresh
1. On the gallery page, pull down from the top
2. Expected: Page refreshes (Android) or manual refresh button works

### Step 10: Backward Compatibility
1. Open the app in a browser WITHOUT the Chrome flag (service worker won't register)
2. Browse stories, use all features
3. Expected: Everything works identically to before — PWA features are progressive enhancements
