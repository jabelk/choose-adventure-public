/**
 * Tree Map rendering component using D3.js
 * Renders an interactive tree visualization of story branches.
 */

/**
 * Render a tree map into the given container.
 * @param {string} containerId - DOM element ID to render into
 * @param {object} treeData - Nested tree data from server
 * @param {string} currentId - Current scene ID
 * @param {string} urlPrefix - Tier URL prefix (e.g., "/kids")
 * @param {string} mode - "active" (POST navigate) or "gallery" (GET link)
 */
function renderTreeMap(containerId, treeData, currentId, urlPrefix, mode) {
    const container = document.getElementById(containerId);
    if (!container || !treeData || !treeData.id) return;

    // Clear previous render
    container.innerHTML = '';

    // Layout config
    const nodeW = 100;
    const nodeH = 60;
    const margin = { top: 20, right: 40, bottom: 20, left: 40 };

    // Build D3 hierarchy
    const root = d3.hierarchy(treeData, d => d.children);

    // Compute tree layout
    const treeLayout = d3.tree().nodeSize([nodeH + 10, nodeW + 40]);
    treeLayout(root);

    // Compute bounds
    let x0 = Infinity, x1 = -Infinity;
    root.each(d => {
        if (d.x < x0) x0 = d.x;
        if (d.x > x1) x1 = d.x;
    });

    const width = (root.height + 1) * (nodeW + 40) + margin.left + margin.right;
    const height = (x1 - x0) + nodeH + margin.top + margin.bottom;

    // Create SVG
    const svg = d3.select(container)
        .append('svg')
        .attr('width', width)
        .attr('height', height)
        .attr('class', 'tree-map-svg');

    const g = svg.append('g')
        .attr('transform', `translate(${margin.left},${margin.top - x0 + nodeH / 2})`);

    // Draw links
    g.selectAll('.tree-link')
        .data(root.links())
        .join('path')
        .attr('class', d => {
            const classes = ['tree-link'];
            if (d.target.data.on_path) classes.push('on-path');
            return classes.join(' ');
        })
        .attr('d', d3.linkHorizontal()
            .x(d => d.y)
            .y(d => d.x)
        );

    // Draw nodes
    const node = g.selectAll('.tree-node')
        .data(root.descendants())
        .join('g')
        .attr('class', d => {
            const classes = ['tree-node'];
            if (d.data.is_current) classes.push('current');
            if (d.data.on_path) classes.push('on-path');
            if (d.data.is_ending) classes.push('ending');
            return classes.join(' ');
        })
        .attr('transform', d => `translate(${d.y},${d.x})`)
        .style('cursor', 'pointer')
        .on('click', (event, d) => navigateToScene(d.data.id, urlPrefix, mode));

    // Node circles
    node.append('circle')
        .attr('r', 14);

    // Node labels
    node.append('text')
        .attr('dy', '0.35em')
        .attr('text-anchor', 'middle')
        .attr('class', 'tree-node-label')
        .text(d => d.data.label);

    // Choice text on hover (tooltip via title)
    node.append('title')
        .text(d => {
            let tip = d.data.label;
            if (d.data.choice_text) tip += ': ' + d.data.choice_text;
            if (d.data.is_ending) tip += ' (ending)';
            if (d.data.is_current) tip += ' (you are here)';
            return tip;
        });
}

/**
 * Navigate to a scene when a tree node is clicked.
 */
function navigateToScene(sceneId, urlPrefix, mode) {
    if (mode === 'active') {
        // POST to navigate route
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = urlPrefix + '/story/navigate/' + sceneId;
        document.body.appendChild(form);
        form.submit();
    } else {
        // Gallery mode — GET link
        const storyId = window.treeMapStoryId;
        if (storyId) {
            window.location.href = urlPrefix + '/gallery/' + storyId + '/' + sceneId;
        }
    }
}
