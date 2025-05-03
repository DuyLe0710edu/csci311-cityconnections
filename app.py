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

def read_graph_data(dataset_path, max_edges=10000):
    """Read and parse graph data from file"""
    nodes = set()
    edges = []
    
    with open(dataset_path, 'r') as f:
        for i, line in enumerate(f):
            if i >= max_edges:  # Limit edges for initial visualization
                break
                
            parts = line.strip().split()
            if len(parts) >= 3:
                source, target, weight = map(float, parts[:3])
                source = int(source)
                target = int(target)
                
                nodes.add(source)
                nodes.add(target)
                edges.append({
                    'id': i,  # Use line number as edge ID
                    'source': source,
                    'target': target,
                    'distance': weight
                })
    
    # Convert nodes to list of dictionaries
    nodes = [{'id': node_id} for node_id in nodes]
    
    print(f"Graph loaded: {len(nodes)} nodes, {len(edges)} edges")
    
    return {
        'nodes': nodes,
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

def prim_mst_with_steps(edges):
    """Implementation of Prim's algorithm with step tracking for visualization"""
    print("Starting Prim's Algorithm...")
    start_time = time.time()
    
    # Build adjacency list
    graph = defaultdict(list)
    nodes = set()
    
    for edge in edges:
        source = edge['source']
        target = edge['target']
        weight = edge['distance']
        edge_id = edge['id']
        
        graph[source].append((weight, edge_id, source, target))
        graph[target].append((weight, edge_id, target, source))
        
        nodes.add(source)
        nodes.add(target)
    
    num_nodes = len(nodes)
    visited = {node: False for node in nodes}
    min_heap = []
    steps = []
    mst_edges = []
    total_weight = 0
    edges_processed = 0
    
    # Start from the first node in the graph
    start_node = edges[0]['source']
    visited[start_node] = True
    
    # Add edges from the starting node to the heap
    for weight, edge_id, u, v in graph[start_node]:
        heapq.heappush(min_heap, (weight, edge_id, u, v))
    
    # Run Prim's algorithm
    while min_heap and len(mst_edges) < num_nodes - 1:
        weight, edge_id, u, v = heapq.heappop(min_heap)
        edges_processed += 1
        
        # Record checking step
        steps.append({
            'edge_id': edge_id,
            'weight': weight,
            'status': 'checking',
            'total_weight': total_weight
        })
        
        if visited[v]:
            # If target node is already visited, skip this edge
            steps.append({
                'edge_id': edge_id,
                'weight': weight,
                'status': 'rejected',
                'total_weight': total_weight
            })
            continue
        
        # Accept this edge
        visited[v] = True
        
        # Find the actual edge object for the MST result
        edge_obj = next((e for e in edges if e['id'] == edge_id), None)
        if edge_obj:
            mst_edges.append(edge_obj)
            total_weight += weight
            
            steps.append({
                'edge_id': edge_id,
                'weight': weight,
                'status': 'accepted',
                'total_weight': total_weight
            })
            
            # Add all edges from the newly added node
            for next_weight, next_edge_id, v_from, v_to in graph[v]:
                if not visited[v_to]:
                    heapq.heappush(min_heap, (next_weight, next_edge_id, v_from, v_to))
    
    end_time = time.time()
    print(f"Prim's Algorithm completed in {end_time - start_time:.2f} seconds")
    print(f"Edges processed: {edges_processed}")
    print(f"MST edges: {len(mst_edges)}, Total weight: {total_weight:.2f}")
    print("="*50 + "\n")
    
    return {
        'mst_edges': mst_edges,
        'total_weight': total_weight,
        'steps': steps
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
        
        # Handle regular datasets - visualization subset
        graph_data = read_graph_data(DATASETS[dataset])
        
        # Run algorithm on visualization subset (for step visualization)
        result = kruskal_mst_with_steps(graph_data['edges'])
        
        # Check if we need to process more data
        try:
            with open(DATASETS[dataset], 'r') as f:
                total_lines = sum(1 for _ in f)
            
            # If we have more data than our visualization subset
            if total_lines > 10000:
                print(f"Dataset has {total_lines} edges. Processing the rest without visualization steps...")
                
                # Load the rest of the edges (starting from where we left off)
                remaining_edges = []
                with open(DATASETS[dataset], 'r') as f:
                    # Skip the edges we've already processed
                    for i in range(10000):
                        next(f)
                    
                    # Read the rest
                    for i, line in enumerate(f, start=10000):
                        parts = line.strip().split()
                        if len(parts) >= 3:
                            source, target, weight = map(float, parts[:3])
                            source = int(source)
                            target = int(target)
                            
                            remaining_edges.append({
                                'id': i,
                                'source': source,
                                'target': target,
                                'distance': weight
                            })
                
                # Continue the MST calculation from where we left off
                if remaining_edges:
                    # Get the current UnionFind state from the first phase
                    uf = UnionFind()
                    for edge in result['mst_edges']:
                        uf.union(edge['source'], edge['target'])
                    
                    current_total_weight = result['total_weight']
                    
                    # Process remaining edges
                    for edge in sorted(remaining_edges, key=lambda x: x['distance']):
                        if uf.union(edge['source'], edge['target']):
                            # Edge accepted into MST
                            result['mst_edges'].append(edge)
                            current_total_weight += edge['distance']
                    
                    # Update the total weight
                    result['total_weight'] = current_total_weight
                    print(f"Final MST weight after processing all edges: {current_total_weight:.2f}")
        
        except Exception as e:
            print(f"Warning: Couldn't process the entire dataset: {str(e)}. Using subset result.")
        
        return jsonify(result)
        
    except Exception as e:
        print(f"Error running Kruskal's algorithm: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/run_prims/<dataset>')
def run_prims(dataset):
    """Run Prim's algorithm and return steps for visualization"""
    if dataset not in DATASETS:
        return jsonify({'error': 'Invalid dataset'}), 400
        
    try:
        # Handle generated dataset
        if dataset == 'generated':
            graph_data = generate_random_graph()
            result = prim_mst_with_steps(graph_data['edges'])
            return jsonify(result)
        
        # Handle regular datasets - visualization subset
        graph_data = read_graph_data(DATASETS[dataset])
        
        # Run algorithm on visualization subset (for step visualization)
        result = prim_mst_with_steps(graph_data['edges'])
        
        # Check if we need to process more data
        try:
            with open(DATASETS[dataset], 'r') as f:
                total_lines = sum(1 for _ in f)
            
            # If we have more data than our visualization subset
            if total_lines > 10000:
                print(f"Dataset has {total_lines} edges. Processing the rest without visualization steps...")
                
                # Load the rest of the edges (starting from where we left off)
                remaining_edges = []
                with open(DATASETS[dataset], 'r') as f:
                    # Skip the edges we've already processed
                    for i in range(10000):
                        next(f)
                    
                    # Read the rest
                    for i, line in enumerate(f, start=10000):
                        parts = line.strip().split()
                        if len(parts) >= 3:
                            source, target, weight = map(float, parts[:3])
                            source = int(source)
                            target = int(target)
                            
                            remaining_edges.append({
                                'id': i,
                                'source': source,
                                'target': target,
                                'distance': weight
                            })
                
                # For Prim's, we need to reconstruct the complete graph and reprocess
                if remaining_edges:
                    # Combine both sets of edges
                    all_edges = graph_data['edges'] + remaining_edges
                    
                    # Build adjacency list
                    graph = defaultdict(list)
                    nodes = set()
                    
                    for edge in all_edges:
                        source = edge['source']
                        target = edge['target']
                        weight = edge['distance']
                        edge_id = edge['id']
                        
                        graph[source].append((weight, edge_id, source, target))
                        graph[target].append((weight, edge_id, target, source))
                        
                        nodes.add(source)
                        nodes.add(target)
                    
                    # Get the currently visualized MST nodes
                    visualized_nodes = set()
                    for edge in result['mst_edges']:
                        visualized_nodes.add(edge['source'])
                        visualized_nodes.add(edge['target'])
                    
                    # Process the full graph but don't overwrite the visualization steps
                    visited = {node: False for node in nodes}
                    mst_edges = []
                    total_weight = 0
                    
                    # Start from a node we already visited
                    start_node = next(iter(visualized_nodes))
                    visited[start_node] = True
                    
                    # Use the same priority queue algorithm
                    min_heap = []
                    for weight, edge_id, u, v in graph[start_node]:
                        heapq.heappush(min_heap, (weight, edge_id, u, v))
                    
                    while min_heap:
                        weight, edge_id, u, v = heapq.heappop(min_heap)
                        
                        if visited[v]:
                            continue
                        
                        # Accept this edge
                        visited[v] = True
                        
                        # Find the actual edge object
                        edge_obj = next((e for e in all_edges if e['id'] == edge_id), None)
                        if edge_obj:
                            mst_edges.append(edge_obj)
                            total_weight += weight
                            
                            # Add all edges from the newly added node
                            for next_weight, next_edge_id, v_from, v_to in graph[v]:
                                if not visited[v_to]:
                                    heapq.heappush(min_heap, (next_weight, next_edge_id, v_from, v_to))
                    
                    # Get only the visualized subset of edges for UI display
                    viz_mst_edges = [edge for edge in mst_edges if edge['id'] < 10000]
                    
                    # Update result with correct total weight but keep viz steps
                    result['total_weight'] = total_weight
                    result['mst_edges'] = viz_mst_edges
                    print(f"Final MST weight after processing all edges: {total_weight:.2f}")
        
        except Exception as e:
            print(f"Warning: Couldn't process the entire dataset: {str(e)}. Using subset result.")
        
        return jsonify(result)
        
    except Exception as e:
        print(f"Error running Prim's algorithm: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(port=5001, debug=True) 