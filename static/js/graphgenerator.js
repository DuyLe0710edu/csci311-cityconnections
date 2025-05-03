/**
 * Graph Generator and Visualization Module
 * Handles graph rendering and Kruskal's algorithm visualization
 */

// Determine if a graph is considered "generated" (small)
function isGeneratedGraph(nodes) {
    return nodes.length <= 30;
}

// Initialize SVG for graph visualization
function initializeGraph(svg, width, height, zoom) {
    svg.selectAll("*").remove();
    
    svg.call(zoom);
    svg.append('g');
}

// Render a graph with nodes and edges
function renderGraph(data, svg, width, height, zoom, transform) {
    // Determine if this is a generated/small graph
    const isSmallGraph = isGeneratedGraph(data.nodes);
    
    // Create force simulation
    const simulation = d3.forceSimulation(data.nodes)
        .force('link', d3.forceLink(data.edges)
            .id(d => d.id)
            .distance(d => Math.min(150, d.distance * 0.2)))
        .force('charge', d3.forceManyBody().strength(-120))
        .force('center', d3.forceCenter(width / 2, height / 2));

    const g = svg.select('g');

    // Draw edges
    const edges = g.selectAll('.edge')
        .data(data.edges)
        .enter()
        .append('g')
        .attr('class', 'edge')
        .attr('id', d => `edge-${d.id}`);

    edges.append('line')
        .style('stroke', '#999')
        .style('stroke-opacity', 0.6)
        .style('stroke-width', 1);

    // Add edge weight labels for all graphs
    const edgeLabels = edges.append('g')
        .attr('class', 'edge-label-group');

    edgeLabels.append('rect')
        .attr('class', 'edge-weight-bg')
        .attr('x', -15)
        .attr('y', -7)
        .attr('width', 30)
        .attr('height', 14)
        .style('opacity', 0.7);

    edgeLabels.append('text')
        .attr('class', 'edge-label')
        .text(d => d.distance.toFixed(1));

    // Draw nodes (all graphs have black dots)
    const nodeGroups = g.selectAll('.node-group')
        .data(data.nodes)
        .enter()
        .append('g')
        .attr('class', 'node-group');
        
    nodeGroups.append('circle')
        .attr('class', 'node')
        .attr('r', d => {
            // Node size based on graph size
            if (data.nodes.length > 100) return 2;
            if (data.nodes.length > 30) return 4;
            return 6;
        });
    
    // Only add node labels for small graphs
    if (isSmallGraph) {
        nodeGroups.append('text')
            .attr('class', 'node-label')
            .text(d => d.id)
            .style('font-size', '5px');
    }

    // Update positions on simulation tick
    simulation.on('tick', () => {
        // Update edge positions
        edges.selectAll('line')
            .attr('x1', d => d.source.x)
            .attr('y1', d => d.source.y)
            .attr('x2', d => d.target.x)
            .attr('y2', d => d.target.y);

        // Update edge label positions
        edges.selectAll('.edge-label-group')
            .attr('transform', d => {
                const midX = (d.source.x + d.target.x) / 2;
                const midY = (d.source.y + d.target.y) / 2;
                return `translate(${midX},${midY})`;
            });
            
        // Update node positions
        nodeGroups.attr('transform', d => `translate(${d.x},${d.y})`);
    });

    // Add hover effect for edges
    edges.on('mouseover', function() {
        d3.select(this).selectAll('line')
            .style('stroke-width', 2)
            .style('stroke-opacity', 1);
        d3.select(this).selectAll('.edge-label-group')
            .style('font-weight', 'bold');
    }).on('mouseout', function() {
        const edge = d3.select(this);
        if (!edge.classed('mst-edge')) {
            edge.selectAll('line')
                .style('stroke-width', 1)
                .style('stroke-opacity', 0.6);
        }
        edge.selectAll('.edge-label-group')
            .style('font-weight', 'normal');
    });
    
    // Add hover effect for nodes only on small graphs
    if (isSmallGraph) {
        nodeGroups.on('mouseover', function(event, d) {
            d3.select(this).select('.node')
                .attr('r', function() {
                    const currentR = parseFloat(d3.select(this).attr('r'));
                    return currentR * 1.2;
                });
            d3.select(this).select('.node-label')
                .style('font-size', '6px')
                .style('font-weight', 'bolder');
        }).on('mouseout', function() {
            d3.select(this).select('.node')
                .attr('r', 6);
            d3.select(this).select('.node-label')
                .style('font-size', '5px')
                .style('font-weight', 'bold');
        });
    }
    
    // Center and scale the graph
    setTimeout(() => {
        const bounds = g.node().getBBox();
        const scale = 0.9 * Math.min(
            width / bounds.width,
            height / bounds.height
        );
        const tx = width / 2 - (bounds.x + bounds.width / 2) * scale;
        const ty = height / 2 - (bounds.y + bounds.height / 2) * scale;
        
        svg.transition()
            .duration(500)
            .call(zoom.transform, d3.zoomIdentity
                .translate(tx, ty)
                .scale(scale));
    }, 100);
    
    return simulation;
}

// Run Kruskal's algorithm visualization
async function runKruskalVisualization(currentGraph, svg, mstResults, mstEdgesList, statusBar) {
    if (!currentGraph) return;
    
    try {
        statusBar.style.display = 'block';
        mstResults.style.display = 'block';
        mstEdgesList.innerHTML = '';

        // Reset all edges
        svg.selectAll('.edge')
            .classed('mst-edge', false)
            .select('line')
            .style('stroke', '#999')
            .style('stroke-opacity', 0.6)
            .style('stroke-width', 1);
        
        // Determine visualization speed based on graph size and user preference
        const isSmallGraph = isGeneratedGraph(currentGraph.nodes);
        
        // Get speed control value (0-100, where 100 is fastest)
        const speedControl = document.getElementById('speedControl');
        const speedValue = speedControl ? parseInt(speedControl.value) : 50;
        
        // Calculate delay - invert the speed value (100 = fast = low delay)
        // For small graphs: between 500ms (slowest) and 50ms (fastest)
        // For large graphs: between 50ms (slowest) and 0ms (fastest)
        const maxDelay = isSmallGraph ? 500 : 50;
        const minDelay = isSmallGraph ? 50 : 0;
        const checkingDelay = maxDelay - ((speedValue / 100) * (maxDelay - minDelay));
        
        // For rejection highlight, use a bit longer delay
        const rejectionDelay = checkingDelay * 1.5;

        // Process each step
        for (const step of currentGraph.steps) {
            const edge = svg.select(`#edge-${step.edge_id}`);
            if (edge.empty()) continue;

            const line = edge.select('line');
            const edgeInfo = currentGraph.edges.find(e => e.id === step.edge_id);
            
            if (!edgeInfo) {
                console.error('Could not find edge info for edge id:', step.edge_id);
                continue;
            }
            
            // Make sure source and target are integers
            const sourceId = typeof edgeInfo.source === 'object' ? edgeInfo.source.id : edgeInfo.source;
            const targetId = typeof edgeInfo.target === 'object' ? edgeInfo.target.id : edgeInfo.target;
            
            // Update status bar (not the final results panel)
            document.getElementById('stepInfo').textContent = 
                `Checking edge ${step.edge_id} (${sourceId} → ${targetId}, weight: ${edgeInfo.distance.toFixed(2)})`;
            
            // Only update the status bar's total weight, not the final results panel
            const statusBarWeight = document.getElementById('statusBarWeight');
            if (statusBarWeight) {
                statusBarWeight.textContent = step.total_weight.toFixed(2);
            }
                
            if (step.status === 'checking') {
                line.style('stroke', '#007bff')
                    .style('stroke-width', 2)
                    .style('stroke-opacity', 1);
                    
                // Create checking edge element
                const checkingElement = document.createElement('div');
                checkingElement.className = 'mst-edge checking';
                checkingElement.textContent = `${sourceId} → ${targetId} (${edgeInfo.distance.toFixed(2)})`;
                checkingElement.id = `mst-edge-${step.edge_id}`;
                mstEdgesList.appendChild(checkingElement);
            } else if (step.status === 'accepted') {
                edge.classed('mst-edge', true);
                line.style('stroke', '#28a745')
                    .style('stroke-width', 2)
                    .style('stroke-opacity', 1);
                
                // Update the existing edge element
                const existingEdge = document.getElementById(`mst-edge-${step.edge_id}`);
                if (existingEdge) {
                    existingEdge.className = 'mst-edge accepted';
                    existingEdge.textContent = `${sourceId} → ${targetId} (${edgeInfo.distance.toFixed(2)})`;
                }
            } else if (step.status === 'rejected') {
                line.style('stroke', '#dc3545')
                    .style('stroke-width', 2)
                    .style('stroke-opacity', 1);
                
                await new Promise(resolve => setTimeout(resolve, rejectionDelay));
                
                line.style('stroke', '#999')
                    .style('stroke-width', 1)
                    .style('stroke-opacity', 0.6);
                    
                // Remove the rejected edge from the list
                const existingEdge = document.getElementById(`mst-edge-${step.edge_id}`);
                if (existingEdge) {
                    existingEdge.remove();
                }
            }
            
            // Wait between steps - use speed based on slider and graph size
            await new Promise(resolve => setTimeout(resolve, checkingDelay));
        }
    } catch (error) {
        console.error('Error in Kruskal visualization:', error);
    }
} 