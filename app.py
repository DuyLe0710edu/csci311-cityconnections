import sys
import time
from collections import defaultdict
import heapq
from algorithm.prims_algo import Prims
from algorithm.kruskal_algo import Kruskal

def read_graph_from_file(file_path):
    """
    Read and parse graph data from file
    
    Args:
        file_path: Path to the input file
        
    Returns:
        edges: List of edges (weight, source, target)
        num_nodes: Total number of nodes
    """
    edges = []
    nodes = set()
    
    with open(file_path, 'r') as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) >= 3:
                source, target, weight = map(float, parts[:3])
                source = int(source)
                target = int(target)
                
                nodes.add(source)
                nodes.add(target)
                edges.append((weight, source, target))
    
    return edges, len(nodes)

def write_results_to_file(file_path, mst_edges, total_weight, algorithm_name, execution_time):
    """
    Write MST results to output file
    
    Args:
        file_path: Path to write results to
        mst_edges: List of edges in the MST
        total_weight: Total weight of the MST
        algorithm_name: Name of the algorithm used
        execution_time: Time taken to execute the algorithm
    """
    with open(file_path, 'w') as f:
        f.write(f"Minimum Spanning Tree using {algorithm_name}\n")
        f.write(f"Total weight: {total_weight}\n")
        f.write(f"Execution time: {execution_time:.6f} seconds\n\n")
        f.write("Edges in MST:\n")
        
        for edge in mst_edges:
            if len(edge) == 3:
                u, v, w = edge
                f.write(f"{u} -- {v} : {w}\n")

def main():
    # Check command line arguments
    if len(sys.argv) != 3:
        print("Usage: python app.py <input_file> output.txt")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    try:
        # Read input graph
        edges, num_nodes = read_graph_from_file(input_file)
        print(f"Read graph with {num_nodes} nodes and {len(edges)} edges from {input_file}")
        
        # Run Prim's algorithm with execution time measurement
        start_time = time.time()
        mst_edges, total_weight = Prims(edges, num_nodes)
        execution_time = time.time() - start_time
        
        # Write results to output file
        write_results_to_file(output_file, mst_edges, total_weight, "Prim's Algorithm", execution_time)
        
        print(f"MST results written to {output_file}")
        print(f"Total MST weight: {total_weight}")
        print(f"Execution time: {execution_time:.6f} seconds")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main() 