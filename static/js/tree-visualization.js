/**
 * Interactive Tree Visualization using D3.js
 * Represents symbolic resonance patterns as an interactive tree
 */

class TreeVisualization {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.emptyState = document.getElementById('emptyState');
        
        this.width = 0;
        this.height = 500;
        this.margin = { top: 20, right: 20, bottom: 20, left: 20 };
        
        this.svg = null;
        this.g = null;
        this.tree = null;
        this.root = null;
        
        this.zoom = d3.zoom()
            .scaleExtent([0.1, 3])
            .on('zoom', (event) => {
                this.g.attr('transform', event.transform);
            });
        
        this.tooltip = this.createTooltip();
        
        this.initializeSVG();
        this.setupResizeObserver();
    }
    
    initializeSVG() {
        this.updateDimensions();
        
        // Remove existing SVG if any
        d3.select(this.container).select('svg').remove();
        
        // Create SVG
        this.svg = d3.select(this.container)
            .append('svg')
            .attr('class', 'tree-container')
            .attr('width', this.width)
            .attr('height', this.height)
            .call(this.zoom);
        
        // Create main group for transformations
        this.g = this.svg.append('g')
            .attr('class', 'tree-group');
        
        // Initialize tree layout
        this.tree = d3.tree()
            .size([this.height - this.margin.top - this.margin.bottom, 
                   this.width - this.margin.left - this.margin.right]);
    }
    
    updateDimensions() {
        const containerRect = this.container.getBoundingClientRect();
        this.width = containerRect.width || 800;
        this.height = Math.max(containerRect.height || 500, 500);
        
        if (this.svg) {
            this.svg
                .attr('width', this.width)
                .attr('height', this.height);
            
            this.tree.size([this.height - this.margin.top - this.margin.bottom, 
                           this.width - this.margin.left - this.margin.right]);
        }
    }
    
    setupResizeObserver() {
        if (window.ResizeObserver) {
            const resizeObserver = new ResizeObserver(() => {
                this.updateDimensions();
                if (this.root) {
                    this.render();
                }
            });
            resizeObserver.observe(this.container);
        }
    }
    
    createTooltip() {
        return d3.select('body')
            .append('div')
            .attr('class', 'tooltip')
            .style('position', 'absolute')
            .style('visibility', 'hidden');
    }
    
    updateTree(treeData) {
        if (!treeData || !treeData.name) {
            this.clearTree();
            return;
        }
        
        this.hideEmptyState();
        
        // Process the tree data
        this.root = d3.hierarchy(treeData);
        this.root.x0 = this.height / 2;
        this.root.y0 = 0;
        
        // Collapse nodes initially (except root and first level)
        this.root.children?.forEach(child => {
            if (child.children) {
                this.collapse(child);
            }
        });
        
        this.render();
        this.centerTree();
    }
    
    render() {
        if (!this.root) return;
        
        // Generate tree layout
        const treeData = this.tree(this.root);
        const nodes = treeData.descendants();
        const links = treeData.descendants().slice(1);
        
        // Update node positions
        nodes.forEach(d => {
            d.y = d.depth * 180; // Horizontal spacing
        });
        
        // Update links
        const link = this.g.selectAll('.link')
            .data(links, d => d.id || (d.id = ++this.nodeId));
        
        const linkEnter = link.enter()
            .insert('path', 'g')
            .attr('class', 'link')
            .attr('d', d => this.diagonal(d.parent || this.root, d.parent || this.root));
        
        const linkUpdate = linkEnter.merge(link);
        
        linkUpdate.transition()
            .duration(600)
            .attr('d', d => this.diagonal(d, d.parent));
        
        link.exit()
            .transition()
            .duration(600)
            .attr('d', d => this.diagonal(this.root, this.root))
            .remove();
        
        // Update nodes
        const node = this.g.selectAll('.node')
            .data(nodes, d => d.id || (d.id = ++this.nodeId));
        
        const nodeEnter = node.enter()
            .append('g')
            .attr('class', d => `node node-${d.data.type}`)
            .attr('transform', d => `translate(${this.root.y0},${this.root.x0})`)
            .on('click', (event, d) => this.toggleNode(event, d))
            .on('mouseover', (event, d) => this.showTooltip(event, d))
            .on('mouseout', () => this.hideTooltip());
        
        // Add circles for nodes
        nodeEnter.append('circle')
            .attr('r', 1e-6);
        
        // Add text labels
        nodeEnter.append('text')
            .attr('dy', '.35em')
            .attr('x', d => d.children || d._children ? -13 : 13)
            .attr('text-anchor', d => d.children || d._children ? 'end' : 'start')
            .text(d => d.data.name)
            .style('fill-opacity', 1e-6);
        
        // Update existing nodes
        const nodeUpdate = nodeEnter.merge(node);
        
        nodeUpdate.transition()
            .duration(600)
            .attr('transform', d => `translate(${d.y},${d.x})`);
        
        nodeUpdate.select('circle')
            .transition()
            .duration(600)
            .attr('r', d => Math.max(4, Math.min(10, d.data.value || 4)))
            .style('fill', d => this.getNodeColor(d));
        
        nodeUpdate.select('text')
            .transition()
            .duration(600)
            .style('fill-opacity', 1)
            .attr('x', d => d.children || d._children ? -13 : 13)
            .attr('text-anchor', d => d.children || d._children ? 'end' : 'start');
        
        // Remove exiting nodes
        const nodeExit = node.exit()
            .transition()
            .duration(600)
            .attr('transform', d => `translate(${this.root.y},${this.root.x})`)
            .remove();
        
        nodeExit.select('circle')
            .attr('r', 1e-6);
        
        nodeExit.select('text')
            .style('fill-opacity', 1e-6);
        
        // Store old positions for transition
        nodes.forEach(d => {
            d.x0 = d.x;
            d.y0 = d.y;
        });
    }
    
    diagonal(s, d) {
        return `M ${s.y} ${s.x}
                C ${(s.y + d.y) / 2} ${s.x},
                  ${(s.y + d.y) / 2} ${d.x},
                  ${d.y} ${d.x}`;
    }
    
    getNodeColor(d) {
        const colors = {
            'root': '#ffc107',
            'entity_group': '#0dcaf0',
            'entity': '#198754',
            'relationship_group': '#dc3545',
            'relationship': '#6c757d',
            'theme_group': '#0d6efd',
            'theme': '#6f42c1'
        };
        return colors[d.data.type] || '#6c757d';
    }
    
    toggleNode(event, d) {
        if (d.children) {
            d._children = d.children;
            d.children = null;
        } else {
            d.children = d._children;
            d._children = null;
        }
        this.render();
    }
    
    collapse(d) {
        if (d.children) {
            d._children = d.children;
            d._children.forEach(child => this.collapse(child));
            d.children = null;
        }
    }
    
    expandAll() {
        if (!this.root) return;
        
        const expand = (d) => {
            if (d._children) {
                d.children = d._children;
                d._children = null;
            }
            if (d.children) {
                d.children.forEach(expand);
            }
        };
        
        expand(this.root);
        this.render();
    }
    
    collapseAll() {
        if (!this.root) return;
        
        if (this.root.children) {
            this.root.children.forEach(child => this.collapse(child));
        }
        this.render();
    }
    
    centerTree() {
        if (!this.root) return;
        
        const bounds = this.g.node().getBBox();
        const fullWidth = bounds.width;
        const fullHeight = bounds.height;
        const centerX = bounds.x + fullWidth / 2;
        const centerY = bounds.y + fullHeight / 2;
        
        const scale = 0.9 / Math.max(fullWidth / this.width, fullHeight / this.height);
        const translate = [this.width / 2 - scale * centerX, this.height / 2 - scale * centerY];
        
        this.svg.transition()
            .duration(750)
            .call(this.zoom.transform, d3.zoomIdentity.translate(translate[0], translate[1]).scale(scale));
    }
    
    showTooltip(event, d) {
        let content = `<strong>${d.data.name}</strong><br/>`;
        content += `Type: ${d.data.type}<br/>`;
        
        if (d.data.value) {
            content += `Value: ${d.data.value}<br/>`;
        }
        
        if (d.data.description) {
            content += `Description: ${d.data.description}<br/>`;
        }
        
        if (d.data.sentiment) {
            content += `Sentiment: ${d.data.sentiment.polarity.toFixed(2)}<br/>`;
        }
        
        this.tooltip
            .style('visibility', 'visible')
            .html(content)
            .style('left', (event.pageX + 10) + 'px')
            .style('top', (event.pageY - 10) + 'px')
            .classed('show', true);
    }
    
    hideTooltip() {
        this.tooltip
            .style('visibility', 'hidden')
            .classed('show', false);
    }
    
    clearTree() {
        this.showEmptyState();
        if (this.g) {
            this.g.selectAll('*').remove();
        }
        this.root = null;
    }
    
    showEmptyState() {
        if (this.emptyState) {
            this.emptyState.style.display = 'block';
        }
    }
    
    hideEmptyState() {
        if (this.emptyState) {
            this.emptyState.style.display = 'none';
        }
    }
}

// Initialize node ID counter
TreeVisualization.prototype.nodeId = 0;
