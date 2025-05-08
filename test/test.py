import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.scrolledtext import ScrolledText
import random
from datetime import datetime, timedelta
import heapq
from collections import Counter, namedtuple

# -------------------------------------------------------------
# City Emergency Response Manager
# -------------------------------------------------------------

# Log file paths
LOG_FILE         = 'incident_log.txt'
COMPRESSED_FILE  = 'incident_log.huff'
CODEBOOK_FILE    = 'incident_log_codebook.txt'

# Pre-defined incidents
INCIDENTS = [
    {'node':'B','time':datetime(2025,5,4,8,0),  'needs':{'Fire Trucks':1,'Ambulances':1,'Police Cars':0}},
    {'node':'D','time':datetime(2025,5,4,14,30), 'needs':{'Fire Trucks':1,'Ambulances':0,'Police Cars':0}},
    {'node':'F','time':datetime(2025,5,4,20,45), 'needs':{'Fire Trucks':0,'Ambulances':0,'Police Cars':1}},
    {'node':'A','time':datetime(2025,5,5,2,0),   'needs':{'Fire Trucks':0,'Ambulances':1,'Police Cars':1}},
    {'node':'I','time':datetime(2025,5,5,10,15),'needs':{'Fire Trucks':2,'Ambulances':0,'Police Cars':0}},
    {'node':'H','time':datetime(2025,5,5,18,0), 'needs':{'Fire Trucks':0,'Ambulances':1,'Police Cars':0}},
]
NODE_LABELS = ['HQ','A','B','C','D','E','F','G','H','I']

# -------------------------------------------------------------
# Graph & Resource Initialization
# -------------------------------------------------------------
def build_city_graph(rows=2, cols=5):
    random.seed(42)
    G = nx.grid_2d_graph(rows, cols)

    mapping, idx = {}, 0
    for r in range(rows):
        for c in range(cols):
            mapping[(r,c)] = NODE_LABELS[idx]
            idx += 1
    G = nx.relabel_nodes(G, mapping)

    # Assigns a random travel time between 5 and 60 minutes
    for u, v in G.edges():
        G.edges[u, v]['weight'] = random.randint(5, 60)

    return G


def initialize_resources(G):
    for n in G.nodes:
        G.nodes[n]['Fire Trucks'] = random.randint(0,2)
        G.nodes[n]['Ambulances']  = random.randint(0,1)
        G.nodes[n]['Police Cars'] = random.randint(0,1)

# -------------------------------------------------------------
# Routing & Allocation Logic
# -------------------------------------------------------------
def shortest_path(G, src, dst):
    return nx.single_source_dijkstra(G, src, dst, weight='weight')


def allocate_resources(G, incidents):
    assigns = {}
    for node, needs in incidents:
        assigns[node] = []
        for rtype, count in needs.items():
            for _ in range(count):
                best_node, best_d = None, float('inf')
                for cand in G.nodes:
                    if G.nodes[cand][rtype] > 0:
                        d, _ = shortest_path(G, cand, node)
                        if d < best_d:
                            best_d, best_node = d, cand
                if best_node:
                    assigns[node].append((rtype, best_node, best_d))
                    G.nodes[best_node][rtype] -= 1
                else:
                    assigns[node].append((rtype, None, None))
    return assigns

# -------------------------------------------------------------
# Huffman Compression
# -------------------------------------------------------------
Node = namedtuple('Node',['freq','char','left','right'])

def make_huffman_tree(text):
    freqs = Counter(text)
    heap = [Node(f, ch, None, None) for ch, f in freqs.items()]
    heapq.heapify(heap)
    while len(heap) > 1:
        a = heapq.heappop(heap)
        b = heapq.heappop(heap)
        heapq.heappush(heap, Node(a.freq + b.freq, None, a, b))
    return heap[0]


def make_codes(node, prefix='', codebook=None):
    if codebook is None: codebook = {}
    if node.char is not None:
        codebook[node.char] = prefix or '0'
    else:
        make_codes(node.left,  prefix+'0', codebook)
        make_codes(node.right, prefix+'1', codebook)
    return codebook


def huffman_compress(text):
    tree = make_huffman_tree(text)
    cb = make_codes(tree)
    return ''.join(cb[ch] for ch in text), cb

# -------------------------------------------------------------
# GUI Application
# -------------------------------------------------------------
class EmergencyGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("City Emergency Manager")
        self.geometry('900x650')
        self.configure(bg='#001f3f')

        # Style
        style = ttk.Style(self)
        style.theme_use('clam')
        font_name = 'Comic Sans MS'

        # Frame labels
        style.configure('TLabelframe', background='#001f3f', borderwidth=0, relief='flat')
        style.configure('TLabelframe.Label', background='#001f3f', foreground='white', font=(font_name,16))
        style.configure('TFrame', background='#001f3f')

        # Buttons & widgets
        style.configure('TButton', font=(font_name,12), relief='ridge', padding=6,
                        background='#004080', foreground='white')
        style.map('TButton', background=[('active','#0059b3')])
        style.configure('TLabel', background='#001f3f', foreground='white', font=(font_name,12))
        style.configure('TCombobox', fieldbackground='#003366', background='#003366',
                        foreground='white', font=(font_name,12))
        style.configure('Vertical.TScrollbar', troughcolor='#003366', background='#0059b3')

        # Layout
        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Borderless Frames
        self.map_frame     = ttk.Labelframe(self, text='Resource Map')
        self.control_frame = ttk.Labelframe(self, text='Actions')
        self.log_frame     = ttk.Labelframe(self, text='Incident Log')
        self.map_frame.grid(    row=0, column=0, rowspan=2, padx=10, pady=10, sticky='nsew')
        self.control_frame.grid(row=0, column=1, padx=10, pady=10, sticky='new')
        self.log_frame.grid(    row=1, column=1, padx=10, pady=10, sticky='nsew')

        # Data
        self.G = build_city_graph()
        initialize_resources(self.G)

        # Map Canvas
        self._draw_map()

        # Controls
        self.sel_var = tk.StringVar()
        self.combo = ttk.Combobox(
            self.control_frame, textvariable=self.sel_var,
            values=[f"{inc['node']} @ {inc['time'].strftime('%Y-%m-%d %H:%M')}" for inc in INCIDENTS],
            state='readonly')
        self.combo.pack(fill='x', padx=10, pady=10)
        ttk.Button(self.control_frame, text='Handle Incident', command=self._handle_incident).pack(fill='x', padx=10, pady=5)
        ttk.Button(self.control_frame, text='Refresh Map',    command=self._refresh_map).pack(fill='x', padx=10, pady=5)
        ttk.Button(self.control_frame, text='Compress Log',   command=self._compress_log).pack(fill='x', padx=10, pady=5)

        # Log box
        self.log_box = ScrolledText(
            self.log_frame, wrap='word', bg='#003366', fg='white', font=(font_name,11), insertbackground='white')
        self.log_box.pack(expand=True, fill='both', padx=5, pady=5)
        self._load_log()

    def _draw_map(self):
        fig, ax = plt.subplots(figsize=(6,5), dpi=100, facecolor='#001f3f')
        ax.set_facecolor('#001f3f')
      
        pos = {n:((NODE_LABELS.index(n)%5)*2, -(NODE_LABELS.index(n)//4)) for n in self.G.nodes}
        labels = {n:f"{n}\nFT:{self.G.nodes[n]['Fire Trucks']} AMB:{self.G.nodes[n]['Ambulances']}\nPC:{self.G.nodes[n]['Police Cars']}" for n in self.G.nodes}
        
        nx.draw(
            self.G, pos,
            labels=labels,
            node_size=9000,
            node_shape='s',
            node_color='#004080',
            edgecolors='white',
            font_family='Comic Sans MS',
            font_size=12,
            font_color='white',
            ax=ax
        )
        nx.draw_networkx_edge_labels(
            self.G, pos,
            edge_labels=nx.get_edge_attributes(self.G,'weight'),
            font_size=16,
            font_color='black',
            ax=ax
        )
        ax.margins(0.1)
        ax.axis('off')
        self.canvas = FigureCanvasTkAgg(fig, master=self.map_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(expand=True, fill='both')

    def _refresh_map(self):
        initialize_resources(self.G)
        self.canvas.get_tk_widget().destroy()
        self._draw_map()

    def _load_log(self):
        try:
            content = open(LOG_FILE).read()
        except FileNotFoundError:
            content = ''
        self.log_box.delete('1.0', tk.END)
        self.log_box.insert(tk.END, content)

    def _compress_log(self):
        text = self.log_box.get('1.0', tk.END)
        if not text.strip():
            return messagebox.showwarning('Empty Log', 'Nothing to compress.')
        compressed, codebook = huffman_compress(text)
        orig_bits = len(text) * 8
        comp_bits = len(compressed)
        with open(COMPRESSED_FILE, 'w') as f:
            f.write(compressed)
        with open(CODEBOOK_FILE, 'w') as f:
            for ch, code in codebook.items():
                f.write(f"{repr(ch)}:{code}\n")
        messagebox.showinfo('Compressed', f'Orig: {orig_bits}b\nComp: {comp_bits}b')

    def _handle_incident(self):
        sel = self.combo.current()
        if sel < 0:
            return messagebox.showwarning('Select Incident', 'Choose one from dropdown.')
        start = INCIDENTS[sel]['time']
        end = start + timedelta(hours=24)
        window = [inc for inc in INCIDENTS if start <= inc['time'] <= end]
        window.sort(key=lambda x: x['time'])
        G2 = build_city_graph(); initialize_resources(G2)
        alloc = allocate_resources(G2, [(i['node'], i['needs']) for i in window])
        lines = [f"=== {datetime.now().strftime('%Y-%m-%d %H:%M')} handled ==="]
        for inc in window:
            lines.append(f"{inc['node']} @ {inc['time'].strftime('%H:%M')}")
            for r, f, d in alloc[inc['node']]:
                if f:
                    lines.append(f"  {r} from {f} ({d}min)")
                else:
                    lines.append(f"  No {r}")
            lines.append("")
        with open(LOG_FILE, 'a') as f:
            f.write("\n".join(lines) + "\n")
        self._load_log()
        messagebox.showinfo('Handled', 'Incident(s) logged & resources allocated.')

if __name__ == '__main__':
    app = EmergencyGUI()
    app.mainloop()
