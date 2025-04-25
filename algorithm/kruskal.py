class UnionFind:
    def __init__(self, size):
        self.parent = list(range(size))
        self.rank = [0] * size
        
    def find(self, x):
        # Path compression
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]
    
    def union(self, x, y):
        # Union by rank
        px, py = self.find(x), self.find(y)
        if px == py:
            return False
        
        if self.rank[px] < self.rank[py]:
            px, py = py, px
        self.parent[py] = px
        if self.rank[px] == self.rank[py]:
            self.rank[px] += 1
        return True

def kruskal_mst_with_steps(edges, num_nodes):
    """
    Implements Kruskal's algorithm with step-by-step tracking for visualization.
    
    Args:
        edges: List of edges, each edge is (edge_id, source, target, weight)
        num_nodes: Number of nodes in the graph
        
    Returns:
        steps: List of steps, each step is (edge_id, source, target, weight, status)
               status can be 'checking', 'accepted', or 'rejected'
        mst_edges: List of edges in the MST
    """
    # Sort edges by weight
    sorted_edges = sorted(edges, key=lambda x: x[3])
    
    # Initialize Union-Find data structure
    uf = UnionFind(num_nodes)
    
    # Initialize result containers
    mst_edges = []
    steps = []
    total_weight = 0
    
    # Process each edge
    for edge in sorted_edges:
        edge_id, source, target, weight = edge
        
        # Record checking step
        steps.append({
            'edge_id': edge_id,
            'source': source,
            'target': target,
            'weight': weight,
            'status': 'checking',
            'total_weight': total_weight
        })
        
        # Check if edge creates a cycle
        if uf.union(source, target):
            # Edge accepted into MST
            mst_edges.append(edge)
            total_weight += weight
            steps.append({
                'edge_id': edge_id,
                'source': source,
                'target': target,
                'weight': weight,
                'status': 'accepted',
                'total_weight': total_weight
            })
        else:
            # Edge creates a cycle
            steps.append({
                'edge_id': edge_id,
                'source': source,
                'target': target,
                'weight': weight,
                'status': 'rejected',
                'total_weight': total_weight
            })
    
    return {
        'steps': steps,
        'mst_edges': mst_edges,
        'total_weight': total_weight
    } 