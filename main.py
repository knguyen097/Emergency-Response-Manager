from emergency_graph import EmergencyGraph, create_sample_city
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
    print("-" * 50)
    
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


if __name__ == "__main__":
    main()