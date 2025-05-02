"""
City Emergency Response Manager - Graph Model
===========================================
This module defines the city emergency zone graph structure with nodes
representing locations and edges representing routes between locations.

Each edge has a weight representing travel time in minutes.
"""

class EmergencyGraph:
    """
    A graph representation of emergency zones in a city.
    
    Attributes:
        vertices (list): List of all locations in the city.
        edges (dict): Dictionary mapping vertices to their neighbors with edge weights.
    """
    
    def __init__(self):
        """Initialize an empty graph."""
        self.vertices = []
        self.edges = {}
    
    def add_vertex(self, vertex):
        """
        Add a new location to the emergency zone graph.
        
        Args:
            vertex (str): The name of the location to add.
        """
        if vertex not in self.vertices:
            self.vertices.append(vertex)
            self.edges[vertex] = {}
    
    def add_edge(self, source, destination, weight):
        """
        Add a route between two locations with a specified travel time.
        
        Args:
            source (str): Starting location.
            destination (str): Ending location.
            weight (float): Travel time in minutes between locations.
        """
        # Add vertices if they don't exist
        if source not in self.vertices:
            self.add_vertex(source)
        if destination not in self.vertices:
            self.add_vertex(destination)
        
        # Add edges (bidirectional by default for city streets)
        self.edges[source][destination] = weight
        self.edges[destination][source] = weight
    
    def get_neighbors(self, vertex):
        """
        Get all neighboring locations and travel times from a given location.
        
        Args:
            vertex (str): The location to get neighbors for.
            
        Returns:
            dict: A dictionary of neighboring locations and their travel times.
        """
        if vertex in self.edges:
            return self.edges[vertex]
        return {}
    
    def get_all_vertices(self):
        """
        Get all locations in the emergency zone.
        
        Returns:
            list: All locations in the city graph.
        """
        return self.vertices
    
    def __str__(self):
        """
        Return a string representation of the graph.
        
        Returns:
            str: A multi-line string showing the graph structure.
        """
        result = "City Emergency Graph:\n"
        for vertex in self.vertices:
            result += f"{vertex} -> {self.edges[vertex]}\n"
        return result


def create_sample_city():
    """
    Create a sample city graph with HQ and locations A, B, C, D.
    
    Returns:
        EmergencyGraph: A sample graph of a city with emergency response locations.
    """
    city = EmergencyGraph()
    
    # Add all locations
    city.add_vertex("HQ")
    city.add_vertex("A")
    city.add_vertex("B")
    city.add_vertex("C")
    city.add_vertex("D")
    
    # Add routes between locations with travel times in minutes
    city.add_edge("HQ", "A", 5)    # 5 minutes from HQ to A
    city.add_edge("HQ", "B", 10)   # 10 minutes from HQ to B
    city.add_edge("A", "B", 3)     # 3 minutes from A to B
    city.add_edge("A", "C", 8)     # 8 minutes from A to C
    city.add_edge("B", "C", 6)     # 6 minutes from B to C
    city.add_edge("B", "D", 7)     # 7 minutes from B to D
    city.add_edge("C", "D", 4)     # 4 minutes from C to D
    
    return city


if __name__ == "__main__":
    # Test the graph creation
    test_city = create_sample_city()
    print(test_city)