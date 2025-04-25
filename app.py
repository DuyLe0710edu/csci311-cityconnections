from flask import Flask, render_template, jsonify
from flask_cors import CORS
import os
import json
import time
from collections import defaultdict
import heapq
import random

app = Flask(__name__)
CORS(app)

# Dataset file mappings
DATASETS = {
    'north_america': 'database/North_America.txt',
    'san_francisco': 'database/San_fran.txt',
    'san_joaquin': 'database/San_joa.txt',
    'oldenburg': 'database/Oldenburg.txt',
    'generated': 'Generated Graph'  # Special marker for randomly generated graphs
}

class UnionFind:
    """Optimized Union-Find data structure with path compression and union by rank"""
    def __init__(self):
        self.parent = {}
        self.rank = defaultdict(int)
        self.size = defaultdict(lambda: 1)
    
    def find(self, x):
        """Find with path compression"""
        if x not in self.parent:
            self.parent[x] = x
            return x
        
        # Path compression
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]
    
    def union(self, x, y):
        """Union by rank with path compression"""
        px, py = self.find(x), self.find(y)
        if px == py:
            return False
            
        # Union by rank
        if self.rank[px] < self.rank[py]:
            px, py = py, px
        self.parent[py] = px
        self.size[px] += self.size[py]
        
        if self.rank[px] == self.rank[py]:
            self.rank[px] += 1
        return True

def read_graph_data(dataset_path, max_edges=None):
    """Read and parse graph data from file with efficient memory usage"""
    print(f"\n{'='*50}")
    print(f"Starting graph construction from: {dataset_path}")
    start_time = time.time()
    
    nodes = set()
    edges = []
    edge_id = 0
    
    print("Reading file and processing edges...")
    with open(dataset_path, 'r') as f:
        for i, line in enumerate(f):
            if max_edges and i >= max_edges:
                break
                
            parts = line.strip().split()
            if len(parts) >= 3:
                source, target, weight = map(float, parts[:3])
                source = int(source)
                target = int(target)
                
                nodes.add(source)
                nodes.add(target)
                edges.append({
                    'id': edge_id,
                    'source': source,
                    'target': target,
                    'distance': weight
                })
                edge_id += 1
                
                if i > 0 and i % 1000 == 0:
                    print(f"Processed {i} edges...")
    
    end_time = time.time()
    print(f"Graph construction completed in {end_time - start_time:.2f} seconds")
    print(f"Total nodes: {len(nodes)}, Total edges: {len(edges)}")
    print("="*50 + "\n")
    
    return {
        'nodes': [{'id': node} for node in nodes],
        'edges': edges
    }

def kruskal_mst_with_steps(edges):
    """Advanced implementation of Kruskal's algorithm optimized for large datasets"""
    print("Starting Kruskal's Algorithm...")
    start_time = time.time()
    
    # Initialize Union-Find data structure
    uf = UnionFind()
    
    # Create min-heap of edges sorted by weight
    edge_heap = [(edge['distance'], edge['id'], edge) for edge in edges]
    heapq.heapify(edge_heap)
    
    mst_edges = []
    total_weight = 0
    steps = []
    edges_processed = 0
    
    # Process edges in order of increasing weight
    while edge_heap and len(mst_edges) < len(set(e['source'] for e in edges) | set(e['target'] for e in edges)) - 1:
        weight, edge_id, edge = heapq.heappop(edge_heap)
        edges_processed += 1
        
        source = edge['source']
        target = edge['target']
        
        # Add checking step
        steps.append({
            'edge_id': edge_id,
            'weight': weight,
            'status': 'checking',
            'total_weight': total_weight
        })
        
        # Check if edge creates a cycle using Union-Find
        if uf.union(source, target):
            # Edge accepted - add to MST
            mst_edges.append(edge)
            total_weight += weight
            steps.append({
                'edge_id': edge_id,
                'weight': weight,
                'status': 'accepted',
                'total_weight': total_weight
            })
        else:
            # Edge rejected - would create cycle
            steps.append({
                'edge_id': edge_id,
                'weight': weight,
                'status': 'rejected',
                'total_weight': total_weight
            })
    
    end_time = time.time()
    print(f"Kruskal's Algorithm completed in {end_time - start_time:.2f} seconds")
    print(f"Edges processed: {edges_processed}")
    print(f"MST edges: {len(mst_edges)}, Total weight: {total_weight:.2f}")
    print("="*50 + "\n")
    
    return {
        'mst_edges': mst_edges,
        'total_weight': total_weight,
        'steps': steps
    }

# Add a function to generate random graphs
def generate_random_graph(min_nodes=8, max_nodes=20):
    """Generate a random graph with given parameters"""
    print(f"\n{'='*50}")
    print(f"Generating random graph with {min_nodes}-{max_nodes} nodes")
    start_time = time.time()
    
    # Generate a random number of nodes
    num_nodes = random.randint(min_nodes, max_nodes)
    nodes = list(range(1, num_nodes + 1))
    
    # Create a basic connected structure (spanning tree) to ensure graph is connected
    edges = []
    edge_id = 0
    
    # First connect all nodes in a path to ensure basic connectivity
    for i in range(len(nodes) - 1):
        weight = round(random.uniform(1.0, 50.0), 2)
        edges.append({
            'id': edge_id,
            'source': nodes[i],
            'target': nodes[i + 1],
            'distance': weight
        })
        edge_id += 1
    
    # Add some random edges to create cycles (ensuring at least one cycle)
    min_extra_edges = max(1, num_nodes // 4)  # At least 1 extra edge to create a cycle
    max_extra_edges = num_nodes // 2 + min_extra_edges
    num_extra_edges = random.randint(min_extra_edges, max_extra_edges)
    
    for _ in range(num_extra_edges):
        source = random.choice(nodes)
        target = random.choice(nodes)
        
        # Ensure we're not creating a self-loop or duplicate edge
        while source == target or any(e['source'] == source and e['target'] == target for e in edges):
            source = random.choice(nodes)
            target = random.choice(nodes)
        
        weight = round(random.uniform(1.0, 50.0), 2)
        edges.append({
            'id': edge_id,
            'source': source,
            'target': target,
            'distance': weight
        })
        edge_id += 1
    
    end_time = time.time()
    print(f"Generated random graph in {end_time - start_time:.2f} seconds")
    print(f"Nodes: {num_nodes}, Edges: {len(edges)}")
    print("="*50 + "\n")
    
    return {
        'nodes': [{'id': node} for node in nodes],
        'edges': edges
    }

@app.route('/')
def index():
    """Main page route"""
    print(f"\n{'='*50}")
    print("Server started. Available datasets:")
    for key, path in DATASETS.items():
        print(f"- {key}: {path}")
    print(f"Access MST visualization at: http://localhost:5001")
    print("="*50 + "\n")
    return render_template('index_3.html')

@app.route('/get_graph_data/<dataset>')
def get_graph_data(dataset):
    """Get graph data for visualization"""
    if dataset not in DATASETS:
        return jsonify({'error': 'Invalid dataset'}), 400
        
    try:
        # Handle generated dataset
        if dataset == 'generated':
            graph_data = generate_random_graph()
            return jsonify(graph_data)
        
        # Handle regular datasets
        graph_data = read_graph_data(DATASETS[dataset])
        return jsonify(graph_data)
    except Exception as e:
        print(f"Error reading graph data: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/run_kruskal/<dataset>')
def run_kruskal(dataset):
    """Run Kruskal's algorithm and return steps for visualization"""
    if dataset not in DATASETS:
        return jsonify({'error': 'Invalid dataset'}), 400
        
    try:
        # Handle generated dataset
        if dataset == 'generated':
            graph_data = generate_random_graph()
            result = kruskal_mst_with_steps(graph_data['edges'])
            return jsonify(result)
        
        # Handle regular datasets
        graph_data = read_graph_data(DATASETS[dataset])
        result = kruskal_mst_with_steps(graph_data['edges'])
        return jsonify(result)
    except Exception as e:
        print(f"Error running Kruskal's algorithm: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(port=5001, debug=True) 