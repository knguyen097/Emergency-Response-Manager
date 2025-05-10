import tkinter as tk
from tkinter import ttk, messagebox
import math
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import random
from datetime import datetime, timedelta
from incident_scheduling import IncidentScheduler, Incident, Resource, IncidentType, Priority

# ─────────── Sorting (Merge Sort) ───────────
def merge_sort(lst, key=lambda x: x):
    if len(lst) <= 1:
        return lst
    mid   = len(lst) // 2
    left  = merge_sort(lst[:mid], key)
    right = merge_sort(lst[mid:], key)
    merged = []
    i = j = 0
    while i < len(left) and j < len(right):
        if key(left[i]) <= key(right[j]):
            merged.append(left[i]); i += 1
        else:
            merged.append(right[j]); j += 1
    merged.extend(left[i:])
    merged.extend(right[j:])
    return merged

# ─────────── Search (KMP) ───────────
def kmp_search(pattern, text):
    def compute_lps(pat):
        lps = [0] * len(pat)
        length = 0
        i = 1
        while i < len(pat):
            if pat[i] == pat[length]:
                length += 1
                lps[i] = length
                i += 1
            else:
                if length != 0:
                    length = lps[length - 1]
                else:
                    lps[i] = 0
                    i += 1
        return lps

    lps = compute_lps(pattern)
    i = j = 0
    while i < len(text):
        if pattern[j] == text[i]:
            i += 1; j += 1
            if j == len(pattern):
                return True
        else:
            if j != 0:
                j = lps[j - 1]
            else:
                i += 1
    return False
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
        style.configure("Time.TCombobox", fieldbackground='#003366',background='#003366', foreground="white", arrowcolor="black")
        style.map("Time.TCombobox",fieldbackground=[("readonly", '#003366')],background=[("readonly", '#003366')],foreground=[("!disabled", "white")])
        
        # Store incidents and tracking variables
        self.incidents = []
        self.completed_incidents = []
        self.current_routes = []
        
        # City graph initialization
        self.G = self.build_city_graph()
        self.initialize_resources(self.G)
        
        # Node options for locations
        self.node_labels = ['HQ', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I']
        
        # Priority colors
        self.priority_colors = {
            Priority.CRITICAL: "#ff0000",  # Red
            Priority.HIGH: "#ffa500",      # Orange
            Priority.MEDIUM: "#ffff00",    # Yellow
            Priority.LOW: "#00ff00",       # Green
            Priority.INFO: "#4287f5"       # Blue
        }
        
        # Fixed incident duration based on priority
        self.priority_durations = {
            Priority.CRITICAL: 120,  # 120 minutes for Critical
            Priority.HIGH: 90,       # 90 minutes for High
            Priority.MEDIUM: 60,     # 60 minutes for Medium
            Priority.LOW: 30,        # 30 minutes for Low
            Priority.INFO: 15        # 15 minutes for Info
        }

        # Define incident types with descriptions
        self.incident_types = {
            1: "Building Fire",           # Critical
            2: "Major Traffic Accident",  # High
            3: "Missing Pet",             # Medium
            4: "Water Main Break",        # Low
            5: "Hazardous Materials",     # Critical
            6: "Medical Emergency"        # Medium
        }
        
        # Resource combinations matching your test.py INCIDENTS
        self.incident_resource_options = [
            {'Fire Trucks': 1, 'Ambulances': 1, 'Police Cars': 0},
            {'Fire Trucks': 1, 'Ambulances': 0, 'Police Cars': 0},
            {'Fire Trucks': 0, 'Ambulances': 0, 'Police Cars': 1},
            {'Fire Trucks': 0, 'Ambulances': 1, 'Police Cars': 1},
            {'Fire Trucks': 2, 'Ambulances': 0, 'Police Cars': 0},
            {'Fire Trucks': 0, 'Ambulances': 1, 'Police Cars': 0}
        ]
        
        # Assign fixed priorities to each incident type
        self.incident_priorities = {
            1: Priority.CRITICAL,  # Building Fire
            2: Priority.HIGH,      # Major Traffic Accident
            3: Priority.LOW,       # Missing Pet
            4: Priority.MEDIUM,    # Water Main Break
            5: Priority.CRITICAL,  # Hazardous Materials
            6: Priority.MEDIUM     # Medical Emergency
        }
        
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
            G.nodes[n]['Ambulances'] = random.randint(0, 2)
            G.nodes[n]['Police Cars'] = random.randint(0, 2)
    
    def create_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="Emergency Response Manager", font=("Comic Sans MS", 22, "bold"))
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
        
        # Priority information display
        priority_frame = ttk.LabelFrame(control_frame, text="Incident Types", padding=10)
        priority_frame.pack(fill=tk.X, pady=5)

        for i, incident_type in self.incident_types.items():
            priority = self.incident_priorities[i]
            ttk.Label(
                priority_frame,
                text=f"{incident_type}: {priority.name} ({self.priority_durations[priority]} min)",
                foreground=self.priority_colors[priority]
            ).pack(anchor=tk.W)
        
        # Incident Selection Section
        incident_frame = ttk.Frame(control_frame)
        incident_frame.pack(fill=tk.X, pady=5)
        
        # Select incident
        ttk.Label(incident_frame, text="Select Incident Type:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.incident_var = tk.StringVar()
        self.incident_combo = ttk.Combobox(incident_frame, textvariable=self.incident_var, width=70)
        self.incident_combo.grid(row=0, column=1, pady=5, sticky=tk.W)
        
        # Location entry
        ttk.Label(incident_frame, text="Location:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.location_var = tk.StringVar()
        self.location_combo = ttk.Combobox(incident_frame, textvariable=self.location_var, width=50)
        self.location_combo.grid(row=1, column=1, pady=5, sticky=tk.W)
        
        # Time dropdown (HH:MM for hours 01–12)
        ttk.Label(incident_frame, text="Time (HH:MM):").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.time_var = tk.StringVar(value="12:00")
        time_options = [f"{h:02d}:00" for h in range(1, 13)]
        self.time_combo = ttk.Combobox(
            incident_frame,
            textvariable=self.time_var,
            values=time_options,
            width=10,
            state="readonly",
            style="Time.TCombobox"
        )
        self.time_combo.grid(row=2, column=1, pady=5, sticky=tk.W)

        # Button frame
        button_frame = ttk.Frame(incident_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=10)
        
        # Action buttons
        ttk.Button(button_frame, text="Add Incident", command=self.add_incident).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Remove Incident", command=self.remove_incident).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Clear All Incidents", command=self.clear_all_incidents).pack(side=tk.LEFT, padx=5)
        
        # Selected incidents section
        ttk.Label(control_frame, text="Selected Incidents:").pack(anchor=tk.W, pady=(10, 5))
        self.incident_list = tk.Listbox(control_frame, height=8, width=50, bg='#003366', fg='white')
        self.incident_list.pack(fill=tk.X, pady=5)
        
        # ─────────── Sort Incidents ───────────
        sort_frame = ttk.LabelFrame(control_frame, text="Sort Incidents", padding=10)
        sort_frame.pack(fill=tk.X, pady=5)
        ttk.Label(sort_frame, text="Sort By:").grid(row=0, column=0, sticky=tk.W)
        self.sort_var = tk.StringVar(value="Priority")
        self.sort_combo = ttk.Combobox(
            sort_frame,
            textvariable=self.sort_var,
            values=["Priority", "Time"],
            width=10,
            state="readonly",
            style="Time.TCombobox"
        )
        self.sort_combo.grid(row=0, column=1, sticky=tk.W)
        ttk.Button(sort_frame, text="Sort", command=self.sort_incidents).grid(row=0, column=2, padx=5)

        # ─────────── Search Logs ───────────
        search_frame = ttk.LabelFrame(control_frame, text="Incident Log Search", padding=10)
        search_frame.pack(fill=tk.X, pady=5)
        ttk.Label(search_frame, text="Keyword:").grid(row=0, column=0, sticky=tk.W)
        self.search_var   = tk.StringVar()
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        self.search_entry.grid(row=0, column=1, sticky=tk.W)
        ttk.Button(search_frame, text="Search", command=self.search_logs).grid(row=0, column=2, padx=5)
        
        # Optimize and Generate Log buttons
        ttk.Button(
            control_frame, 
            text="OPTIMIZE RESPONSE ROUTE",
            command=self.optimize_route, 
            style="Accent.TButton"
        ).pack(fill=tk.X, pady=10)
        
        ttk.Button(
            control_frame, 
            text="Generate Routes Log", 
            command=self.generate_routes_log
        ).pack(fill=tk.X, pady=10)
        
        # Optimized schedule section
        ttk.Label(control_frame, text="Optimized Response Plan:").pack(anchor=tk.W, pady=(10, 5))
        self.schedule_text = tk.Text(control_frame, height=15, width=50, bg='#003366', fg='white')
        self.schedule_text.pack(fill=tk.X, pady=5)
        
        # Initialize comboboxes
        self.update_comboboxes()
    
    def create_map_visualization(self, frame):
        self.fig, self.ax = plt.subplots(figsize=(8, 7), dpi=100, facecolor='#001f3f')
        self.ax.set_facecolor('#001f3f')
        
        # Store positions for later use
        self.pos = {n: ((self.node_labels.index(n) % 5) * 2, -(self.node_labels.index(n) // 5)) for n in self.G.nodes}
        self.labels = {n: f"{n}\nFT:{self.G.nodes[n]['Fire Trucks']} AMB:{self.G.nodes[n]['Ambulances']}\nPC:{self.G.nodes[n]['Police Cars']}" for n in self.G.nodes}
        
        # Draw the base graph
        self.draw_base_graph()
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(expand=True, fill='both')
    
    def draw_base_graph(self):
        """Draw the base graph without routes"""
        self.ax.clear()
        
        nx.draw(
            self.G, self.pos,
            labels=self.labels,
            node_size=6000,
            node_shape='s',
            node_color='#004080',
            edgecolors='white',
            font_size=12,
            font_color='white',
            ax=self.ax
        )
        nx.draw_networkx_edge_labels(
            self.G, self.pos,
            edge_labels=nx.get_edge_attributes(self.G, 'weight'),
            font_size=16,
            font_color='black',
            ax=self.ax
        )
        self.ax.margins(0.1)
        self.ax.axis('off')

    def update_comboboxes(self):
        # Format incident options to match resource combinations with priorities and descriptive names
        incident_options = [
            (f"{self.incident_types[i+1]} (Fire Trucks: "
             f"{res['Fire Trucks']}, Ambulances: {res['Ambulances']}, "
             f"Police Cars: {res['Police Cars']}) - {self.incident_priorities[i+1].name}")
            for i, res in enumerate(self.incident_resource_options)
        ]
        self.incident_combo['values'] = incident_options
        self.location_combo['values'] = self.node_labels

        # Auto-select first values if nothing is selected
        if not self.incident_var.get() and incident_options:
            self.incident_combo.current(0)

        if not self.location_var.get() and self.node_labels:
            self.location_combo.current(0)
    
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

        # Extract the incident type from the selection
        try:
            # Find which incident type we're dealing with
            incident_type_name = incident_option.split('(')[0].strip()

            # Find the incident type ID by name
            incident_index = next(i for i, name in self.incident_types.items() if name == incident_type_name) - 1

            resource_needs = self.get_resource_needs(incident_index)
            priority = self.incident_priorities[incident_index + 1]

            # Get the duration based on priority
            duration = self.priority_durations[priority]
        except (ValueError, IndexError, StopIteration) as e:
            messagebox.showwarning("Warning", f"Invalid incident selection: {str(e)}")
            return

        # Create incident entry for display with priority
        incident_entry = f"{incident_type_name} @ {location} ({time_str}) - {priority.name}"

        # Add incident to our list with priority and type name
        self.incidents.append({
            "type": incident_type_name,
            "type_id": incident_index + 1,
            "node": location,
            "time": incident_time,
            "needs": resource_needs,
            "priority": priority,
            "duration": duration
        })

        # Add to listbox with color coding
        self.incident_list.insert(tk.END, incident_entry)
        idx = self.incident_list.size() - 1
        self.incident_list.itemconfig(idx, {'fg': self.priority_colors[priority]})

        # Clear selection
        self.incident_var.set("")
        self.location_var.set("")
    
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
        self.clear_route_highlights()
    
    def shortest_path(self, src, dst):
        import heapq
        # Initialize distances and predecessors
        dist = {node: float('inf') for node in self.G.nodes()}
        prev = {node: None for node in self.G.nodes()}
        dist[src] = 0

        # Min-heap of (distance, node)
        heap = [(0, src)]
        visited = set()

        while heap:
            current_dist, u = heapq.heappop(heap)
            if u in visited:
                continue
            visited.add(u)
            # Early exit if we've reached the target
            if u == dst:
                break

            # Relax all neighbors
            for v, attrs in self.G[u].items():
                w = attrs.get('weight', 1)
                nd = current_dist + w
                if nd < dist[v]:
                    dist[v] = nd
                    prev[v] = u
                    heapq.heappush(heap, (nd, v))

        # Reconstruct path from src → dst
        path = []
        if dist[dst] < float('inf'):
            node = dst
            while node is not None:
                path.insert(0, node)
                node = prev[node]

        # Return (distance, path) 
        return dist[dst], path
    
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
    
    def highlight_routes(self, routes):
        """Highlight routes on the map"""
        # Clear previous routes
        self.clear_route_highlights()
        
        # Draw each route with a color based on priority
        for path, priority in routes:
            color = self.priority_colors[priority]
            
            # Create the edges list
            edges = [(path[i], path[i+1]) for i in range(len(path)-1)]
            
            # Draw edges with arrows
            nx.draw_networkx_edges(
                self.G, self.pos,
                edgelist=edges,
                width=5,
                edge_color=color,
                arrows=True,
                arrowstyle='-|>',
                arrowsize=20,
                ax=self.ax,
                alpha=0.7
            )
            
            # Add arrows indicating direction at midpoints of edges
            for i in range(len(path)-1):
                u, v = path[i], path[i+1]
                u_pos, v_pos = self.pos[u], self.pos[v]
                
                # Calculate midpoint
                mid_x = (u_pos[0] + v_pos[0]) / 2
                mid_y = (u_pos[1] + v_pos[1]) / 2
                
                # Add a small node at the midpoint to indicate direction
                self.ax.scatter(mid_x, mid_y, s=100, c=color, marker='>', zorder=5)
            
            # Store the current routes
            self.current_routes.append((edges, color))
        
        # Redraw the canvas
        self.canvas.draw()
    
    def clear_route_highlights(self):
        """Clear all route highlights"""
        if hasattr(self, 'ax'):
            # Redraw the base graph
            self.draw_base_graph()
            self.canvas.draw()
            
            # Clear stored routes
            self.current_routes = []
    
    def optimize_route(self):
        if not self.incidents:
            messagebox.showwarning("Warning", "No incidents to optimize.")
            return
        
        # Clear previous results
        self.schedule_text.delete(1.0, tk.END)
        self.clear_route_highlights()
        
        # Sort incidents by priority first, then by time
        sorted_incidents = sorted(
            self.incidents, 
            key=lambda x: (-x["priority"].value, x["time"])
        )
        
        # Create a copy of the graph for resource allocation
        G2 = self.build_city_graph()
        self.initialize_resources(G2)
        
        # Allocate resources
        alloc = self.allocate_resources(G2, [(inc["node"], inc["needs"]) for inc in sorted_incidents])
        
        # Track routes to highlight and log info
        total_time = 0
        locations_visited = set()
        routes_to_highlight = []
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Display header
        self.schedule_text.insert(tk.END, "Optimized Response Plan:\n\n")
        
        for i, incident in enumerate(sorted_incidents, 1):
            # Track current position for tagging
            line_start = self.schedule_text.index(tk.END)
            
            # Insert incident line with priority
            duration = incident.get('duration', self.priority_durations[incident['priority']])
            incident_text = f"{i}. {incident['type']} - {incident['priority'].name} Priority ({duration} min)\n"
            self.schedule_text.insert(tk.END, incident_text)
            
            # Apply color tag
            line_end = self.schedule_text.index(tk.END + "-1c")
            tag_name = f"priority_{i}"
            self.schedule_text.tag_configure(tag_name, foreground=self.priority_colors[incident['priority']])
            self.schedule_text.tag_add(tag_name, line_start, line_end)
            
            # Add incident details
            self.schedule_text.insert(tk.END, f"   Location: {incident['node']}\n")
            self.schedule_text.insert(tk.END, f"   Time: {incident['time'].strftime('%H:%M')}\n")
            
            # Calculate estimated completion time
            completion_time = incident['time'] + timedelta(minutes=duration)
            self.schedule_text.insert(tk.END, f"   Est. Completion: {completion_time.strftime('%H:%M')}\n")
            
            self.schedule_text.insert(tk.END, "   Resources:\n")
            
            # Create incident log entry
            incident_log = {
                "id": f"INC-{len(self.completed_incidents) + 1:03d}",
                "type": incident['type'],
                "node": incident['node'],
                "time": incident['time'],
                "priority": incident['priority'],
                "duration": duration,
                "completion_time": completion_time,
                "timestamp": timestamp,
                "resources": []
            }
            
            locations_visited.add(incident['node'])
            
            # Process each resource allocation
            for r, src, d in alloc[incident['node']]:
                if src:
                    self.schedule_text.insert(tk.END, f"     {r} from {src} ({d}min)\n")
                    total_time += d
                    locations_visited.add(src)
                    
                    # Add to resource log
                    incident_log["resources"].append({
                        "type": r,
                        "source": src,
                        "time": d
                    })
                    
                    # Add route to highlight
                    path = nx.shortest_path(self.G, src, incident['node'], weight='weight')
                    routes_to_highlight.append((path, incident['priority']))
                else:
                    self.schedule_text.insert(tk.END, f"     No {r} available\n")
            
            self.schedule_text.insert(tk.END, "\n")
            
            # Add to completed incidents log
            self.completed_incidents.append(incident_log)
        
        # Add summary
        self.schedule_text.insert(tk.END, f"Summary:\n")
        self.schedule_text.insert(tk.END, f"Number of incidents: {len(sorted_incidents)}\n")
        self.schedule_text.insert(tk.END, f"Number of locations: {len(locations_visited)}\n")
        self.schedule_text.insert(tk.END, f"Total response time: {total_time} minutes\n")
        
        # Highlight routes on the map
        self.highlight_routes(routes_to_highlight)
    
    def generate_routes_log(self):
        """Generate log of all routed incidents"""
        if not self.completed_incidents:
            messagebox.showinfo("Info", "No incidents have been routed yet.")
            return
        
        # Create log window
        log_window = tk.Toplevel(self.root)
        log_window.title("Routes Log")
        log_window.geometry("700x500")
        log_window.configure(bg='#001f3f')
        
        # Create log frame
        log_frame = ttk.Frame(log_window, padding=10)
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create text widget for log
        log_text = tk.Text(log_frame, width=80, height=30, bg='#003366', fg='white')
        log_text.pack(fill=tk.BOTH, expand=True)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(log_text, command=log_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        log_text.config(yscrollcommand=scrollbar.set)
        
        # Insert log header
        log_text.insert(tk.END, "===== EMERGENCY RESPONSE ROUTES LOG =====\n\n")
        
        # Group by optimization batch
        by_timestamp = {}
        for incident in self.completed_incidents:
            timestamp = incident["timestamp"]
            if timestamp not in by_timestamp:
                by_timestamp[timestamp] = []
            by_timestamp[timestamp].append(incident)
        
        # Process each batch
        for timestamp, incidents in by_timestamp.items():
            log_text.insert(tk.END, f"=== Batch: {timestamp} ===\n")
            log_text.insert(tk.END, f"Number of Incidents: {len(incidents)}\n\n")
            
            # Track batch statistics
            total_routes = 0
            total_time = 0
            all_routes = []
            
            # Process each incident
            for incident in incidents:
                # Set priority tag
                priority_tag = f"priority_{incident['priority'].name}"
                log_text.tag_configure(priority_tag, foreground=self.priority_colors[incident['priority']])
                
                # Insert incident details
                log_text.insert(tk.END, f"Incident: {incident['id']}\n")
                log_text.insert(tk.END, f"Type: {incident['type']}\n")
                log_text.insert(tk.END, f"Location: {incident['node']}\n")
                log_text.insert(tk.END, f"Time: {incident['time'].strftime('%H:%M')}\n")
                
                # Add completion time if available
                if 'completion_time' in incident:
                    log_text.insert(tk.END, f"Est. Completion: {incident['completion_time'].strftime('%H:%M')}\n")
                
                # Insert priority with color
                log_text.insert(tk.END, "Priority: ")
                log_text.insert(tk.END, f"{incident['priority'].name}", priority_tag)
                log_text.insert(tk.END, f" ({incident.get('duration', 0)} min)\n")
                
                # Insert routes
                log_text.insert(tk.END, "Routes:\n")
                
                # Process resources/routes
                incident_time = 0
                if incident['resources']:
                    for resource in incident['resources']:
                        route_str = f"  {resource['type']} from {resource['source']} to {incident['node']} ({resource['time']}min)"
                        log_text.insert(tk.END, f"{route_str}\n")
                        
                        incident_time += resource['time']
                        total_time += resource['time']
                        total_routes += 1
                        
                        all_routes.append(f"{resource['source']} → {incident['node']}")
                    
                    log_text.insert(tk.END, f"Total Route Time: {incident_time} minutes\n")
                else:
                    log_text.insert(tk.END, "  No resources allocated\n")
                
                log_text.insert(tk.END, "\n")
            
            # Add batch summary
            log_text.insert(tk.END, "Batch Summary:\n")
            log_text.insert(tk.END, f"Total Routes: {total_routes}\n")
            log_text.insert(tk.END, f"Total Travel Time: {total_time} minutes\n")
            if all_routes:
                log_text.insert(tk.END, f"Routes: {', '.join(all_routes)}\n")
            log_text.insert(tk.END, "\n\n")
        
        # Make text read-only
        log_text.config(state=tk.DISABLED)
        
        # Add export button
        export_frame = ttk.Frame(log_window)
        export_frame.pack(fill=tk.X, pady=10)
        
        def export_log():
            try:
                # Create logs directory if needed
                import os
                if not os.path.exists("logs"):
                    os.makedirs("logs")
                
                # Create log file with timestamp
                filename = f"logs/routes_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                
                with open(filename, "w") as f:
                    f.write(log_text.get("1.0", tk.END))
                
                messagebox.showinfo("Export Successful", f"Log exported to {filename}")
            except Exception as e:
                messagebox.showerror("Export Failed", f"Error exporting log: {str(e)}")
        
        ttk.Button(export_frame, text="Export Log", command=export_log).pack(side=tk.RIGHT, padx=10)

    def sort_incidents(self):
        # choose key
        if self.sort_var.get() == "Priority":
            key = lambda inc: -inc["priority"].value
        else:
            key = lambda inc: inc["time"]
        # sort & refresh listbox
        self.incidents = merge_sort(self.incidents, key=key)
        self.incident_list.delete(0, tk.END)
        for inc in self.incidents:
            txt = f"{inc['type']} @ {inc['node']} ({inc['time'].strftime('%H:%M')})"
            self.incident_list.insert(tk.END, txt)
            self.incident_list.itemconfig(
                tk.END, {'fg': self.priority_colors[inc['priority']]}
            )

    def search_logs(self):
        kw = self.search_var.get().strip().lower()
        if not kw:
            messagebox.showwarning("Warning", "Enter a keyword to search.")
            return
        matches = []
        for inc in self.completed_incidents:
            hay = f"{inc['type']} {inc['node']} {inc['priority'].name}".lower()
            if kmp_search(kw, hay):
                matches.append(inc)
        # popup results
        win = tk.Toplevel(self.root)
        win.title(f"Search: '{kw}'")
        txt = tk.Text(win, bg='#003366', fg='white')
        txt.pack(fill=tk.BOTH, expand=True)
        if not matches:
            txt.insert(tk.END, "No matches found.")
        else:
            for m in matches:
                txt.insert(tk.END,
                    f"Type: {m['type']}\n"
                    f"Loc:  {m['node']}\n"
                    f"Prio: {m['priority'].name}\n"
                    f"Time: {m['time'].strftime('%H:%M')}\n\n"
                )
        txt.config(state=tk.DISABLED)

if __name__ == "__main__":
    root = tk.Tk()
    app = EmergencyResponseManager(root)
    root.mainloop()