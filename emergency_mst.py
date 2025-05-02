"""
City Emergency Response Manager - MST Planning Module
=================================================
This module implements Minimum Spanning Tree (MST) algorithms 
to simulate infrastructure building or emergency coverage zones.

It provides both Prim's and Kruskal's algorithms for creating MSTs 
from the city emergency graph.
"""

import heapq
from emergency_graph import EmergencyGraph, create_sample_city

def prims_algorithm(graph):
    """
    Implement Prim's algorithm to find the Minimum Spanning Tree (MST) of the city.
    
    Args:
        graph (EmergencyGraph): The city emergency graph.
        
    Returns:
        tuple: (mst_edges, total_cost) where:
            - mst_edges is a list of tuples (source, destination, weight)
            - total_cost is the total infrastructure cost/time
    """
    if not graph.vertices:
        return [], 0
    
    # Choose a starting vertex (first one in the list)
    start_vertex = graph.vertices[0]
    
    # Track vertices added to the MST
    mst_vertices = {start_vertex}
    
    # Track edges in the MST
    mst_edges = []
    
    # Total cost/time of the MST
    total_cost = 0
    
    # Priority queue for edges
    # Format: (weight, source, destination)
    edges_queue = []
    
    # Add all edges from the start vertex to the priority queue
    for neighbor, weight in graph.get_neighbors(start_vertex).items():
        heapq.heappush(edges_queue, (weight, start_vertex, neighbor))
    
    # Continue until all vertices are in the MST or no more edges
    while edges_queue and len(mst_vertices) < len(graph.vertices):
        # Get the edge with the smallest weight
        weight, source, destination = heapq.heappop(edges_queue)
        
        # Skip if the destination is already in the MST
        if destination in mst_vertices:
            continue
        
        # Add the destination to the MST
        mst_vertices.add(destination)
        
        # Add the edge to the MST
        mst_edges.append((source, destination, weight))
        
        # Update the total cost
        total_cost += weight
        
        # Add all edges from the new vertex to the priority queue
        for neighbor, edge_weight in graph.get_neighbors(destination).items():
            if neighbor not in mst_vertices:
                heapq.heappush(edges_queue, (edge_weight, destination, neighbor))
    
    return mst_edges, total_cost


def find_set(parent, vertex):
    """Helper function for Kruskal's algorithm to find the set of a vertex"""
    if parent[vertex] != vertex:
        parent[vertex] = find_set(parent, parent[vertex])
    return parent[vertex]


def union_sets(parent, rank, u, v):
    """Helper function for Kruskal's algorithm to union two sets"""
    root_u = find_set(parent, u)
    root_v = find_set(parent, v)
    
    if root_u != root_v:
        if rank[root_u] < rank[root_v]:
            parent[root_u] = root_v
        elif rank[root_u] > rank[root_v]:
            parent[root_v] = root_u
        else:
            parent[root_v] = root_u
            rank[root_u] += 1


def kruskals_algorithm(graph):
    """
    Implement Kruskal's algorithm to find the Minimum Spanning Tree (MST) of the city.
    
    Args:
        graph (EmergencyGraph): The city emergency graph.
        
    Returns:
        tuple: (mst_edges, total_cost) where:
            - mst_edges is a list of tuples (source, destination, weight)
            - total_cost is the total infrastructure cost/time
    """
    # List to store all edges in the graph
    all_edges = []
    
    # Add all edges to the list
    for vertex in graph.vertices:
        for neighbor, weight in graph.get_neighbors(vertex).items():
            # To avoid duplicates (since the graph is undirected),
            # only add edges where source < destination
            if vertex < neighbor:
                all_edges.append((vertex, neighbor, weight))
    
    # Sort edges by weight
    all_edges.sort(key=lambda x: x[2])
    
    # Initialize parent and rank for union-find
    parent = {vertex: vertex for vertex in graph.vertices}
    rank = {vertex: 0 for vertex in graph.vertices}
    
    # Track edges in the MST
    mst_edges = []
    
    # Total cost/time of the MST
    total_cost = 0
    
    # Process edges in ascending order of weight
    for source, destination, weight in all_edges:
        # If including this edge doesn't create a cycle
        if find_set(parent, source) != find_set(parent, destination):
            # Add the edge to the MST
            mst_edges.append((source, destination, weight))
            
            # Update the total cost
            total_cost += weight
            
            # Union the sets
            union_sets(parent, rank, source, destination)
    
    return mst_edges, total_cost


def visualize_mst(graph, mst_edges):
    """
    Create a simple text-based visualization of the MST.
    
    Args:
        graph (EmergencyGraph): The original city emergency graph.
        mst_edges (list): List of edges in the MST.
        
    Returns:
        str: A multi-line string visualization of the MST.
    """
    result = "Minimum Spanning Tree (Infrastructure Plan):\n"
    result += "=" * 50 + "\n"
    
    # Sort edges for a more readable output
    sorted_edges = sorted(mst_edges)
    
    for source, destination, weight in sorted_edges:
        result += f"{source} -- {weight} mins --> {destination}\n"
    
    return result


def plan_infrastructure(city, algorithm="prim"):
    """
    Plan optimal infrastructure or emergency coverage zones using MST algorithms.
    
    Args:
        city (EmergencyGraph): The city emergency graph.
        algorithm (str, optional): Algorithm to use, either "prim" or "kruskal". 
                                   Defaults to "prim".
    
    Returns:
        tuple: (mst_edges, total_cost) where:
            - mst_edges is a list of tuples (source, destination, weight)
            - total_cost is the total infrastructure cost/time
    """
    if algorithm.lower() == "prim":
        return prims_algorithm(city)
    elif algorithm.lower() == "kruskal":
        return kruskals_algorithm(city)
    else:
        raise ValueError("Algorithm must be either 'prim' or 'kruskal'")


def compare_algorithms(city):
    """
    Compare the results of Prim's and Kruskal's algorithms on the same graph.
    
    Args:
        city (EmergencyGraph): The city emergency graph.
        
    Returns:
        None: Prints comparison results.
    """
    print("\nComparing MST Algorithms for Infrastructure Planning:\n")
    
    # Run Prim's algorithm
    prim_start_time = __import__('time').time()
    prim_edges, prim_cost = prims_algorithm(city)
    prim_end_time = __import__('time').time()
    prim_time = prim_end_time - prim_start_time
    
    # Run Kruskal's algorithm
    kruskal_start_time = __import__('time').time()
    kruskal_edges, kruskal_cost = kruskals_algorithm(city)
    kruskal_end_time = __import__('time').time()
    kruskal_time = kruskal_end_time - kruskal_start_time
    
    # Print results
    print("Prim's Algorithm:")
    print(f"- Total infrastructure cost/time: {prim_cost} minutes")
    print(f"- Number of connections: {len(prim_edges)}")
    print(f"- Execution time: {prim_time:.6f} seconds")
    print("\nKruskal's Algorithm:")
    print(f"- Total infrastructure cost/time: {kruskal_cost} minutes")
    print(f"- Number of connections: {len(kruskal_edges)}")
    print(f"- Execution time: {kruskal_time:.6f} seconds")
    
    # Print differences if any
    if prim_cost != kruskal_cost:
        print("\nNote: The algorithms produced different total costs!")
    else:
        print("\nBoth algorithms produced the same total cost, as expected for MST algorithms.")
    
    # Print the MST from one of the algorithms
    print("\n" + visualize_mst(city, prim_edges))


if __name__ == "__main__":
    # Create a sample city
    city = create_sample_city()
    
    print("City Emergency Response Manager - Infrastructure Planning")
    print("=" * 60)
    print("\nOriginal City Graph:")
    print(city)
    
    # Plan infrastructure using both algorithms and compare
    compare_algorithms(city)
    
    # Demonstrate infrastructure planning with Prim's algorithm
    print("\nPlanning optimal emergency infrastructure with Prim's algorithm:")
    mst_edges, total_cost = plan_infrastructure(city, "prim")
    print(visualize_mst(city, mst_edges))
    print(f"Total infrastructure cost/time: {total_cost} minutes")
    
    # Example: Add more locations and run again
    print("\nAdding more emergency zones to the city...")
    city.add_vertex("E")
    city.add_vertex("F")
    city.add_edge("D", "E", 9)
    city.add_edge("C", "F", 12)
    city.add_edge("E", "F", 5)
    
    print("\nUpdated City Graph:")
    print(city)
    
    # Plan infrastructure for the expanded city
    print("\nPlanning optimal emergency infrastructure for expanded city:")
    mst_edges, total_cost = plan_infrastructure(city, "kruskal")
    print(visualize_mst(city, mst_edges))
    print(f"Total infrastructure cost/time: {total_cost} minutes")
