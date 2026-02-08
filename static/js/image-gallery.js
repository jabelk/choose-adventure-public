/**
 * Image Gallery — full-screen swipeable image viewer.
 * Usage: initImageGallery({ images: [url1, url2, ...], startIndex: 0 })
 */
function initImageGallery(config) {
    var images = config.images || [];
    if (images.length === 0) return;

    var currentIndex = config.startIndex || 0;
    var overlay = null;
    var imgEl = null;
    var counterEl = null;
    var prevBtn = null;
    var nextBtn = null;
    var touchStartX = 0;
    var touchStartY = 0;

    function open() {
        // Build overlay
        overlay = document.createElement('div');
        overlay.className = 'image-gallery-overlay';

        // Close button
        var closeBtn = document.createElement('button');
        closeBtn.className = 'gallery-close-btn';
        closeBtn.innerHTML = '&times;';
        closeBtn.setAttribute('aria-label', 'Close gallery');
        closeBtn.addEventListener('click', close);
        overlay.appendChild(closeBtn);

        // Loading placeholder
        var placeholder = document.createElement('div');
        placeholder.className = 'gallery-loading-placeholder';
        placeholder.textContent = 'Loading…';
        overlay.appendChild(placeholder);

        // Image
        imgEl = document.createElement('img');
        imgEl.className = 'gallery-image loading';
        imgEl.alt = 'Story image';
        imgEl.addEventListener('load', function () {
            imgEl.classList.remove('loading');
            placeholder.style.display = 'none';
        });
        overlay.appendChild(imgEl);

        // Prev button
        prevBtn = document.createElement('button');
        prevBtn.className = 'gallery-nav-btn prev';
        prevBtn.innerHTML = '&#8249;';
        prevBtn.setAttribute('aria-label', 'Previous image');
        prevBtn.addEventListener('click', prev);
        overlay.appendChild(prevBtn);

        // Next button
        nextBtn = document.createElement('button');
        nextBtn.className = 'gallery-nav-btn next';
        nextBtn.innerHTML = '&#8250;';
        nextBtn.setAttribute('aria-label', 'Next image');
        nextBtn.addEventListener('click', next);
        overlay.appendChild(nextBtn);

        // Counter
        counterEl = document.createElement('div');
        counterEl.className = 'gallery-counter';
        overlay.appendChild(counterEl);

        document.body.appendChild(overlay);

        // Keyboard
        document.addEventListener('keydown', onKeyDown);

        // Touch
        overlay.addEventListener('touchstart', onTouchStart, { passive: true });
        overlay.addEventListener('touchend', onTouchEnd);

        showImage();
    }

    function close() {
        if (overlay) {
            document.removeEventListener('keydown', onKeyDown);
            overlay.remove();
            overlay = null;
        }
    }

    function showImage() {
        if (!overlay) return;
        var placeholder = overlay.querySelector('.gallery-loading-placeholder');
        if (placeholder) {
            placeholder.style.display = '';
        }
        imgEl.classList.add('loading');
        imgEl.src = images[currentIndex];
        counterEl.textContent = (currentIndex + 1) + ' / ' + images.length;

        // Hide nav at boundaries
        prevBtn.disabled = currentIndex === 0;
        nextBtn.disabled = currentIndex === images.length - 1;

        // Hide arrows if single image
        if (images.length <= 1) {
            prevBtn.style.display = 'none';
            nextBtn.style.display = 'none';
        }
    }

    function prev() {
        if (currentIndex > 0) {
            currentIndex--;
            showImage();
        }
    }

    function next() {
        if (currentIndex < images.length - 1) {
            currentIndex++;
            showImage();
        }
    }

    function onKeyDown(e) {
        if (e.key === 'Escape') {
            close();
        } else if (e.key === 'ArrowLeft') {
            prev();
        } else if (e.key === 'ArrowRight') {
            next();
        }
    }

    function onTouchStart(e) {
        if (e.touches.length === 1) {
            touchStartX = e.touches[0].clientX;
            touchStartY = e.touches[0].clientY;
        }
    }

    function onTouchEnd(e) {
        if (e.changedTouches.length === 1) {
            var dx = e.changedTouches[0].clientX - touchStartX;
            var dy = e.changedTouches[0].clientY - touchStartY;
            // Only trigger swipe if horizontal movement > 50px and > vertical
            if (Math.abs(dx) > 50 && Math.abs(dx) > Math.abs(dy)) {
                if (dx > 0) {
                    prev();  // swipe right = previous
                } else {
                    next();  // swipe left = next
                }
            }
        }
    }

    // Expose open function
    return { open: open, close: close };
}
