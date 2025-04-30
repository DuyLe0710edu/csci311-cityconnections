class Union_Find:
  def __init__(self, n):
    self.parent = [-1] * n

  def find(self, x):
    # Find the root of x
    if self.parent[x] < 0:
      return x
    self.parent[x] = self.find(self.parent[x])
    return self.parent[x]

  def union(self, x, y):
    # Union the sets containing x and y
    # If x and y are already in the same set, return False
    a, b = self.find(x), self.find(y);
    if a == b:
      return False


    if -self.parent[a] < -self.parent[b]:
      a, b = b, a

    # Merge the sets
    self.parent[a] += self.parent[b]
    self.parent[b] = a
    return True

def Kruskal(edges, n):
  """
  Kruskal's algorithm to find the minimum spanning tree (MST) of a graph.

  Args:
      edges: List of edges, each edge is (edge_id, source, target, weight)
      n: Number of nodes in the graph

  Returns:
      mst_edges: List of edges in the MST
      total_weight: Total weight of the MST
  """
  # Sort edges by weight
  edges.sort(key=lambda x: x[0])

  # Initialize Union-Find data structure
  uf = Union_Find(n)

  # Initialize result containers
  mst_edges = []
  total_weight = 0

  # Process each edge
  for w, u, v in edges:
    if uf.union(u, v):
      total_weight += w
      mst_edges.append((u, v, w))
      if len(mst_edges) == n - 1:
        break

  if len(mst_edges) != n - 1:
    print("The graph is not connected.")

  return mst_edges, total_weight
