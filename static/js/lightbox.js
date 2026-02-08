/* Lightbox — tap images to view full-screen with pinch-to-zoom and swipe-to-dismiss */
(function() {
    var lightbox = document.getElementById('lightbox');
    var lightboxImg = document.getElementById('lightbox-img');
    if (!lightbox || !lightboxImg) return;

    // State
    var scale = 1;
    var translateX = 0;
    var translateY = 0;
    var startDist = 0;
    var startScale = 1;
    var panStartX = 0;
    var panStartY = 0;
    var panStartTx = 0;
    var panStartTy = 0;
    var isDragging = false;
    var swipeStartY = 0;
    var swipeStartTime = 0;

    function openLightbox(src) {
        lightboxImg.src = src;
        scale = 1;
        translateX = 0;
        translateY = 0;
        applyTransform();
        lightbox.classList.add('active');
        document.body.style.overflow = 'hidden';
    }

    function closeLightbox() {
        lightbox.classList.remove('active');
        document.body.style.overflow = '';
        lightboxImg.src = '';
    }

    function applyTransform() {
        lightboxImg.style.transform = 'translate(' + translateX + 'px, ' + translateY + 'px) scale(' + scale + ')';
    }

    // Open on tap — event delegation for dynamic images
    document.addEventListener('click', function(e) {
        var img = e.target.closest('.chat-photo, .scene-image-container img, .gallery-image img, .extra-image img');
        if (img && img.src) {
            e.preventDefault();
            e.stopPropagation();
            openLightbox(img.src);
        }
    });

    // Close button
    lightbox.querySelector('.lightbox-close').addEventListener('click', function(e) {
        e.stopPropagation();
        closeLightbox();
    });

    // Close on backdrop tap (but not on the image)
    lightbox.addEventListener('click', function(e) {
        if (e.target === lightbox) {
            closeLightbox();
        }
    });

    // Escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && lightbox.classList.contains('active')) {
            closeLightbox();
        }
    });

    // --- Touch handling: pinch-to-zoom + swipe-to-dismiss ---
    lightboxImg.addEventListener('touchstart', function(e) {
        if (e.touches.length === 2) {
            // Pinch start
            e.preventDefault();
            startDist = getTouchDist(e.touches);
            startScale = scale;
        } else if (e.touches.length === 1) {
            // Pan/swipe start
            panStartX = e.touches[0].clientX;
            panStartY = e.touches[0].clientY;
            panStartTx = translateX;
            panStartTy = translateY;
            swipeStartY = e.touches[0].clientY;
            swipeStartTime = Date.now();
            isDragging = true;
        }
    }, { passive: false });

    lightboxImg.addEventListener('touchmove', function(e) {
        if (e.touches.length === 2) {
            // Pinch zoom
            e.preventDefault();
            var dist = getTouchDist(e.touches);
            scale = Math.max(0.5, Math.min(5, startScale * (dist / startDist)));
            applyTransform();
        } else if (e.touches.length === 1 && isDragging) {
            e.preventDefault();
            var dx = e.touches[0].clientX - panStartX;
            var dy = e.touches[0].clientY - panStartY;
            if (scale > 1.05) {
                // When zoomed in, pan the image
                translateX = panStartTx + dx;
                translateY = panStartTy + dy;
            } else {
                // When at normal scale, track vertical drag for dismiss
                translateY = dy;
                // Fade out as user drags down
                var opacity = Math.max(0.2, 1 - Math.abs(dy) / 400);
                lightbox.style.background = 'rgba(0,0,0,' + opacity + ')';
            }
            applyTransform();
        }
    }, { passive: false });

    lightboxImg.addEventListener('touchend', function(e) {
        if (e.touches.length === 0 && isDragging) {
            isDragging = false;
            var dy = translateY;
            var elapsed = Date.now() - swipeStartTime;

            if (scale <= 1.05) {
                // Check for swipe-to-dismiss: fast swipe or dragged far enough
                if ((Math.abs(dy) > 100) || (Math.abs(dy) > 50 && elapsed < 300)) {
                    closeLightbox();
                    lightbox.style.background = '';
                    return;
                }
                // Snap back
                translateY = 0;
                lightbox.style.background = '';
                applyTransform();
            }
        }
    });

    // Double-tap to toggle zoom
    var lastTap = 0;
    lightboxImg.addEventListener('touchend', function(e) {
        if (e.touches.length > 0) return;
        var now = Date.now();
        if (now - lastTap < 300) {
            // Double tap
            if (scale > 1.05) {
                scale = 1;
                translateX = 0;
                translateY = 0;
            } else {
                scale = 2.5;
            }
            applyTransform();
        }
        lastTap = now;
    });

    function getTouchDist(touches) {
        var dx = touches[0].clientX - touches[1].clientX;
        var dy = touches[0].clientY - touches[1].clientY;
        return Math.sqrt(dx * dx + dy * dy);
    }
})();
