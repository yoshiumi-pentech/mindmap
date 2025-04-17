import tkinter as tk
from tkinter import simpledialog

class MindMapApp:
    def __init__(self, root):
        self.root = root
        self.root.title("マインドマップ作成ツール")
        self.canvas = tk.Canvas(root, bg="white", width=800, height=600)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.nodes = {}
        self.connections = []
        self.selected_node = None

        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)

        self.create_menu()

    def create_menu(self):
        menu = tk.Menu(self.root)
        self.root.config(menu=menu)

        node_menu = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label="ノード", menu=node_menu)
        node_menu.add_command(label="ノードを追加", command=self.add_node)

    def add_node(self, x, y):
        node_id = self.canvas.create_oval(x-30, y-30, x+30, y+30, fill="lightblue", outline="black")
        text_id = self.canvas.create_text(x, y, text="ダブルクリックで編集", font=("Arial", 12))
        self.nodes[node_id] = {"text_id": text_id, "label": "ダブルクリックで編集", "x": x, "y": y}
        self.canvas.tag_bind(text_id, "<Double-1>", lambda event, nid=node_id: self.edit_node_label(nid))

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

    def on_canvas_click(self, event):
        clicked_items = self.canvas.find_overlapping(event.x, event.y, event.x, event.y)
        for item in clicked_items:
            if item in self.nodes:
                self.selected_node = item
                break
        else:
            # If no node is clicked, create a new node at the clicked position
            self.add_node(event.x, event.y)

    def on_drag(self, event):
        if self.selected_node:
            x, y = event.x, event.y
            self.canvas.coords(self.selected_node, x-30, y-30, x+30, y+30)
            text_id = self.nodes[self.selected_node]["text_id"]
            self.canvas.coords(text_id, x, y)
            self.nodes[self.selected_node]["x"] = x
            self.nodes[self.selected_node]["y"] = y

    def on_release(self, event):
        self.selected_node = None

if __name__ == "__main__":
    print("Starting MindMapApp...")  # Debug statement to confirm script execution
    root = tk.Tk()
    app = MindMapApp(root)
    root.mainloop()
