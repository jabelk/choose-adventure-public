/**
 * Coloring page generator for gallery reader.
 * Handles button click → fetch → display → download links.
 */
function initColoringPage(config) {
    var btn = document.getElementById('coloring-btn');
    var area = document.getElementById('coloring-page-area');

    if (!btn || !area || !config.sceneHasPrompt) {
        if (btn) btn.style.display = 'none';
        return;
    }

    btn.addEventListener('click', function () {
        btn.disabled = true;
        btn.textContent = 'Generating...';
        area.innerHTML = '<div class="coloring-loading">Generating coloring page...</div>';

        fetch(config.coloringUrl)
            .then(function (resp) { return resp.json(); })
            .then(function (data) {
                if (data.error) {
                    area.innerHTML =
                        '<div class="coloring-error">' +
                        data.error +
                        '<br><button onclick="document.getElementById(\'coloring-btn\').disabled=false;' +
                        'document.getElementById(\'coloring-btn\').textContent=\'Coloring Page\';' +
                        'document.getElementById(\'coloring-page-area\').innerHTML=\'\';">Retry</button>' +
                        '</div>';
                    return;
                }

                var pdfUrl = config.pdfUrl;
                area.innerHTML =
                    '<div class="coloring-page-result">' +
                    '<img src="' + data.url + '" alt="Coloring page">' +
                    '<div class="coloring-downloads">' +
                    '<a href="' + data.url + '" download>Download PNG</a>' +
                    '<a href="' + pdfUrl + '">Download PDF</a>' +
                    '</div>' +
                    '</div>';

                btn.textContent = 'Coloring Page';
                btn.disabled = false;
            })
            .catch(function () {
                area.innerHTML =
                    '<div class="coloring-error">' +
                    'Coloring page generation failed. Try again.' +
                    '<br><button onclick="document.getElementById(\'coloring-btn\').disabled=false;' +
                    'document.getElementById(\'coloring-btn\').textContent=\'Coloring Page\';' +
                    'document.getElementById(\'coloring-page-area\').innerHTML=\'\';">Retry</button>' +
                    '</div>';
            });
    });
}
