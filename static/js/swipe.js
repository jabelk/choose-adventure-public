/**
 * Swipe gesture navigation for scene view.
 *
 * Usage:
 *   initSwipeNav(element, { onSwipeLeft: fn, onSwipeRight: fn })
 */
function initSwipeNav(element, callbacks) {
    if (!element) return;

    const MIN_DISTANCE = 150;
    const MIN_VELOCITY = 0.3; // px/ms
    const IGNORED_SELECTORS = 'video, canvas, .tree-map-container';

    let startX = 0;
    let startY = 0;
    let startTime = 0;

    element.addEventListener('touchstart', function (e) {
        // Ignore touches on video, canvas, tree map
        if (e.target.closest(IGNORED_SELECTORS)) return;

        const touch = e.touches[0];
        startX = touch.clientX;
        startY = touch.clientY;
        startTime = Date.now();
    }, { passive: true });

    element.addEventListener('touchend', function (e) {
        if (!startTime) return;

        const touch = e.changedTouches[0];
        const deltaX = touch.clientX - startX;
        const deltaY = touch.clientY - startY;
        const elapsed = Date.now() - startTime;
        const velocity = Math.abs(deltaX) / elapsed;

        // Reset
        startTime = 0;

        // Must be primarily horizontal
        if (Math.abs(deltaX) <= Math.abs(deltaY)) return;

        // Must meet distance OR velocity threshold
        if (Math.abs(deltaX) < MIN_DISTANCE && velocity < MIN_VELOCITY) return;

        if (deltaX > 0 && callbacks.onSwipeRight) {
            callbacks.onSwipeRight();
        } else if (deltaX < 0 && callbacks.onSwipeLeft) {
            callbacks.onSwipeLeft();
        }
    }, { passive: true });
}
