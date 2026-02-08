/**
 * Bedtime wind-down timer.
 * Shows elapsed time since bedtime story started.
 * Gently pulses after 5 minutes to suggest winding down.
 */
function initBedtimeTimer() {
    var WIND_DOWN_SECONDS = 300; // 5 minutes
    var STORAGE_KEY = 'bedtime_start_time';
    var timerEl = document.getElementById('bedtime-timer');
    if (!timerEl) return;

    // Initialize start time if not already set
    var startTime = sessionStorage.getItem(STORAGE_KEY);
    if (!startTime) {
        startTime = Date.now().toString();
        sessionStorage.setItem(STORAGE_KEY, startTime);
    }
    startTime = parseInt(startTime, 10);

    function updateTimer() {
        var elapsed = Math.floor((Date.now() - startTime) / 1000);
        var minutes = Math.floor(elapsed / 60);
        var seconds = elapsed % 60;
        timerEl.textContent = String(minutes).padStart(2, '0') + ':' + String(seconds).padStart(2, '0');

        if (elapsed >= WIND_DOWN_SECONDS && !timerEl.classList.contains('wind-down')) {
            timerEl.classList.add('wind-down');
        }
    }

    updateTimer();
    setInterval(updateTimer, 1000);
}
