/**
 * Template Shuffle — show a random subset of template cards, with a shuffle button.
 */
function initTemplateShuffle(displayCount) {
    var grid = document.querySelector('.template-grid');
    if (!grid) return;

    var allCards = Array.prototype.slice.call(grid.querySelectorAll('.template-card'));
    if (allCards.length <= displayCount) return; // No shuffling needed

    var currentIndices = [];

    function fisherYatesShuffle(arr) {
        var a = arr.slice();
        for (var i = a.length - 1; i > 0; i--) {
            var j = Math.floor(Math.random() * (i + 1));
            var tmp = a[i];
            a[i] = a[j];
            a[j] = tmp;
        }
        return a;
    }

    function showSubset(excludeIndices) {
        // Build candidate pool excluding previously shown indices (if possible)
        var candidates = [];
        for (var i = 0; i < allCards.length; i++) {
            if (excludeIndices.indexOf(i) === -1) {
                candidates.push(i);
            }
        }

        // If not enough fresh candidates, use full pool
        if (candidates.length < displayCount) {
            candidates = [];
            for (var j = 0; j < allCards.length; j++) {
                candidates.push(j);
            }
        }

        var shuffled = fisherYatesShuffle(candidates);
        var selected = shuffled.slice(0, displayCount);

        // Hide all, then show selected
        for (var k = 0; k < allCards.length; k++) {
            allCards[k].classList.add('template-hidden');
        }
        for (var m = 0; m < selected.length; m++) {
            allCards[selected[m]].classList.remove('template-hidden');
        }

        currentIndices = selected;
    }

    // Initial display
    showSubset([]);

    // Wire up shuffle button
    var btn = document.getElementById('shuffle-btn');
    if (btn) {
        btn.addEventListener('click', function() {
            showSubset(currentIndices);
        });
    }
}
