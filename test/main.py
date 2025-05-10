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
        
        # Optimize button
        ttk.Button(control_frame, text="Optimize Response Route", 
                   command=self.optimize_route, style="Accent.TButton").pack(fill=tk.X, pady=10)
        
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
            ax=ax
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
        for inc in act_sched:
            st = inc.time.strftime("%H:%M")
            et = (inc.time + timedelta(minutes=inc.estimated_duration)).strftime("%H:%M")
            self.schedule_text.insert(
                tk.END,
                f"    {inc.id}: {inc.location} | {st}–{et} | Priority {inc.priority.name}\n"
            )

        # 5. Route summary 
        total_time = sum(d for _, _, d in alloc.values() for d in [d] if d)
        locations_visited = {inc["node"] for inc in sorted_incidents}
        self.route_text.insert(tk.END, f"Route Information:\n")
        self.route_text.insert(tk.END, f"  Incidents: {len(sorted_incidents)}\n")
        self.route_text.insert(tk.END, f"  Locations: {len(locations_visited)}\n")
        self.route_text.insert(tk.END, f"  Total response time: {total_time} minutes\n")

        
    def _show_mst(self):
        T = nx.minimum_spanning_tree(self.G, weight='weight')
        
        fig, ax = plt.subplots()
        pos = nx.get_node_attributes(self, 'pos')  
        nx.draw_networkx_nodes(T, pos, node_size=300, ax=ax)
        nx.draw_networkx_labels(T, pos, ax=ax)
        nx.draw_networkx_edges(T, pos, edgelist=T.edges(), width=2, edge_color='red', ax=ax)
        self.canvas.figure = fig
        self.canvas.draw()
    
    def _schedule_activity(self):
        sched = IncidentScheduler()
        sched.incidents = self.incidents             
        chosen = sched.activity_selection_greedy(sched.incidents)
        self._display_schedule(chosen, title="Activity-Selection Schedule")

    
    def _display_schedule(self, incidents, title="Schedule"):
        dlg = tk.Toplevel(self.root)
        dlg.title(title)
        txt = tk.Text(dlg, width=50, height=15)
        for inc in incidents:
            st = inc.time.strftime("%H:%M")
            et = (inc.time + timedelta(minutes=inc.estimated_duration)).strftime("%H:%M")
            txt.insert(tk.END, f"{inc.id} | {inc.priority.name:<8} | {st}–{et} | {inc.location}\n")
        txt.pack(padx=10, pady=10)

    def _sort_incidents(self, by="priority", algo="merge"):
        sched = IncidentScheduler()
        sched.incidents = self.incidents
        if by == "priority":
            sorted_list = sched.sort_by_priority(algo)
        elif by == "time":
            sorted_list = sched.sort_by_time(algo)
        else:
            sorted_list = sched.sort_by_location(algo)
        self._display_schedule(sorted_list, title=f"Sorted by {by.title()} ({algo})")

if __name__ == "__main__":
    root = tk.Tk()
    app = EmergencyResponseManager(root)
    root.mainloop()
