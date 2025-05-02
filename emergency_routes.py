"""
City Emergency Response Manager - Dijkstra's Algorithm for Route Calculation
===========================================================================
This module implements Dijkstra's algorithm to find the fastest emergency
response routes from HQ to any location or between any two locations in the city.
"""

import heapq
from emergency_graph import EmergencyGraph, create_sample_city


def dijkstra(graph, start_vertex):
    """
    Implement Dijkstra's algorithm to find shortest paths from a starting location
    to all other locations in the emergency zone.
    
    Args:
        graph (EmergencyGraph): The city emergency graph.
        start_vertex (str): The starting location.
        
    Returns:
        tuple: (distances, predecessors) where:
            - distances is a dict mapping each vertex to its shortest distance from start
            - predecessors is a dict mapping each vertex to its predecessor on shortest path
    """
    # Initialize all distances to infinity and predecessors to None
    distances = {vertex: float('infinity') for vertex in graph.get_all_vertices()}
    predecessors = {vertex: None for vertex in graph.get_all_vertices()}
    
    # Distance from start to itself is 0
    distances[start_vertex] = 0
    
    # Priority queue to track vertices to visit next
    # Format: (distance, vertex)
    priority_queue = [(0, start_vertex)]
    
    # Set to track visited vertices
    visited = set()
    
    while priority_queue:
        # Get vertex with smallest distance
        current_distance, current_vertex = heapq.heappop(priority_queue)
        
        # Skip if already visited (we found a shorter path before)
        if current_vertex in visited:
            continue
        
        # Mark as visited
        visited.add(current_vertex)
        
        # If current distance is greater than the known distance, skip
        if current_distance > distances[current_vertex]:
            continue
        
        # Check all neighbors
        for neighbor, weight in graph.get_neighbors(current_vertex).items():
            # Calculate potential new distance
            distance = current_distance + weight
            
            # If we found a shorter path, update
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                predecessors[neighbor] = current_vertex
                heapq.heappush(priority_queue, (distance, neighbor))
    
    return distances, predecessors


def get_shortest_path(graph, start_vertex, end_vertex):
    """
    Find the shortest path between two locations using Dijkstra's algorithm.
    
    Args:
        graph (EmergencyGraph): The city emergency graph.
        start_vertex (str): The starting location.
        end_vertex (str): The destination location.
        
    Returns:
        tuple: (path, total_time) where:
            - path is a list of locations to visit in order
            - total_time is the total travel time in minutes
    """
    # Calculate distances and predecessors
    distances, predecessors = dijkstra(graph, start_vertex)
    
    # If there's no path to the end vertex
    if distances[end_vertex] == float('infinity'):
        return [], float('infinity')
    
    # Reconstruct the path
    path = []
    current = end_vertex
    
    # Work backwards from end to start
    while current is not None:
        path.append(current)
        current = predecessors[current]
    
    # Reverse the path to get from start to end
    path.reverse()
    
    return path, distances[end_vertex]


def print_emergency_routes(city, start_location="HQ"):
    """
    Print the fastest route from a starting location (default: HQ) to all other locations.
    
    Args:
        city (EmergencyGraph): The city emergency graph.
        start_location (str, optional): The starting location. Defaults to "HQ".
    """
    print(f"\nEmergency Response Routes from {start_location}:")
    print("-" * 50)
    
    for location in city.get_all_vertices():
        if location != start_location:
            path, time = get_shortest_path(city, start_location, location)
            
            if time == float('infinity'):
                print(f"No route to {location}")
            else:
                route_str = " → ".join(path)
                print(f"To {location}: {route_str} (Time: {time} minutes)")


if __name__ == "__main__":
    # Create a sample city
    city = create_sample_city()
    
    # Calculate and print emergency routes from HQ
    print_emergency_routes(city)
    
    # You can also find routes between specific locations
    start, end = "A", "D"
    path, time = get_shortest_path(city, start, end)
    
    print(f"\nShortest path from {start} to {end}:")
    if time == float('infinity'):
        print(f"No route available")
    else:
        print(f"Route: {' → '.join(path)}")
        print(f"Response time: {time} minutes")