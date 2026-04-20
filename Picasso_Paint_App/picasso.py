"""
Project 6 : Picasso
A simple paint / sketch desktop application using Python and Tkinter.

Features included:
- Freehand drawing with mouse
- Multiple colors (red, green, blue, black + a few extras)
- Eraser tool
- Clear canvas
- Pen width control
- Visual feedback for currently selected color/tool
- Resizable window
- Shapes: rectangle, oval, triangle
- Undo for last 5 actions
- Spray paint tool
- Save and load drawing data

Notes:
- Save/load stores the drawing as JSON instructions, not as an image file.
- The app uses only standard Python libraries.
"""

import json
import math
import random
import tkinter as tk
from tkinter import ttk, filedialog, messagebox


class PicassoApp:
    """Main paint application class."""

    def __init__(self, root):
        self.root = root
        self.root.title("Picasso - Python Paint App")
        self.root.geometry("1100x700")
        self.root.minsize(800, 500)

        # -----------------------------
        # State variables
        # -----------------------------
        self.current_color = "black"
        self.background_color = "white"
        self.current_width = 4

        # Tools:
        # pen, eraser, spray, rectangle, oval, triangle
        self.current_tool = "pen"

        # Used while drawing freehand
        self.last_x = None
        self.last_y = None

        # Used while drawing shapes
        self.shape_start_x = None
        self.shape_start_y = None
        self.preview_shape_id = None

        # Each action is a list of canvas item IDs created together.
        # This makes undo easier because one "stroke" can remove many line segments.
        self.action_history = []
        self.max_undo = 5

        # Save enough information to rebuild the drawing later.
        self.saved_actions = []

        # Keep references to toolbar buttons so the UI can show selected tool/color.
        self.tool_buttons = {}
        self.color_buttons = {}

        self._build_ui()
        self._bind_canvas_events()
        self._update_status()

    # ------------------------------------------------------------------
    # UI SETUP
    # ------------------------------------------------------------------
    def _build_ui(self):
        """Create the main interface layout and controls."""

        self.root.columnconfigure(0, weight=0)
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(0, weight=1)

        # Left toolbar frame
        self.toolbar = ttk.Frame(self.root, padding=10)
        self.toolbar.grid(row=0, column=0, sticky="ns")

        # Right drawing area frame
        self.canvas_frame = ttk.Frame(self.root, padding=10)
        self.canvas_frame.grid(row=0, column=1, sticky="nsew")

        self.canvas_frame.rowconfigure(1, weight=1)
        self.canvas_frame.columnconfigure(0, weight=1)

        # -----------------------------
        # Title / status
        # -----------------------------
        title_label = ttk.Label(
            self.toolbar,
            text="Picasso",
            font=("Segoe UI", 18, "bold")
        )
        title_label.pack(anchor="w", pady=(0, 10))

        self.status_label = ttk.Label(
            self.toolbar,
            text="",
            font=("Segoe UI", 10, "bold"),
            foreground="blue"
        )
        self.status_label.pack(anchor="w", pady=(0, 15))

        # -----------------------------
        # Tool selection
        # -----------------------------
        ttk.Label(self.toolbar, text="Tools", font=("Segoe UI", 11, "bold")).pack(anchor="w")

        tool_frame = ttk.Frame(self.toolbar)
        tool_frame.pack(fill="x", pady=(5, 15))

        self._make_tool_button(tool_frame, "Pen", "pen")
        self._make_tool_button(tool_frame, "Eraser", "eraser")
        self._make_tool_button(tool_frame, "Spray", "spray")
        self._make_tool_button(tool_frame, "Rectangle", "rectangle")
        self._make_tool_button(tool_frame, "Oval", "oval")
        self._make_tool_button(tool_frame, "Triangle", "triangle")

        # -----------------------------
        # Colors
        # -----------------------------
        ttk.Label(self.toolbar, text="Colors", font=("Segoe UI", 11, "bold")).pack(anchor="w")

        color_frame = ttk.Frame(self.toolbar)
        color_frame.pack(fill="x", pady=(5, 15))

        palette = ["black", "red", "green", "blue", "orange", "purple"]
        for color in palette:
            self._make_color_button(color_frame, color)

        # -----------------------------
        # Pen width slider
        # -----------------------------
        ttk.Label(self.toolbar, text="Pen Width", font=("Segoe UI", 11, "bold")).pack(anchor="w")

        self.width_var = tk.IntVar(value=self.current_width)
        self.width_slider = ttk.Scale(
            self.toolbar,
            from_=1,
            to=30,
            orient="horizontal",
            command=self._on_width_change
        )
        self.width_slider.set(self.current_width)
        self.width_slider.pack(fill="x", pady=(5, 0))

        self.width_value_label = ttk.Label(self.toolbar, text=f"{self.current_width}px")
        self.width_value_label.pack(anchor="w", pady=(2, 15))

        # -----------------------------
        # Action buttons
        # -----------------------------
        ttk.Label(self.toolbar, text="Actions", font=("Segoe UI", 11, "bold")).pack(anchor="w")

        action_frame = ttk.Frame(self.toolbar)
        action_frame.pack(fill="x", pady=(5, 15))

        ttk.Button(action_frame, text="Undo", command=self.undo_last_action).pack(fill="x", pady=2)
        ttk.Button(action_frame, text="Clear Canvas", command=self.clear_canvas).pack(fill="x", pady=2)
        ttk.Button(action_frame, text="Save Drawing", command=self.save_drawing).pack(fill="x", pady=2)
        ttk.Button(action_frame, text="Load Drawing", command=self.load_drawing).pack(fill="x", pady=2)

        # Helpful instructions
        help_text = (
            "Instructions:\n"
            "- Drag mouse to draw.\n"
            "- Pen/Spray use selected color.\n"
            "- Eraser paints with canvas background.\n"
            "- For shapes, click and drag.\n"
            "- Undo remembers last 5 actions."
        )
        ttk.Label(self.toolbar, text=help_text, justify="left", wraplength=220).pack(anchor="w", pady=(10, 0))

        # -----------------------------
        # Canvas
        # -----------------------------
        canvas_title = ttk.Label(
            self.canvas_frame,
            text="Drawing Area",
            font=("Segoe UI", 12, "bold")
        )
        canvas_title.grid(row=0, column=0, sticky="w", pady=(0, 5))

        self.canvas = tk.Canvas(
            self.canvas_frame,
            bg=self.background_color,
            highlightthickness=1,
            highlightbackground="#999999"
        )
        self.canvas.grid(row=1, column=0, sticky="nsew")

    def _make_tool_button(self, parent, text, tool_name):
        """Create and store a tool button."""
        button = ttk.Button(
            parent,
            text=text,
            command=lambda: self.select_tool(tool_name)
        )
        button.pack(fill="x", pady=2)
        self.tool_buttons[tool_name] = button

    def _make_color_button(self, parent, color_name):
        """Create a color button with a colored label."""
        button = tk.Button(
            parent,
            bg=color_name,
            width=12,
            relief="raised",
            command=lambda c=color_name: self.select_color(c)
        )
        button.pack(fill="x", pady=2)
        self.color_buttons[color_name] = button

    # ------------------------------------------------------------------
    # STATE / STATUS
    # ------------------------------------------------------------------
    def select_tool(self, tool_name):
        """Select the active drawing tool."""
        self.current_tool = tool_name
        self._update_status()

    def select_color(self, color_name):
        """Select the active color and switch away from eraser if needed."""
        self.current_color = color_name

        # If the user picks a real color while eraser is active,
        # it feels natural to switch back to the pen tool.
        if self.current_tool == "eraser":
            self.current_tool = "pen"

        self._update_status()

    def _on_width_change(self, value):
        """Update brush width when the slider moves."""
        self.current_width = int(float(value))
        self.width_value_label.config(text=f"{self.current_width}px")

    def _update_status(self):
        """Refresh text and button styles to show current selection."""
        self.status_label.config(
            text=f"Tool: {self.current_tool.title()} | Color: {self.current_color.title()} | Width: {self.current_width}px"
        )

        # Visually indicate selected color
        for color_name, button in self.color_buttons.items():
            if color_name == self.current_color and self.current_tool != "eraser":
                button.config(relief="sunken", bd=3)
            else:
                button.config(relief="raised", bd=1)

        # Visually indicate selected tool
        for tool_name, button in self.tool_buttons.items():
            if tool_name == self.current_tool:
                button.state(["pressed"])
            else:
                button.state(["!pressed"])

    # ------------------------------------------------------------------
    # CANVAS EVENT BINDINGS
    # ------------------------------------------------------------------
    def _bind_canvas_events(self):
        """Bind mouse events for painting and shape creation."""
        self.canvas.bind("<ButtonPress-1>", self.on_mouse_down)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_up)

    def on_mouse_down(self, event):
        """Handle the first click on the canvas."""
        self.last_x = event.x
        self.last_y = event.y

        # Start a new action group. Everything created until mouse release
        # will belong to this single undoable action.
        self.current_action_ids = []
        self.current_action_data = []

        if self.current_tool in ("rectangle", "oval", "triangle"):
            self.shape_start_x = event.x
            self.shape_start_y = event.y

    def on_mouse_drag(self, event):
        """Handle dragging while the mouse button is held."""
        if self.current_tool == "pen":
            self._draw_freehand(event.x, event.y, erase=False)

        elif self.current_tool == "eraser":
            self._draw_freehand(event.x, event.y, erase=True)

        elif self.current_tool == "spray":
            self._spray_paint(event.x, event.y)

        elif self.current_tool in ("rectangle", "oval", "triangle"):
            self._preview_shape(event.x, event.y)

    def on_mouse_up(self, event):
        """Finish the current action and store it for undo/save."""
        if self.current_tool in ("rectangle", "oval", "triangle"):
            self._finalize_shape(event.x, event.y)

        # Only store actions that actually created something.
        if hasattr(self, "current_action_ids") and self.current_action_ids:
            self.action_history.append(self.current_action_ids)

            # Keep only the last 5 actions for undo memory.
            if len(self.action_history) > self.max_undo:
                self.action_history.pop(0)

            # Store permanent rebuild data for save/load.
            self.saved_actions.append(self.current_action_data)

        self.last_x = None
        self.last_y = None
        self.shape_start_x = None
        self.shape_start_y = None
        self.preview_shape_id = None

    # ------------------------------------------------------------------
    # DRAWING FUNCTIONS
    # ------------------------------------------------------------------
    def _draw_freehand(self, x, y, erase=False):
        """Draw a smooth freehand line segment from the previous point to the new point."""
        if self.last_x is None or self.last_y is None:
            self.last_x, self.last_y = x, y
            return

        color = self.background_color if erase else self.current_color

        line_id = self.canvas.create_line(
            self.last_x, self.last_y, x, y,
            fill=color,
            width=self.current_width,
            capstyle=tk.ROUND,
            smooth=True
        )

        self.current_action_ids.append(line_id)
        self.current_action_data.append({
            "type": "line",
            "coords": [self.last_x, self.last_y, x, y],
            "fill": color,
            "width": self.current_width,
            "capstyle": "round",
            "smooth": True
        })

        self.last_x, self.last_y = x, y

    def _spray_paint(self, x, y):
        """Simulate spray paint by drawing many tiny dots around the cursor."""
        radius = self.current_width * 2
        dot_count = 20 + self.current_width

        for _ in range(dot_count):
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(0, radius)

            dot_x = x + math.cos(angle) * distance
            dot_y = y + math.sin(angle) * distance

            size = max(1, self.current_width // 4)

            dot_id = self.canvas.create_oval(
                dot_x, dot_y,
                dot_x + size, dot_y + size,
                fill=self.current_color,
                outline=self.current_color
            )

            self.current_action_ids.append(dot_id)
            self.current_action_data.append({
                "type": "oval",
                "coords": [dot_x, dot_y, dot_x + size, dot_y + size],
                "fill": self.current_color,
                "outline": self.current_color,
                "width": 1
            })

        self.last_x, self.last_y = x, y

    # ------------------------------------------------------------------
    # SHAPE FUNCTIONS
    # ------------------------------------------------------------------
    def _preview_shape(self, x, y):
        """Show a temporary preview of the current shape while dragging."""
        if self.preview_shape_id is not None:
            self.canvas.delete(self.preview_shape_id)

        x1, y1 = self.shape_start_x, self.shape_start_y
        x2, y2 = x, y

        if self.current_tool == "rectangle":
            self.preview_shape_id = self.canvas.create_rectangle(
                x1, y1, x2, y2,
                outline=self.current_color,
                width=self.current_width,
                dash=(4, 2)
            )

        elif self.current_tool == "oval":
            self.preview_shape_id = self.canvas.create_oval(
                x1, y1, x2, y2,
                outline=self.current_color,
                width=self.current_width,
                dash=(4, 2)
            )

        elif self.current_tool == "triangle":
            points = self._triangle_points(x1, y1, x2, y2)
            self.preview_shape_id = self.canvas.create_polygon(
                points,
                outline=self.current_color,
                fill="",
                width=self.current_width,
                dash=(4, 2)
            )

    def _finalize_shape(self, x, y):
        """Replace the preview with a real shape and save it as one action."""
        if self.preview_shape_id is not None:
            self.canvas.delete(self.preview_shape_id)
            self.preview_shape_id = None

        x1, y1 = self.shape_start_x, self.shape_start_y
        x2, y2 = x, y

        if self.current_tool == "rectangle":
            shape_id = self.canvas.create_rectangle(
                x1, y1, x2, y2,
                outline=self.current_color,
                width=self.current_width
            )
            shape_data = {
                "type": "rectangle",
                "coords": [x1, y1, x2, y2],
                "outline": self.current_color,
                "width": self.current_width
            }

        elif self.current_tool == "oval":
            shape_id = self.canvas.create_oval(
                x1, y1, x2, y2,
                outline=self.current_color,
                width=self.current_width
            )
            shape_data = {
                "type": "oval",
                "coords": [x1, y1, x2, y2],
                "outline": self.current_color,
                "width": self.current_width,
                "fill": ""
            }

        elif self.current_tool == "triangle":
            points = self._triangle_points(x1, y1, x2, y2)
            shape_id = self.canvas.create_polygon(
                points,
                outline=self.current_color,
                fill="",
                width=self.current_width
            )
            shape_data = {
                "type": "polygon",
                "coords": points,
                "outline": self.current_color,
                "fill": "",
                "width": self.current_width
            }

        else:
            return

        self.current_action_ids.append(shape_id)
        self.current_action_data.append(shape_data)

    def _triangle_points(self, x1, y1, x2, y2):
        """Return three points for a triangle inside the drag box."""
        top_x = (x1 + x2) / 2
        top_y = y1
        left_x = x1
        left_y = y2
        right_x = x2
        right_y = y2
        return [top_x, top_y, left_x, left_y, right_x, right_y]

    # ------------------------------------------------------------------
    # UNDO / CLEAR
    # ------------------------------------------------------------------
    def undo_last_action(self):
        """Remove the most recent action from the canvas and saved data."""
        if not self.action_history:
            messagebox.showinfo("Undo", "Nothing to undo.")
            return

        last_action_ids = self.action_history.pop()

        for item_id in last_action_ids:
            self.canvas.delete(item_id)

        # Remove the matching saved action block too, if available.
        if self.saved_actions:
            self.saved_actions.pop()

    def clear_canvas(self):
        """Erase the entire canvas and reset stored actions."""
        confirm = messagebox.askyesno("Clear Canvas", "Are you sure you want to clear the entire canvas?")
        if confirm:
            self.canvas.delete("all")
            self.action_history.clear()
            self.saved_actions.clear()

    # ------------------------------------------------------------------
    # SAVE / LOAD
    # ------------------------------------------------------------------
    def save_drawing(self):
        """Save the drawing instructions to a JSON file."""
        if not self.saved_actions:
            messagebox.showinfo("Save Drawing", "There is nothing to save.")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")]
        )

        if not file_path:
            return

        data = {
            "background": self.background_color,
            "actions": self.saved_actions
        }

        try:
            with open(file_path, "w", encoding="utf-8") as file:
                json.dump(data, file, indent=4)
            messagebox.showinfo("Save Drawing", "Drawing saved successfully.")
        except Exception as exc:
            messagebox.showerror("Save Error", f"Could not save drawing:\n{exc}")

    def load_drawing(self):
        """Load drawing instructions from a JSON file and rebuild the canvas."""
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")]
        )

        if not file_path:
            return

        try:
            with open(file_path, "r", encoding="utf-8") as file:
                data = json.load(file)

            self.canvas.delete("all")
            self.action_history.clear()
            self.saved_actions.clear()

            self.background_color = data.get("background", "white")
            self.canvas.config(bg=self.background_color)

            loaded_actions = data.get("actions", [])

            for action_group in loaded_actions:
                created_ids = []

                for item in action_group:
                    item_type = item.get("type")
                    coords = item.get("coords", [])
                    width = item.get("width", 1)
                    fill = item.get("fill", "")
                    outline = item.get("outline", "")
                    smooth = item.get("smooth", False)

                    if item_type == "line":
                        new_id = self.canvas.create_line(
                            *coords,
                            fill=fill,
                            width=width,
                            capstyle=tk.ROUND,
                            smooth=smooth
                        )

                    elif item_type == "rectangle":
                        new_id = self.canvas.create_rectangle(
                            *coords,
                            outline=outline,
                            width=width
                        )

                    elif item_type == "oval":
                        new_id = self.canvas.create_oval(
                            *coords,
                            outline=outline,
                            fill=fill,
                            width=width
                        )

                    elif item_type == "polygon":
                        new_id = self.canvas.create_polygon(
                            *coords,
                            outline=outline,
                            fill=fill,
                            width=width
                        )

                    else:
                        continue

                    created_ids.append(new_id)

                if created_ids:
                    self.action_history.append(created_ids)
                    if len(self.action_history) > self.max_undo:
                        self.action_history.pop(0)

                    self.saved_actions.append(action_group)

            messagebox.showinfo("Load Drawing", "Drawing loaded successfully.")

        except Exception as exc:
            messagebox.showerror("Load Error", f"Could not load drawing:\n{exc}")


def main():
    """Program entry point."""
    root = tk.Tk()

    # Use ttk theme if available
    style = ttk.Style()
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass

    app = PicassoApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()