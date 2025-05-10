import tkinter as tk
from tkinter import ttk, messagebox
import math
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import random
from datetime import datetime, timedelta

class EmergencyResponseManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Emergency Response Manager")
        self.root.geometry("1000x800")
        self.root.configure(bg='#001f3f')
        
        # Style
        style = ttk.Style(self.root)
        style.theme_use('clam')
        font_name = 'Comic Sans MS'  

        # Style configurations
        style.configure('TLabelframe', background='#001f3f', borderwidth=0, relief='flat')
        style.configure('TLabelframe.Label', background='#001f3f', foreground='white', font=(font_name, 16))
        style.configure('TFrame', background='#001f3f')
        style.configure('TButton', font=(font_name, 12), relief='ridge', padding=6,
                        background='#004080', foreground='white')
        style.map('TButton', background=[('active', '#0059b3')])
        style.configure('TLabel', background='#001f3f', foreground='white', font=(font_name, 12))
        style.configure('TCombobox', fieldbackground='#003366', background='#003366',
                        foreground='white', font=(font_name, 12))
        style.configure('Accent.TButton', font=(font_name, 14, "bold"))
        
        # Store incidents
        self.incidents = []
        
        # City graph initialization
        self.G = self.build_city_graph()
        self.initialize_resources(self.G)
        
        # Node options for locations
        self.node_labels = ['HQ', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I']
        
        # Resource combinations matching your test.py INCIDENTS
        self.incident_resource_options = [
            {'Fire Trucks': 1, 'Ambulances': 1, 'Police Cars': 0},
            {'Fire Trucks': 1, 'Ambulances': 0, 'Police Cars': 0},
            {'Fire Trucks': 0, 'Ambulances': 0, 'Police Cars': 1},
            {'Fire Trucks': 0, 'Ambulances': 1, 'Police Cars': 1},
            {'Fire Trucks': 2, 'Ambulances': 0, 'Police Cars': 0},
            {'Fire Trucks': 0, 'Ambulances': 1, 'Police Cars': 0}
        ]
        
        # Create UI components
        self.create_ui()
        
    def build_city_graph(self, rows=2, cols=5):
        random.seed(42)
        G = nx.grid_2d_graph(rows, cols)

        mapping, idx = {}, 0
        node_labels = ['HQ', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I']
        for r in range(rows):
            for c in range(cols):
                mapping[(r, c)] = node_labels[idx]
                idx += 1
        G = nx.relabel_nodes(G, mapping)

        # Assigns a random travel time between 5 and 60 minutes
        for u, v in G.edges():
            G.edges[u, v]['weight'] = random.randint(5, 60)

        return G

    def initialize_resources(self, G):
        for n in G.nodes:
            G.nodes[n]['Fire Trucks'] = random.randint(0, 2)
            G.nodes[n]['Ambulances'] = random.randint(0, 1)
            G.nodes[n]['Police Cars'] = random.randint(0, 1)
    
    def create_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="Emergency Response Manager", font=("Arial", 18, "bold"))
        title_label.pack(pady=10)
        
        # Create a frame that will contain both the map and the controls
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left side - Map
        map_frame = ttk.LabelFrame(content_frame, text="Resource Map", padding=10)
        map_frame.grid(row=0, column=0, rowspan=2, padx=10, pady=10, sticky="nsew")
        
        # Create the map visualization
        self.create_map_visualization(map_frame)
        
        # Right side - Controls
        control_frame = ttk.LabelFrame(content_frame, text="Incident Management", padding=10)
        control_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        
        # Configure grid weights
        content_frame.columnconfigure(0, weight=3)  # Map takes more space
        content_frame.columnconfigure(1, weight=2)  # Controls take less space
        content_frame.rowconfigure(0, weight=1)
        
        # Incident Selection Section
        incident_frame = ttk.Frame(control_frame)
        incident_frame.pack(fill=tk.X, pady=5)
        
        # Select incident
        ttk.Label(incident_frame, text="Select Incident Type:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.incident_var = tk.StringVar()
        self.incident_combo = ttk.Combobox(incident_frame, textvariable=self.incident_var, width=50)
        self.incident_combo.grid(row=0, column=1, pady=5, sticky=tk.W)
        
        # Location entry
        ttk.Label(incident_frame, text="Location:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.location_var = tk.StringVar()
        self.location_combo = ttk.Combobox(incident_frame, textvariable=self.location_var, width=50)
        self.location_combo.grid(row=1, column=1, pady=5, sticky=tk.W)
        
        # Time entry
        ttk.Label(incident_frame, text="Time (HH:MM):").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.time_var = tk.StringVar(value="12:00")
        time_entry = ttk.Entry(incident_frame, textvariable=self.time_var, width=10)
        time_entry.grid(row=2, column=1, pady=5, sticky=tk.W)
        
        # Button frame
        button_frame = ttk.Frame(incident_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=10)
        
        # Action buttons
        ttk.Button(button_frame, text="Add Incident", command=self.add_incident).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Create New Incident", command=self.create_new_incident).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Remove Incident", command=self.remove_incident).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Clear All Incidents", command=self.clear_all_incidents).pack(side=tk.LEFT, padx=5)
        
        # Selected incidents section
        ttk.Label(control_frame, text="Selected Incidents:").pack(anchor=tk.W, pady=(10, 5))
        self.incident_list = tk.Listbox(control_frame, height=8, width=50, bg='#003366', fg='white')
        self.incident_list.pack(fill=tk.X, pady=5)
        
        # Optimize button
        ttk.Button(control_frame, text="Optimize Response Route", 
                   command=self.optimize_route, style="Accent.TButton").pack(fill=tk.X, pady=10)
        
        # Optimized schedule section
        ttk.Label(control_frame, text="Optimized Response Plan:").pack(anchor=tk.W, pady=(10, 5))
        self.schedule_text = tk.Text(control_frame, height=10, width=50, bg='#003366', fg='white')
        self.schedule_text.pack(fill=tk.X, pady=5)
        
        # Route information section
        ttk.Label(control_frame, text="Route Information:").pack(anchor=tk.W, pady=(10, 5))
        self.route_text = tk.Text(control_frame, height=5, width=50, bg='#003366', fg='white')
        self.route_text.pack(fill=tk.X, pady=5)
        
        # Initialize comboboxes
        self.update_comboboxes()
    
    def create_map_visualization(self, frame):
        fig, ax = plt.subplots(figsize=(8, 7), dpi=100, facecolor='#001f3f')
        ax.set_facecolor('#001f3f')
        
        pos = {n: ((self.node_labels.index(n) % 5) * 2, -(self.node_labels.index(n) // 5)) for n in self.G.nodes}
        labels = {n: f"{n}\nFT:{self.G.nodes[n]['Fire Trucks']} AMB:{self.G.nodes[n]['Ambulances']}\nPC:{self.G.nodes[n]['Police Cars']}" for n in self.G.nodes}
        
        nx.draw(
            self.G, pos,
            labels=labels,
            node_size=9000,
            node_shape='s',
            node_color='#004080',
            edgecolors='white',
            font_size=12,
            font_color='white',
            ax=ax
        )
        nx.draw_networkx_edge_labels(
            self.G, pos,
            edge_labels=nx.get_edge_attributes(self.G, 'weight'),
            font_size=16,
            font_color='yellow',
            ax=ax
        )
        ax.margins(0.1)
        ax.axis('off')
        self.canvas = FigureCanvasTkAgg(fig, master=frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(expand=True, fill='both')
    
    def update_comboboxes(self):
        # Format incident options to match resource combinations
        incident_options = [
            f"Incident {i+1} (Fire Trucks: {res['Fire Trucks']}, Ambulances: {res['Ambulances']}, Police Cars: {res['Police Cars']})"
            for i, res in enumerate(self.incident_resource_options)
        ]
        self.incident_combo['values'] = incident_options
        self.location_combo['values'] = self.node_labels
    
    def get_resource_needs(self, incident_index):
        # Get the resource needs directly from our predefined options
        if 0 <= incident_index < len(self.incident_resource_options):
            return self.incident_resource_options[incident_index]
        return {'Fire Trucks': 0, 'Ambulances': 0, 'Police Cars': 0}
    
    def add_incident(self):
        incident_option = self.incident_var.get()
        location = self.location_var.get()
        time_str = self.time_var.get()
        
        if not incident_option or not location:
            messagebox.showwarning("Warning", "Please select both an incident type and location.")
            return
        
        # Parse the time
        try:
            hours, minutes = map(int, time_str.split(":"))
            incident_time = datetime.now().replace(hour=hours, minute=minutes)
        except ValueError:
            messagebox.showwarning("Warning", "Invalid time format. Please use HH:MM.")
            return
        
        # Extract the incident index from the selection
        try:
            incident_index = int(incident_option.split()[1][0]) - 1  # Extract from "Incident X"
            resource_needs = self.get_resource_needs(incident_index)
        except (ValueError, IndexError):
            messagebox.showwarning("Warning", "Invalid incident selection.")
            return
        
        # Create incident entry for display
        incident_entry = f"{incident_option.split('(')[0].strip()} @ {location} ({time_str})"
        
        # Add incident to our list
        self.incidents.append({
            "type": f"Incident {incident_index + 1}",
            "node": location,
            "time": incident_time,
            "needs": resource_needs
        })
        
        # Add to listbox
        self.incident_list.insert(tk.END, incident_entry)
        
        # Clear selection
        self.incident_var.set("")
        self.location_var.set("")
    
    def create_new_incident(self):
        # In a real application, this would open a dialog to create a custom resource combination
        messagebox.showinfo("Info", "This would open a dialog to create a custom incident with resource needs.")
    
    def remove_incident(self):
        try:
            selected_idx = self.incident_list.curselection()[0]
            self.incident_list.delete(selected_idx)
            self.incidents.pop(selected_idx)
        except IndexError:
            messagebox.showwarning("Warning", "Please select an incident to remove.")
    
    def clear_all_incidents(self):
        self.incident_list.delete(0, tk.END)
        self.incidents.clear()
        self.schedule_text.delete(1.0, tk.END)
        self.route_text.delete(1.0, tk.END)
    
    def shortest_path(self, src, dst):
        return nx.single_source_dijkstra(self.G, src, dst, weight='weight')
    
    def allocate_resources(self, G, incidents):
        assigns = {}
        for node, needs in incidents:
            assigns[node] = []
            for rtype, count in needs.items():
                for _ in range(count):
                    best_node, best_d = None, float('inf')
                    for cand in G.nodes:
                        if G.nodes[cand][rtype] > 0:
                            d, _ = self.shortest_path(cand, node)
                            if d < best_d:
                                best_d, best_node = d, cand
                    if best_node:
                        assigns[node].append((rtype, best_node, best_d))
                        G.nodes[best_node][rtype] -= 1
                    else:
                        assigns[node].append((rtype, None, None))
        return assigns
    
    def optimize_route(self):
        if not self.incidents:
            messagebox.showwarning("Warning", "No incidents to optimize.")
            return
        
        # Clear previous results
        self.schedule_text.delete(1.0, tk.END)
        self.route_text.delete(1.0, tk.END)
        
        # Sort incidents by time
        sorted_incidents = sorted(self.incidents, key=lambda x: x["time"])
        
        # Create a copy of the graph for resource allocation
        G2 = self.build_city_graph()
        self.initialize_resources(G2)
        
        # Allocate resources
        alloc = self.allocate_resources(G2, [(inc["node"], inc["needs"]) for inc in sorted_incidents])
        
        # Calculate total travel time and unique locations
        total_time = 0
        locations_visited = set()
        
        # Display optimized schedule
        self.schedule_text.insert(tk.END, "Optimized Response Plan:\n\n")
        
        for i, incident in enumerate(sorted_incidents, 1):
            self.schedule_text.insert(tk.END, f"{i}. {incident['type']}\n")
            self.schedule_text.insert(tk.END, f"   Location: {incident['node']}\n")
            self.schedule_text.insert(tk.END, f"   Time: {incident['time'].strftime('%H:%M')}\n")
            self.schedule_text.insert(tk.END, "   Resources:\n")
            
            locations_visited.add(incident['node'])
            
            for r, src, d in alloc[incident['node']]:
                if src:
                    self.schedule_text.insert(tk.END, f"     {r} from {src} ({d}min)\n")
                    total_time += d
                    locations_visited.add(src)
                else:
                    self.schedule_text.insert(tk.END, f"     No {r} available\n")
            
            self.schedule_text.insert(tk.END, "\n")
        
        # Display route information
        self.route_text.insert(tk.END, f"Route Information:\n")
        self.route_text.insert(tk.END, f"Number of incidents: {len(sorted_incidents)}\n")
        self.route_text.insert(tk.END, f"Number of locations: {len(locations_visited)}\n")
        self.route_text.insert(tk.END, f"Total response time: {total_time} minutes")

if __name__ == "__main__":
    root = tk.Tk()
    app = EmergencyResponseManager(root)
    root.mainloop()
