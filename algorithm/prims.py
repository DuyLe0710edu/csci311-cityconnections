# import heapq

# def prim_mst_with_steps(edges, num_nodes):
#     """
#     Implements Prim's algorithm with step-by-step tracking for visualization.
    
#     Args:
#         edges: List of edges, each edge is (edge_id, source, target, weight)
#         num_nodes: Number of nodes in the graph
        
#     Returns:
#         steps: List of steps, each step is (edge_id, source, target, weight, status)
#                status can be 'checking' or 'accepted'
#         mst_edges: List of edges in the MST
#         total_weight: Total weight of the MST
#     """
#     from collections import defaultdict

#     # Build adjacency list
#     graph = defaultdict(list)
#     for edge in edges:
#         edge_id, u, v, w = edge
#         graph[u].append((w, edge_id, u, v))
#         graph[v].append((w, edge_id, v, u))
    
#     visited = [False] * num_nodes
#     min_heap = []
#     steps = []
#     mst_edges = []
#     total_weight = 0

#     # Start from node 0 (you could generalize it)
#     visited[0] = True
#     for w, edge_id, u, v in graph[0]:
#         heapq.heappush(min_heap, (w, edge_id, u, v))
    
#     while min_heap and len(mst_edges) < num_nodes - 1:
#         weight, edge_id, u, v = heapq.heappop(min_heap)

#         # Record checking step
#         steps.append({
#             'edge_id': edge_id,
#             'source': u,
#             'target': v,
#             'weight': weight,
#             'status': 'checking',
#             'total_weight': total_weight
#         })

#         if visited[v]:
#             # If the target node is already visited, skip this edge
#             continue
        
#         # Accept this edge
#         visited[v] = True
#         mst_edges.append((edge_id, u, v, weight))
#         total_weight += weight
        
#         steps.append({
#             'edge_id': edge_id,
#             'source': u,
#             'target': v,
#             'weight': weight,
#             'status': 'accepted',
#             'total_weight': total_weight
#         })

#         # Add all edges from the new node
#         for next_weight, next_edge_id, v_from, v_to in graph[v]:
#             if not visited[v_to]:
#                 heapq.heappush(min_heap, (next_weight, next_edge_id, v_from, v_to))

#     return {
#         'steps': steps,
#         'mst_edges': mst_edges,
#         'total_weight': total_weight
#     }