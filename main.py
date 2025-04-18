import tkinter as tk
from tkinter import simpledialog
import json  # For saving and loading data

class MindMapApp:
    def __init__(self, root):
        self.root = root
        self.root.title("マインドマップ作成ツール")
        self.canvas = tk.Canvas(root, bg="white", width=800, height=600)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.nodes = {}
        self.connections = []
        self.selected_node = None
        self.active_node = None  # Track the active node for hierarchy
        self.hierarchy = {}  # Store parent-child relationships

        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)

        self.create_menu()
        self.load_state()  # Load saved state on startup
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)  # Handle app close event

    def create_menu(self):
        menu = tk.Menu(self.root)
        self.root.config(menu=menu)

        node_menu = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label="ノード", menu=node_menu)
        node_menu.add_command(label="ノードを追加", command=self.add_node)

    def add_node(self, x, y, parent=None):
        """Add a new node at the given position, optionally as a child of a parent node."""
        node_id = self.canvas.create_oval(x-30, y-30, x+30, y+30, fill="lightblue", outline="black")
        text_id = self.canvas.create_text(x, y, text="ダブルクリックで編集", font=("Arial", 12))
        level = 1 if parent is None else self.nodes[parent]["level"] + 1
        self.nodes[node_id] = {"text_id": text_id, "label": "ダブルクリックで編集", "x": x, "y": y, "level": level}
        self.canvas.tag_bind(text_id, "<Double-1>", lambda event, nid=node_id: self.edit_node_label(nid))

        # If a parent is specified, create a hierarchical relationship
        if parent:
            self.hierarchy[node_id] = parent
            parent_x, parent_y = self.nodes[parent]["x"], self.nodes[parent]["y"]
            self.canvas.create_line(parent_x, parent_y, x, y, fill="black")
            print(f"Node {node_id} added as child of {parent}, Level: {level}")

    def edit_node_label(self, node_id):
        text_id = self.nodes[node_id]["text_id"]
        x, y = self.nodes[node_id]["x"], self.nodes[node_id]["y"]

        # Create an entry widget for inline editing
        entry = tk.Entry(self.root, font=("Arial", 12))
        entry.insert(0, self.nodes[node_id]["label"])
        entry.place(x=x-50, y=y-10, width=100)

        def save_label(event):
            new_label = entry.get()
            self.nodes[node_id]["label"] = new_label
            self.canvas.itemconfig(text_id, text=new_label)
            entry.destroy()

        entry.bind("<Return>", save_label)
        entry.bind("<FocusOut>", lambda event: entry.destroy())  # Destroy entry if focus is lost

    def set_active_node(self, node_id):
        """Set the given node as active and update its appearance."""
        if self.active_node is not None:
            self.canvas.itemconfig(self.active_node, width=1)  # Reset border thickness
        self.active_node = node_id
        self.canvas.itemconfig(self.active_node, width=3)  # Highlight the active node

    def on_canvas_click(self, event):
        clicked_items = self.canvas.find_overlapping(event.x, event.y, event.x, event.y)
        for item in clicked_items:
            if item in self.nodes:
                self.set_active_node(item)  # Set the clicked node as active
                self.selected_node = item
                print(f"Selected node: {self.nodes[item]['label']}, Level: {self.nodes[item]['level']}")  # Debug statement
                break
        else:
            # If no node is clicked, create a new node at the clicked position
            if self.active_node:
                self.add_node(event.x, event.y, parent=self.active_node)  # Add as child of active node
            else:
                self.add_node(event.x, event.y)  # Add as a root node

    def on_drag(self, event):
        if self.selected_node:
            x, y = event.x, event.y
            self.canvas.coords(self.selected_node, x-30, y-30, x+30, y+30)
            text_id = self.nodes[self.selected_node]["text_id"]
            self.canvas.coords(text_id, x, y)
            self.nodes[self.selected_node]["x"] = x
            self.nodes[self.selected_node]["y"] = y

            # Update lines connecting to children
            for child, parent in self.hierarchy.items():
                if parent == self.selected_node:
                    child_x, child_y = self.nodes[child]["x"], self.nodes[child]["y"]
                    self.canvas.coords(self.canvas.find_withtag(f"line_{parent}_{child}"),
                                       x, y, child_x, child_y)

    def on_release(self, event):
        self.selected_node = None

    def save_state(self):
        """Save the current state of nodes, connections, and hierarchy to a file."""
        data = {
            "nodes": {
                node_id: {
                    "label": node_data["label"],
                    "x": node_data["x"],
                    "y": node_data["y"],
                    "level": node_data["level"]
                }
                for node_id, node_data in self.nodes.items()
            },
            "hierarchy": {
                child: parent for child, parent in self.hierarchy.items()
            }
        }
        with open("mindmap_state.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def load_state(self):
        """Load the saved state of nodes, connections, and hierarchy from a file."""
        try:
            with open("mindmap_state.json", "r", encoding="utf-8") as f:
                data = json.load(f)
                for node_id, node_data in data["nodes"].items():
                    x, y = node_data["x"], node_data["y"]
                    node_id = self.canvas.create_oval(x-30, y-30, x+30, y+30, fill="lightblue", outline="black")
                    text_id = self.canvas.create_text(x, y, text=node_data["label"], font=("Arial", 12))
                    self.nodes[node_id] = {
                        "text_id": text_id,
                        "label": node_data["label"],
                        "x": x,
                        "y": y,
                        "level": node_data["level"]
                    }
                    self.canvas.tag_bind(text_id, "<Double-1>", lambda event, nid=node_id: self.edit_node_label(nid))
                
                # Validate hierarchy and create connections
                self.hierarchy = {}
                for child, parent in data["hierarchy"].items():
                    if int(child) in self.nodes and int(parent) in self.nodes:
                        self.hierarchy[int(child)] = int(parent)
                        parent_x, parent_y = self.nodes[int(parent)]["x"], self.nodes[int(parent)]["y"]
                        child_x, child_y = self.nodes[int(child)]["x"], self.nodes[int(child)]["y"]
                        self.canvas.create_line(parent_x, parent_y, child_x, child_y, fill="black",
                                                tags=f"line_{parent}_{child}")
                    else:
                        print(f"Warning: Invalid hierarchy reference - child: {child}, parent: {parent}")
        except FileNotFoundError:
            print("No saved state found. Starting with an empty mind map.")
        except json.JSONDecodeError as e:
            print(f"Error loading mindmap_state.json: {e}. Starting with an empty mind map.")

    def on_close(self):
        """Handle the application close event."""
        self.save_state()  # Save the current state
        self.root.destroy()

if __name__ == "__main__":
    print("Starting MindMapApp...")  # Debug statement to confirm script execution
    root = tk.Tk()
    app = MindMapApp(root)
    root.mainloop()
