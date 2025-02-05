import tkinter as tk
from tkinter import filedialog, Text, Menu, colorchooser
from PIL import Image, ImageTk
import os
import random
import math
import json

class Node:
    def __init__(self, canvas, x, y, node_type):
        self.canvas = canvas
        self.node_type = node_type
        self.visible = True
        self.important = False
        self.media_only = False
        
        offset_x = random.randint(10, 30) * random.choice([-1, 1])
        offset_y = random.randint(10, 30) * random.choice([-1, 1])
        self.x = x + offset_x
        self.y = y + offset_y
        self.create_node()

    def create_node(self):
        self.frame = self.canvas.create_rectangle(self.x, self.y, self.x + 150, self.y + 100, fill='lightgrey', tags='node')
        self.label = self.canvas.create_text(self.x + 60, self.y + 10, text=self.node_type, font=("Arial", 10, "bold"))

        if self.node_type == "Picture" or self.node_type == "Image and Text":
            self.button = self.canvas.create_text(self.x + 60, self.y + 40, text="Upload Image", font=("Arial", 8), tags="upload")
            self.canvas.tag_bind("upload", "<Button-1>", self.upload_image)
            if self.node_type == "Image and Text":
                self.text_entry = Text(self.canvas, width=15, height=2)
                self.entry_window = self.canvas.create_window(self.x + 60, self.y + 65, window=self.text_entry)
        elif self.node_type == "Text" or self.node_type == "File and Text":
            self.text_entry = Text(self.canvas, width=15, height=2)
            self.entry_window = self.canvas.create_window(self.x + 60, self.y + 40, window=self.text_entry)
            if self.node_type == "File and Text":
                self.button = self.canvas.create_text(self.x + 60, self.y + 65, text="Upload File", font=("Arial", 8), tags="upload_file")
                self.canvas.tag_bind("upload_file", "<Button-1>", self.upload_file)
        elif self.node_type == "File":
            self.button = self.canvas.create_text(self.x + 60, self.y + 40, text="Upload File", font=("Arial", 8), tags="upload_file")
            self.canvas.tag_bind("upload_file", "<Button-1>", self.upload_file)
        elif self.node_type == "URL Node":
            self.url_entry = Text(self.canvas, width=15, height=2)
            self.entry_window = self.canvas.create_window(self.x + 60, self.y + 40, window=self.url_entry)
        elif self.node_type == "Sound Node":
            self.button = self.canvas.create_text(self.x + 60, self.y + 40, text="Upload Sound", font=("Arial", 8), tags="upload_sound")
            self.canvas.tag_bind("upload_sound", "<Button-1>", self.upload_sound)

        self.canvas.tag_bind(self.frame, "<ButtonPress-1>", self.start_move)
        self.canvas.tag_bind(self.frame, "<B1-Motion>", self.move)
        
        # Bind right-click context menu to the whole node
        self.canvas.tag_bind(self.frame, "<Button-3>", self.show_context_menu)
        self.canvas.tag_bind(self.label, "<Button-3>", self.show_context_menu)
        if hasattr(self, 'button'):
            self.canvas.tag_bind(self.button, "<Button-3>", self.show_context_menu)
        if hasattr(self, 'entry_window'):
            self.canvas.tag_bind(self.entry_window, "<Button-3>", self.show_context_menu)
        
        # Enable dragging for the entire node
        self.canvas.tag_bind(self.frame, "<ButtonPress-1>", self.start_move)
        self.canvas.tag_bind(self.label, "<ButtonPress-1>", self.start_move)
        if hasattr(self, 'button'):
            self.canvas.tag_bind(self.button, "<ButtonPress-1>", self.start_move)
        if hasattr(self, 'entry_window'):
            self.canvas.tag_bind(self.entry_window, "<ButtonPress-1>", self.start_move)
        self.canvas.tag_bind(self.frame, "<B1-Motion>", self.move)
        self.canvas.tag_bind(self.label, "<B1-Motion>", self.move)
        if hasattr(self, 'button'):
            self.canvas.tag_bind(self.button, "<B1-Motion>", self.move)
        if hasattr(self, 'entry_window'):
            self.canvas.tag_bind(self.entry_window, "<B1-Motion>", self.move)

    def upload_image(self, event):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
        if file_path:
            image = Image.open(file_path)
            image = image.resize((100, 60), Image.LANCZOS)
            self.content = ImageTk.PhotoImage(image)
            self.image_id = self.canvas.create_image(self.x+60, self.y+50, image=self.content, tags='image')
            self.canvas.delete(self.button)
            self.canvas.tag_bind(self.image_id, "<Button-3>", self.show_context_menu)
    
    def upload_file(self, event):
        file_path = filedialog.askopenfilename(filetypes=[("All Files", "*.txt;*.docx;*.py")])
        if file_path:
            self.file_label = self.canvas.create_text(self.x+60, self.y+60, text=os.path.basename(file_path), font=("Arial", 7), fill="blue")
            self.canvas.delete(self.button)
            self.canvas.tag_bind(self.file_label, "<Button-3>", self.show_context_menu)

    def upload_sound(self, event):
        file_path = filedialog.askopenfilename(filetypes=[("Sound Files", "*.mp3;*.wav")])
        if file_path:
            self.canvas.create_text(self.x + 60, self.y + 60, text=os.path.basename(file_path), font=("Arial", 7), fill="blue")
            self.canvas.delete(self.button)
    
    def show_context_menu(self, event):
        self.context_menu = Menu(self.canvas, tearoff=0)
        self.context_menu.add_command(label="Delete", command=self.delete)
        self.context_menu.add_command(label="Duplicate", command=self.duplicate)
        self.context_menu.add_command(label="Media Only", command=self.media_only_toggle)
        self.context_menu.add_command(label="Mark as important", command=self.mark_as_important)
        self.context_menu.post(event.x_root, event.y_root)

    def media_only_toggle(self):
        self.media_only = not self.media_only
        if self.media_only:
            self.canvas.itemconfigure(self.frame, state="hidden")
            self.canvas.itemconfigure(self.label, state="hidden")
        else:
            self.canvas.itemconfigure(self.frame, state="normal")
            self.canvas.itemconfigure(self.label, state="normal")
    
    def delete(self):
        items_to_delete = [self.frame, self.label]
        if hasattr(self, 'button'):
            items_to_delete.append(self.button)
        if hasattr(self, 'entry_window'):
            items_to_delete.append(self.entry_window)
        if hasattr(self, 'image_id'):
            items_to_delete.append(self.image_id)
        self.canvas.delete(*items_to_delete)
    
    def duplicate(self):
        Node(self.canvas, self.x, self.y, self.node_type)

    def mark_as_important(self):
        self.important = not self.important
        fill_color = "yellow" if self.important else "lightgrey"
        self.canvas.itemconfigure(self.frame, fill=fill_color)
    
    def toggle_visibility(self):
        self.visible = not self.visible
        state = "normal" if self.visible else "hidden"
        self.canvas.itemconfigure(self.frame, state=state)
        self.canvas.itemconfigure(self.label, state=state)
        if hasattr(self, 'image_id'):
            self.canvas.itemconfigure(self.image_id, state=state)
        if hasattr(self, 'file_label'):
            self.canvas.itemconfigure(self.file_label, state=state)
        if hasattr(self, 'entry_window'):
            self.canvas.itemconfigure(self.entry_window, state=state)
        if hasattr(self, 'button'):
            self.canvas.itemconfigure(self.button, state=state)
    
    def start_move(self, event):
        self.drag_data = {"x": event.x, "y": event.y}

    def move(self, event):
        delta_x = event.x - self.drag_data["x"]
        delta_y = event.y - self.drag_data["y"]
        self.canvas.move(self.frame, delta_x, delta_y)
        self.canvas.move(self.label, delta_x, delta_y)
        if hasattr(self, 'image_id'):
            self.canvas.move(self.image_id, delta_x, delta_y)
        if hasattr(self, 'file_label'):
            self.canvas.move(self.file_label, delta_x, delta_y)
        if hasattr(self, 'entry_window'):
            self.canvas.move(self.entry_window, delta_x, delta_y)
        if hasattr(self, 'button'):
            self.canvas.move(self.button, delta_x, delta_y)
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y

class WhiteboardApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Information Whiteboard")
        self.root.geometry("1200x800")
        
        self.canvas = tk.Canvas(root, bg="white", scrollregion=(-5000, -5000, 5000, 5000))
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        self.canvas.bind("<ButtonPress-3>", self.start_pan)
        self.canvas.bind("<B3-Motion>", self.pan)
        self.canvas.bind("<MouseWheel>", self.zoom)
        self.canvas.bind("<Button-1>", self.check_pin_placement)
        
        self.default_color = "red"
        self.current_color = self.default_color
        
        self.menu_bar = Menu(root)

        # Project menu
        self.project_menu = Menu(self.menu_bar, tearoff=0)
        self.project_menu.add_command(label="Save", command=self.save_project)
        self.project_menu.add_command(label="Open", command=self.open_project)
        self.project_menu.add_command(label="Clear", command=self.clear_project)
        self.menu_bar.add_cascade(label="Project", menu=self.project_menu)
        
        root.config(menu=self.menu_bar)


        
        # Create Node menu
        self.node_menu = Menu(self.menu_bar, tearoff=0)
        self.node_menu.add_command(label="Picture Node", command=lambda: self.add_node("Picture"))
        self.node_menu.add_command(label="Text Node", command=lambda: self.add_node("Text"))
        self.node_menu.add_command(label="File Node", command=lambda: self.add_node("File"))
        self.node_menu.add_command(label="Image and Text", command=lambda: self.add_node("Image and Text"))
        self.node_menu.add_command(label="File and Text", command=lambda: self.add_node("File and Text"))
        self.node_menu.add_command(label="URL Node", command=lambda: self.add_node("URL Node"))
        self.node_menu.add_command(label="Sound Node", command=lambda: self.add_node("Sound Node"))
        self.menu_bar.add_cascade(label="Create Node", menu=self.node_menu)
        
        # Create Pin menu
        self.pin_menu = Menu(self.menu_bar, tearoff=0)
        self.pin_menu.add_command(label="Place Pin", command=self.start_pin_placement)
        self.pin_menu.add_command(label="Remove Pin", command=self.start_pin_removal)
        self.pin_menu.add_command(label="Central Pin", command=self.create_central_pin)
        self.pin_menu.add_command(label="Choose Color", command=self.choose_color)
        self.menu_bar.add_cascade(label="Pin", menu=self.pin_menu)
        
        # Create Thread menu
        self.thread_menu = Menu(self.menu_bar, tearoff=0)
        self.thread_menu.add_command(label="Single Thread", command=self.start_single_thread)
        self.thread_menu.add_command(label="Multi Thread", command=self.start_multi_thread)
        self.thread_menu.add_command(label="Remove Thread", command=self.start_remove_thread)
        self.thread_menu.add_command(label="Choose Color", command=self.choose_color)
        self.menu_bar.add_cascade(label="Thread", menu=self.thread_menu)

        root.config(menu=self.menu_bar)
        
        self.nodes = []
        self.pins = []
        self.lines = []
        self.pin_placement_mode = False
        self.pin_removal_mode = False
        self.single_thread_mode = False
        self.multi_thread_mode = False
        self.first_pin = None
        self.last_pin = None
        self.current_thread_color = self.default_color
        self.central_pin = None
        self.drag_data = {"x": 0, "y": 0}

    def add_node(self, node_type):
        node = Node(self.canvas, self.root.winfo_pointerx(), self.root.winfo_pointery(), node_type)
        self.nodes.append(node)
    
    def start_pin_placement(self):
        self.pin_placement_mode = True
        self.pin_removal_mode = False
    
    def start_pin_removal(self):
        self.pin_placement_mode = False
        self.pin_removal_mode = True
    
    def check_pin_placement(self, event):
        if self.pin_placement_mode:
            self.place_pin(event.x, event.y)
            self.pin_placement_mode = False
        elif self.pin_removal_mode:
            self.remove_pin(event.x, event.y)
            self.pin_removal_mode = False
        elif self.single_thread_mode:
            self.select_thread_pin(event.x, event.y)
        elif self.multi_thread_mode:
            self.select_multi_thread_pin(event.x, event.y)
    
    def choose_color(self):
        color = colorchooser.askcolor()[1]
        if color:
            self.current_color = color

    def create_central_pin(self):
        if self.central_pin:
            self.canvas.delete(self.central_pin)
        self.central_pin = self.canvas.create_oval(600-10, 400-10, 600+10, 400+10, fill=self.current_color, tags='central_pin')
        
        # Create threads to all existing pins from the central pin
        for pin in self.pins:
            self.create_thread(self.central_pin, pin)
    
    def start_single_thread(self):
        self.single_thread_mode = True
        self.first_pin = None
    
    def select_thread_pin(self, x, y):
        for pin in self.pins:
            pin_x = self.canvas.coords(pin)[0] + 10
            pin_y = self.canvas.coords(pin)[1] + 10
            distance = math.hypot(x - pin_x, y - pin_y)
            if distance < 10:
                if self.first_pin is None:
                    self.first_pin = pin
                else:
                    # Draw line between the two pins
                    self.create_thread(self.first_pin, pin)
                    self.first_pin = None
                return

    def start_multi_thread(self):
        self.multi_thread_mode = True
        self.last_pin = None

    def select_multi_thread_pin(self, x, y):
        for pin in self.pins:
            pin_x = self.canvas.coords(pin)[0] + 10
            pin_y = self.canvas.coords(pin)[1] + 10
            distance = math.hypot(x - pin_x, y - pin_y)
            if distance < 10:
                if self.last_pin is None:
                    self.last_pin = pin
                else:
                    # Draw line between the last pin and the new pin
                    self.create_thread(self.last_pin, pin)
                    self.last_pin = pin
                return

    def create_thread(self, pin1, pin2):
        pin1_coords = self.canvas.coords(pin1)
        pin2_coords = self.canvas.coords(pin2)
        line = self.canvas.create_line(pin1_coords[0] + 10, pin1_coords[1] + 10,
                                       pin2_coords[0] + 10, pin2_coords[1] + 10,
                                       fill=self.current_thread_color, width=2)
        self.lines.append(line)

    def start_remove_thread(self):
        self.canvas.bind("<Button-1>", self.remove_thread)

    def remove_thread(self, event):
        x, y = event.x, event.y
        items = self.canvas.find_overlapping(x - 1, y - 1, x + 1, y + 1)
        for item in items:
            if item in self.lines:
                self.canvas.delete(item)
                self.lines.remove(item)
                break
        # Unbind to stop further thread removal
        self.canvas.unbind("<Button-1>")
    
    def place_pin(self, x, y):
        for pin in self.pins:
            pin_x = self.canvas.coords(pin)[0] + 10
            pin_y = self.canvas.coords(pin)[1] + 10
            distance = math.hypot(x - pin_x, y - pin_y)
            if distance < 20:
                return  # Pin ist zu nahe an einem anderen Pin
        pin = self.canvas.create_oval(x-10, y-10, x+10, y+10, fill=self.current_color, tags='pin')
        self.pins.append(pin)
        
        # Create a thread to the central pin if it exists
        if self.central_pin:
            self.create_thread(self.central_pin, pin)
    
    def remove_pin(self, x, y):
        for pin in self.pins:
            pin_x = self.canvas.coords(pin)[0] + 10
            pin_y = self.canvas.coords(pin)[1] + 10
            distance = math.hypot(x - pin_x, y - pin_y)
            if distance < 10:
                self.canvas.delete(pin)
                self.pins.remove(pin)
                break

    def zoom(self, event):
        scale = 1.1 if event.delta > 0 else 0.9
        self.canvas.scale("all", event.x, event.y)
    
    def start_pan(self, event):
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y
    
    def pan(self, event):
        delta_x = event.x - self.drag_data["x"]
        delta_y = event.y - self.drag_data["y"]
        self.canvas.move(tk.ALL, delta_x, delta_y)
        self.drag_data["x"] = event.x
        self.drag_data["y"] = event.y

    def save_project(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON Files", "*.json")])
        if not file_path:
            return
        
        data = {
            "nodes": [],
            "pins": [],
            "threads": []
        }
        
        for node in self.nodes:
            node_data = {
                "x": node.x,
                "y": node.y,
                "type": node.node_type,
                "color": self.canvas.itemcget(node.frame, "fill"),
                "text": node.text_entry.get("1.0", "end").strip() if hasattr(node, 'text_entry') else "",
            }
            data["nodes"].append(node_data)
        
        for pin in self.pins:
            coords = self.canvas.coords(pin)
            data["pins"].append({"x": coords[0] + 10, "y": coords[1] + 10, "color": self.canvas.itemcget(pin, "fill")})
        
        for line in self.lines:
            coords = self.canvas.coords(line)
            data["threads"].append({"x1": coords[0], "y1": coords[1], "x2": coords[2], "y2": coords[3], "color": self.canvas.itemcget(line, "fill")})
        
        with open(file_path, "w") as f:
            json.dump(data, f, indent=4)
    
    def open_project(self):
        file_path = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
        if not file_path:
            return
        
        self.clear_project()
        
        with open(file_path, "r") as f:
            data = json.load(f)
        
        for node_data in data["nodes"]:
            node = Node(self.canvas, node_data["x"], node_data["y"], node_data["type"])
            self.nodes.append(node)
            self.canvas.itemconfig(node.frame, fill=node_data["color"])
            if hasattr(node, "text_entry"):
                node.text_entry.insert("1.0", node_data["text"])
        
        for pin_data in data["pins"]:
            pin = self.canvas.create_oval(pin_data["x"]-10, pin_data["y"]-10, pin_data["x"]+10, pin_data["y"]+10, fill=pin_data["color"], tags='pin')
            self.pins.append(pin)
        
        for thread_data in data["threads"]:
            line = self.canvas.create_line(thread_data["x1"], thread_data["y1"], thread_data["x2"], thread_data["y2"], fill=thread_data["color"], width=2)
            self.lines.append(line)
    
    def clear_project(self):
        for node in self.nodes:
            node.delete()
        self.nodes.clear()
        
        for pin in self.pins:
            self.canvas.delete(pin)
        self.pins.clear()
        
        for line in self.lines:
            self.canvas.delete(line)
        self.lines.clear()

root = tk.Tk()
app = WhiteboardApp(root)
root.mainloop()