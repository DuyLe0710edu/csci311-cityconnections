import heapq

def Prims(edges, n):
  """
  Prim's algorithm to find the minimum spanning tree (MST) of a graph.

  Args:
      edges: List of edges, each edge is (weight, source, target)
      n: Number of nodes in the graph

  Returns:
      mst_edges: List of edges in the MST
      total_weight: Total weight of the MST
  """
  # Build adjacency list
  graph = [[] for _ in range(n)]
  for w, u, v in edges:
    graph[u].append((w, v))
    graph[v].append((w, u))
  
  # Initialize data structures
  visited = [False] * n
  min_heap = []
  mst_edges = []
  total_weight = 0
  
  # Start from node 0
  visited[0] = True
  for w, v in graph[0]:
    heapq.heappush(min_heap, (w, 0, v))
  
  while min_heap and len(mst_edges) < n - 1:
    w, u, v = heapq.heappop(min_heap)
    
    if visited[v]:
      continue
    
    # Add edge to MST
    visited[v] = True
    mst_edges.append((u, v, w))
    total_weight += w
    
    # Add all edges from the new node
    for next_w, next_v in graph[v]:
      if not visited[next_v]:
        heapq.heappush(min_heap, (next_w, v, next_v))
  
  if len(mst_edges) != n - 1:
    print("The graph is not connected.")
    
  return mst_edges, total_weight 