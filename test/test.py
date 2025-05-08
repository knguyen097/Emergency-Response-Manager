import networkx as nx
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import ttk, messagebox
import random
from datetime import datetime, timedelta
import heapq
from collections import Counter, namedtuple

# -----------------------------------------------------------------------------
# City Emergency Response and Resource Manager
# A single-file application to visualize resources, handle incidents,
# and maintain a log with optional Huffman compression.
# -----------------------------------------------------------------------------

# Log file paths
LOG_FILE         = 'incident_log.txt'
COMPRESSED_FILE  = 'incident_log.huff'
CODEBOOK_FILE    = 'incident_log_codebook.txt'

# Pre-defined incidents with timestamps and resource needs
INCIDENTS = [
    {'id':'I1','node':'B','time':datetime(2025,5,4,8,0),
     'needs':{'fire_trucks':1,'ambulances':1,'police_cars':0}},
    {'id':'I2','node':'D','time':datetime(2025,5,4,14,30),
     'needs':{'fire_trucks':1,'ambulances':0,'police_cars':0}},
    {'id':'I3','node':'F','time':datetime(2025,5,4,20,45),
     'needs':{'fire_trucks':0,'ambulances':0,'police_cars':1}},
    {'id':'I4','node':'A','time':datetime(2025,5,5,2,0),
     'needs':{'fire_trucks':0,'ambulances':1,'police_cars':1}},
    {'id':'I5','node':'I','time':datetime(2025,5,5,10,15),
     'needs':{'fire_trucks':2,'ambulances':0,'police_cars':0}},
    {'id':'I6','node':'H','time':datetime(2025,5,5,18,0),
     'needs':{'fire_trucks':0,'ambulances':1,'police_cars':0}},
]

# Node labels for the 2x5 grid layout
NODE_LABELS = ['HQ','A','B','C','D','E','F','G','H','I']

# -----------------------------------------------------------------------------
# Graph & Resource Initialization
# -----------------------------------------------------------------------------

def build_city_graph(rows=2, cols=5):
    """
    Creates a 2x5 grid graph and relabels nodes to HQ, A-I.
    Edges have a uniform travel-time weight of 1.
    """
    G = nx.grid_2d_graph(rows, cols)
    mapping = {}
    idx = 0
    # Map grid coordinates to human-friendly labels
    for r in range(rows):
        for c in range(cols):
            mapping[(r,c)] = NODE_LABELS[idx]
            idx += 1
    G = nx.relabel_nodes(G, mapping)
    # Assign weight to each edge
    for u, v in G.edges():
        G.edges[u, v]['weight'] = 1
    return G


def initialize_resources(G):
    """
    Randomly assigns a small fleet of fire trucks, ambulances,
    and police cars to each node in the graph.
    """
    random.seed(42)  # for reproducible results
    for node in G.nodes:
        G.nodes[node]['fire_trucks'] = random.randint(0, 2)
        G.nodes[node]['ambulances']  = random.randint(0, 1)
        G.nodes[node]['police_cars'] = random.randint(0, 1)

# -----------------------------------------------------------------------------
# Visualization of the Grid with Resources
# -----------------------------------------------------------------------------

def visualize_graph(G, path=None):
    """
    Draws the resource grid. Nodes are square and large enough
    to display multi-line labels with resource counts.

    Optionally highlights a path in red.
    """
    # Compute positions based on label index for neat layout
    pos = {
        node: (NODE_LABELS.index(node) % 5,
               -(NODE_LABELS.index(node)//5))
        for node in G.nodes
    }
    # Build multi-line labels: name and resource counts
    labels = {
        node: f"{node}\n"
              f"FT:{G.nodes[node]['fire_trucks']}  "
              f"AMB:{G.nodes[node]['ambulances']}\n"
              f"PC:{G.nodes[node]['police_cars']}"
        for node in G.nodes
    }
    # Draw nodes and edges
    nx.draw(G, pos,
            labels=labels,
            node_size=3200,
            font_size=8,
            node_shape='s',
            linewidths=1,
            edgecolors='black')
    # Draw edge weights
    nx.draw_networkx_edge_labels(
        G, pos,
        edge_labels=nx.get_edge_attributes(G, 'weight'),
        font_size=6)

    # Highlight a specific path if provided
    if path:
        edge_list = list(zip(path, path[1:]))
        nx.draw_networkx_edges(
            G, pos,
            edgelist=edge_list,
            width=3,
            edge_color='r')

    plt.axis('off')
    plt.show()

# -----------------------------------------------------------------------------
# Routing and Allocation Logic
# -----------------------------------------------------------------------------

def shortest_path(G, source, target):
    """
    Returns the shortest path and distance between two nodes
    using Dijkstra's algorithm.
    """
    distance, path = nx.single_source_dijkstra(
        G, source, target, weight='weight')
    return distance, path


def allocate_resources(G, incidents):
    """
    Attempts to assign the nearest available unit of each requested type
    to every incident in the provided list. Deducts resources as used.
    """
    assignments = {}
    for inc_id, node, needs in incidents:
        assignments[inc_id] = []
        # For each resource type and required count
        for rtype, count in needs.items():
            for _ in range(count):
                best_node = None
                best_dist = float('inf')
                # Search every graph node for availability
                for candidate in G.nodes:
                    if G.nodes[candidate][rtype] > 0:
                        dist, _ = shortest_path(G, candidate, node)
                        if dist < best_dist:
                            best_dist, best_node = dist, candidate
                if best_node is None:
                    assignments[inc_id].append((rtype, None, None))
                else:
                    assignments[inc_id].append((rtype, best_node, best_dist))
                    # Decrement the resource count at that node
                    G.nodes[best_node][rtype] -= 1
    return assignments

# -----------------------------------------------------------------------------
# Huffman Coding for Log Compression
# -----------------------------------------------------------------------------

Node = namedtuple('Node', ['freq', 'char', 'left', 'right'])

def make_huffman_tree(text):
    freqs = Counter(text)
    heap = [Node(freq, ch, None, None) for ch, freq in freqs.items()]
    heapq.heapify(heap)
    # Merge least frequent nodes until one tree remains
    while len(heap) > 1:
        left = heapq.heappop(heap)
        right = heapq.heappop(heap)
        merged = Node(left.freq + right.freq, None, left, right)
        heapq.heappush(heap, merged)
    return heap[0]


def make_codes(node, prefix='', codebook=None):
    if codebook is None:
        codebook = {}
    if node.char is not None:
        codebook[node.char] = prefix or '0'
    else:
        make_codes(node.left,  prefix + '0', codebook)
        make_codes(node.right, prefix + '1', codebook)
    return codebook


def huffman_compress(text):
    """
    Compresses input text to a bitstring and returns
    the compressed data plus the codebook for decompression.
    """
    tree = make_huffman_tree(text)
    codebook = make_codes(tree)
    compressed = ''.join(codebook[ch] for ch in text)
    return compressed, codebook

# -----------------------------------------------------------------------------
# GUI Application
# -----------------------------------------------------------------------------

class EmergencyGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("City Emergency Manager")
        self.geometry("520x450")

        # Build the graph and seed resources
        self.G = build_city_graph()
        initialize_resources(self.G)

        # UI buttons for main actions
        ttk.Button(self, text="Show Resource Map",
                   command=self.show_map).pack(pady=6)
        ttk.Button(self, text="Handle Incident",
                   command=self.handle_incident_gui).pack(pady=6)
        ttk.Button(self, text="Open Log",
                   command=self.open_log).pack(pady=6)

    def show_map(self):
        """Displays the city graph with resources."""
        visualize_graph(self.G)

    def handle_incident_gui(self):
        """Prompts user to select an incident to handle."""
        win = tk.Toplevel(self)
        win.title("Select Incident")
        lb = tk.Listbox(win, width=75)
        mapping = {'fire_trucks':'FT', 'ambulances':'AMB', 'police_cars':'PC'}
        for i, inc in enumerate(INCIDENTS):
            needs = ', '.join(f"{mapping[k]}:{v}" for k,v in inc['needs'].items() if v)
            lb.insert(tk.END,
                      f"{i+1}. {inc['id']} @ {inc['node']} @ "
                      f"{inc['time'].strftime('%Y-%m-%d %H:%M')} "
                      f"needs {needs}")
        lb.pack(padx=10, pady=10)

        def on_handle():
            sel = lb.curselection()
            if not sel:
                messagebox.showwarning("Selection Error",
                                       "Please select an incident.")
                return
            win.destroy()
            self.process_incident(sel[0])

        ttk.Button(win, text="Handle Selected",
                   command=on_handle).pack(pady=5)

    def process_incident(self, index):
        """Handles the chosen incident and any within 24 hours."""
        selected = INCIDENTS[index]
        start_time = selected['time']
        end_time = start_time + timedelta(hours=24)
        # Filter incidents in the 24h window
        window_incs = [inc for inc in INCIDENTS
                       if start_time <= inc['time'] <= end_time]
        window_incs.sort(key=lambda x: x['time'])

        # Copy graph and allocate resources
        tempG = build_city_graph()
        initialize_resources(tempG)
        allocs = allocate_resources(
            tempG,
            [(inc['id'], inc['node'], inc['needs']) for inc in window_incs]
        )

        # Prepare display and log entries
        display_lines = []
        log_entries = [f"=== Handled at "
                       f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ==="]
        for inc in window_incs:
            header = (f"{inc['id']} @ {inc['node']} @ "
                      f"{inc['time'].strftime('%Y-%m-%d %H:%M')}: ")
            display_lines.append(header)
            log_entries.append(header)
            for rtype, from_node, dist in allocs[inc['id']]:
                if from_node:
                    line = f"  {rtype} assigned from {from_node} ({dist} min)"
                else:
                    line = f"  No {rtype} available"
                display_lines.append(line)
                log_entries.append(line)
            display_lines.append("")
            log_entries.append("")

        # Append to log file
        with open(LOG_FILE, 'a') as f:
            f.write("\n".join(log_entries) + "\n\n")

        messagebox.showinfo("Allocations",
                            "\n".join(display_lines))

    def open_log(self):
        """Opens the log viewer with optional Huffman compression."""
        win = tk.Toplevel(self)
        win.title("Incident Log")
        text = tk.Text(win, width=85, height=20)
        text.pack(padx=10, pady=10)
        try:
            with open(LOG_FILE) as f:
                content = f.read()
        except FileNotFoundError:
            content = "No log entries yet."
        text.insert('1.0', content)

        def on_compress():
            if not content.strip():
                messagebox.showwarning("Empty Log",
                                       "Nothing to compress.")
                return
            compressed, codebook = huffman_compress(content)
            orig_bits = len(content) * 8
            comp_bits = len(compressed)
            ratio = comp_bits / orig_bits * 100
            # Write compressed data and codebook
            with open(COMPRESSED_FILE, 'w') as cf:
                cf.write(compressed)
            with open(CODEBOOK_FILE, 'w') as cb:
                for ch, code in codebook.items():
                    cb.write(f"{repr(ch)}:{code}\n")
            messagebox.showinfo(
                "Compression Complete",
                f"Original: {orig_bits} bits\n"
                f"Compressed: {comp_bits} bits\n"
                f"Ratio: {ratio:.1f}%\n"
                f"Saved to {COMPRESSED_FILE}" )

        btn_frame = ttk.Frame(win)
        btn_frame.pack(pady=5)
        ttk.Button(btn_frame, text="Compress Log",
                   command=on_compress).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="Close",
                   command=win.destroy).pack(side='left')

if __name__ == "__main__":
    app = EmergencyGUI()
    app.mainloop()
