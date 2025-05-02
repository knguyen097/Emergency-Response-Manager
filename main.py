from emergency_graph import EmergencyGraph, create_sample_city, visualize_graph
from emergency_routes import get_shortest_path, print_emergency_routes

def main():
    print("City Emergency Response Manager - Demo")
    print("======================================")
    
    # Create a sample city graph
    city = create_sample_city()
    
    # Print the city graph structure
    print("\nCity Graph Structure:")
    print(city)
    
    # Print all emergency routes from HQ
    print_emergency_routes(city)
    
    # Allow custom route calculations
    print("\nCustom Route Calculation:")
    print("-" * 50)\
    
    # List all available locations
    locations = city.get_all_vertices()
    print(f"Available locations: {', '.join(locations)}")
    
    start = input("\nEnter starting location (or press Enter for HQ): ").strip() or "HQ"
    if start not in locations:
        print(f"Location '{start}' doesn't exist. Using HQ instead.")
        start = "HQ"
    
    end = input("Enter destination location: ").strip()
    if end not in locations:
        print(f"Location '{end}' doesn't exist. Using D instead.")
        end = "D"
    
    # Calculate and show the route
    path, time = get_shortest_path(city, start, end)
    
    print("\nResults:")
    if time == float('infinity'):
        print(f"No route available from {start} to {end}")
    else:
        print(f"Fastest route from {start} to {end}:")
        print(f"Route: {' → '.join(path)}")
        print(f"Estimated response time: {time} minutes")
        
    city = create_sample_city()
    print("\nCity Graph Structure:")
    print(city)

    # 1) Visualize the city map
    visualize_graph(city)

    # 2) Demo emergency routes
    print_emergency_routes(city)

    # 3) Incident Options
    sample_incidents = [
        (1, 4, "Fire at A"),
        (3, 5, "Accident on B–C road"),
        (0, 6, "Medical emergency at HQ"),
        (5, 7, "Gas leak at D"),
        (8, 11, "Flooding at C"),
        (5, 9, "Structural collapse at B"),
    ]
    
if __name__ == "__main__":
    main()