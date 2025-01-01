"""
DriftPaint - Art Made From Laptop Motion
Main application entry point.
"""

import tkinter as tk
from tkinter import ttk, colorchooser, filedialog, messagebox
from PIL import Image, ImageDraw
import time
import os
import sys

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sensor_service import SensorService


class DriftPaintApp:
    """Main DriftPaint Application."""

    # Color palette
    COLORS = [
        "#1a1a2e", "#16213e", "#0f3460", "#e94560",  # Dark theme
        "#ff6b6b", "#feca57", "#48dbfb", "#1dd1a1",  # Vibrant
        "#5f27cd", "#ff9ff3", "#54a0ff", "#00d2d3",  # Neon
        "#ffffff", "#2d3436", "#636e72", "#b2bec3",  # Neutrals
    ]

    def __init__(self, root):
        self.root = root
        self.root.title("DriftPaint - Art Made From Laptop Motion")
        self.root.geometry("1200x800")
        self.root.configure(bg="#0a0a0f")

        # App state
        self.canvas_width = 900
        self.canvas_height = 650
        self.brush_size = 8
        self.brush_color = "#e94560"
        self.sensitivity = 150  # pixels per unit tilt
        self.is_drawing = True

        # Cursor position (center of canvas initially)
        self.cursor_x = self.canvas_width / 2
        self.cursor_y = self.canvas_height / 2
        self.prev_x = self.cursor_x
        self.prev_y = self.cursor_y

        # Shake gesture state
        self.last_shake_handled = 0
        self.color_index = 0

        # Offscreen image for saving
        self.pil_image = Image.new("RGB", (self.canvas_width, self.canvas_height), "white")
        self.pil_draw = ImageDraw.Draw(self.pil_image)

        # Mock mode key states
        self.mock_keys = {"Left": False, "Right": False, "Up": False, "Down": False}

        # Initialize sensor
        # Initialize sensor
        self.sensor = SensorService(use_mock=False)  # Use hardware sensor if available


        self._setup_ui()
        self._bind_events()

        # Start sensor and update loop
        # Start sensor and update loop
        self.sensor.start()
        mode = "Hardware Sensor" if not self.sensor.use_mock else "Mock (Arrow Keys)"
        self.status_label.config(text=f"Mode: {mode}")
        self._update_loop()

    def _setup_ui(self):
        """Create the UI layout."""
        # Main container
        main_frame = tk.Frame(self.root, bg="#0a0a0f")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        # Left panel - Controls
        control_panel = tk.Frame(main_frame, bg="#12121a", width=250)
        control_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 15))
        control_panel.pack_propagate(False)

        # Title
        title_label = tk.Label(
            control_panel, text="DriftPaint", font=("Segoe UI", 20, "bold"),
            bg="#12121a", fg="#e94560"
        )
        title_label.pack(pady=(20, 5))

        subtitle_label = tk.Label(
            control_panel, text="Art From Motion", font=("Segoe UI", 10),
            bg="#12121a", fg="#666"
        )
        subtitle_label.pack(pady=(0, 20))

        # Brush Size
        size_frame = tk.Frame(control_panel, bg="#12121a")
        size_frame.pack(fill=tk.X, padx=15, pady=10)

        tk.Label(size_frame, text="Brush Size", bg="#12121a", fg="#aaa",
                 font=("Segoe UI", 9)).pack(anchor=tk.W)

        self.size_var = tk.IntVar(value=self.brush_size)
        size_slider = ttk.Scale(
            size_frame, from_=2, to=50, variable=self.size_var,
            orient=tk.HORIZONTAL, command=self._on_size_change
        )
        size_slider.pack(fill=tk.X, pady=(5, 0))

        self.size_label = tk.Label(size_frame, text=f"{self.brush_size}px",
                                   bg="#12121a", fg="#e94560", font=("Segoe UI", 9))
        self.size_label.pack(anchor=tk.E)

        # Sensitivity
        sens_frame = tk.Frame(control_panel, bg="#12121a")
        sens_frame.pack(fill=tk.X, padx=15, pady=10)

        tk.Label(sens_frame, text="Sensitivity", bg="#12121a", fg="#aaa",
                 font=("Segoe UI", 9)).pack(anchor=tk.W)

        self.sens_var = tk.IntVar(value=self.sensitivity)
        sens_slider = ttk.Scale(
            sens_frame, from_=50, to=400, variable=self.sens_var,
            orient=tk.HORIZONTAL, command=self._on_sens_change
        )
        sens_slider.pack(fill=tk.X, pady=(5, 0))

        self.sens_label = tk.Label(sens_frame, text=f"{self.sensitivity}",
                                   bg="#12121a", fg="#e94560", font=("Segoe UI", 9))
        self.sens_label.pack(anchor=tk.E)

        # Smoothing
        smooth_frame = tk.Frame(control_panel, bg="#12121a")
        smooth_frame.pack(fill=tk.X, padx=15, pady=10)

        tk.Label(smooth_frame, text="Smoothing", bg="#12121a", fg="#aaa",
                 font=("Segoe UI", 9)).pack(anchor=tk.W)

        self.smooth_var = tk.DoubleVar(value=0.15)
        smooth_slider = ttk.Scale(
            smooth_frame, from_=0.05, to=0.5, variable=self.smooth_var,
            orient=tk.HORIZONTAL, command=self._on_smooth_change
        )
        smooth_slider.pack(fill=tk.X, pady=(5, 0))

        # Color Palette
        color_frame = tk.Frame(control_panel, bg="#12121a")
        color_frame.pack(fill=tk.X, padx=15, pady=15)

        tk.Label(color_frame, text="Colors", bg="#12121a", fg="#aaa",
                 font=("Segoe UI", 9)).pack(anchor=tk.W, pady=(0, 5))

        palette_frame = tk.Frame(color_frame, bg="#12121a")
        palette_frame.pack(fill=tk.X)

        for i, color in enumerate(self.COLORS):
            btn = tk.Button(
                palette_frame, bg=color, width=2, height=1, relief=tk.FLAT,
                command=lambda c=color: self._set_color(c)
            )
            btn.grid(row=i // 4, column=i % 4, padx=2, pady=2)

        # Custom color button
        custom_btn = tk.Button(
            color_frame, text="Custom...", bg="#1e1e2e", fg="#aaa",
            relief=tk.FLAT, font=("Segoe UI", 9), command=self._pick_color
        )
        custom_btn.pack(fill=tk.X, pady=(10, 0))

        # Current color indicator
        self.color_indicator = tk.Frame(color_frame, bg=self.brush_color, height=8)
        self.color_indicator.pack(fill=tk.X, pady=(10, 0))

        # Action buttons
        btn_frame = tk.Frame(control_panel, bg="#12121a")
        btn_frame.pack(fill=tk.X, padx=15, pady=20)

        clear_btn = tk.Button(
            btn_frame, text="Clear Canvas", bg="#e94560", fg="white",
            relief=tk.FLAT, font=("Segoe UI", 10, "bold"), pady=8,
            command=self._clear_canvas
        )
        clear_btn.pack(fill=tk.X, pady=(0, 10))

        save_btn = tk.Button(
            btn_frame, text="Export PNG", bg="#1dd1a1", fg="white",
            relief=tk.FLAT, font=("Segoe UI", 10, "bold"), pady=8,
            command=self._save_canvas
        )
        save_btn.pack(fill=tk.X)

        # Toggle drawing
        self.draw_var = tk.BooleanVar(value=True)
        draw_check = tk.Checkbutton(
            btn_frame, text="Enable Drawing", variable=self.draw_var,
            bg="#12121a", fg="#aaa", selectcolor="#1e1e2e",
            font=("Segoe UI", 9), command=self._toggle_drawing
        )
        draw_check.pack(anchor=tk.W, pady=(15, 0))

        # Status
        status_frame = tk.Frame(control_panel, bg="#0a0a0f")
        status_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=10, pady=10)

        self.status_label = tk.Label(
            status_frame, text="Mode: Initializing...",
            bg="#0a0a0f", fg="#666", font=("Segoe UI", 8)
        )
        self.status_label.pack(anchor=tk.W)

        self.sensor_label = tk.Label(
            status_frame, text="X: 0.00  Y: 0.00",
            bg="#0a0a0f", fg="#444", font=("Consolas", 8)
        )
        self.sensor_label.pack(anchor=tk.W)

        # Right panel - Canvas
        canvas_frame = tk.Frame(main_frame, bg="#1a1a2e")
        canvas_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(
            canvas_frame, width=self.canvas_width, height=self.canvas_height,
            bg="white", highlightthickness=2, highlightbackground="#e94560"
        )
        self.canvas.pack(padx=10, pady=10)

        # Draw cursor indicator
        self.cursor_id = self.canvas.create_oval(
            self.cursor_x - 5, self.cursor_y - 5,
            self.cursor_x + 5, self.cursor_y + 5,
            fill="", outline="#e94560", width=2
        )

        # Instructions
        instr_label = tk.Label(
            canvas_frame,
            text="Arrow Keys: Simulate tilt  |  Space: Clear  |  Shake: Change color",
            bg="#1a1a2e", fg="#555", font=("Segoe UI", 9)
        )
        instr_label.pack(pady=(0, 10))

    def _bind_events(self):
        """Bind keyboard events for mock mode."""
        self.root.bind("<KeyPress>", self._on_key_press)
        self.root.bind("<KeyRelease>", self._on_key_release)
        self.root.bind("<space>", lambda e: self._clear_canvas())
        self.root.focus_set()

    def _on_key_press(self, event):
        """Handle key press for mock sensor control."""
        key = event.keysym
        if key in self.mock_keys:
            self.mock_keys[key] = True

    def _on_key_release(self, event):
        """Handle key release."""
        key = event.keysym
        if key in self.mock_keys:
            self.mock_keys[key] = False

    def _update_loop(self):
        """Main update loop (~30Hz)."""
        # Calculate movement based on mode
        move_x, move_y = 0.0, 0.0

        if self.sensor.use_mock:
            # In mock mode, directly use arrow keys for movement
            speed = self.sensitivity * 0.05  # pixels per frame
            if self.mock_keys["Left"]:
                move_x -= speed
            if self.mock_keys["Right"]:
                move_x += speed
            if self.mock_keys["Up"]:
                move_y -= speed
            if self.mock_keys["Down"]:
                move_y += speed
        else:
            # In hardware mode, use sensor data
            state = self.sensor.get_state()
            move_x = state['x'] * self.sensitivity * 0.1
            move_y = state['y'] * self.sensitivity * 0.1

        # Calculate new position
        new_x = self.cursor_x + move_x
        new_y = self.cursor_y + move_y

        # Clamp to canvas bounds
        new_x = max(0, min(self.canvas_width, new_x))
        new_y = max(0, min(self.canvas_height, new_y))

        # Draw line if enabled and moved
        if self.is_drawing and (abs(new_x - self.prev_x) > 0.5 or abs(new_y - self.prev_y) > 0.5):
            # Draw on Tkinter canvas
            self.canvas.create_line(
                self.prev_x, self.prev_y, new_x, new_y,
                fill=self.brush_color, width=self.brush_size,
                capstyle=tk.ROUND, smooth=True
            )
            # Draw on PIL image for saving
            self.pil_draw.line(
                [(self.prev_x, self.prev_y), (new_x, new_y)],
                fill=self.brush_color, width=self.brush_size
            )

        self.prev_x, self.prev_y = new_x, new_y
        self.cursor_x, self.cursor_y = new_x, new_y

        # Update cursor indicator
        self.canvas.coords(
            self.cursor_id,
            self.cursor_x - self.brush_size / 2, self.cursor_y - self.brush_size / 2,
            self.cursor_x + self.brush_size / 2, self.cursor_y + self.brush_size / 2
        )
        self.canvas.itemconfig(self.cursor_id, outline=self.brush_color)

        # Check for shake gesture (color change) - only in hardware mode
        if not self.sensor.use_mock:
            state = self.sensor.get_state()
            if state['shake_time'] > self.last_shake_handled:
                self.last_shake_handled = state['shake_time']
                self._cycle_color()

        # Update status
        mode = "Mock (Arrow Keys)" if self.sensor.use_mock else "Hardware Sensor"
        self.status_label.config(text=f"Mode: {mode}")
        if self.sensor.use_mock:
            self.sensor_label.config(text=f"X: {move_x:.1f}  Y: {move_y:.1f}")
        else:
            state = self.sensor.get_state()
            self.sensor_label.config(text=f"X: {state['x']:.2f}  Y: {state['y']:.2f}")

        # Schedule next update
        self.root.after(33, self._update_loop)  # ~30Hz

    def _on_size_change(self, value):
        self.brush_size = int(float(value))
        self.size_label.config(text=f"{self.brush_size}px")

    def _on_sens_change(self, value):
        self.sensitivity = int(float(value))
        self.sens_label.config(text=f"{self.sensitivity}")

    def _on_smooth_change(self, value):
        self.sensor.set_smoothing(float(value))

    def _set_color(self, color):
        self.brush_color = color
        self.color_indicator.config(bg=color)

    def _pick_color(self):
        color = colorchooser.askcolor(title="Choose Brush Color")[1]
        if color:
            self._set_color(color)

    def _cycle_color(self):
        """Cycle to next color (triggered by shake)."""
        self.color_index = (self.color_index + 1) % len(self.COLORS)
        self._set_color(self.COLORS[self.color_index])

    def _toggle_drawing(self):
        self.is_drawing = self.draw_var.get()

    def _clear_canvas(self):
        """Clear the canvas."""
        self.canvas.delete("all")
        self.pil_image = Image.new("RGB", (self.canvas_width, self.canvas_height), "white")
        self.pil_draw = ImageDraw.Draw(self.pil_image)

        # Recreate cursor
        self.cursor_id = self.canvas.create_oval(
            self.cursor_x - 5, self.cursor_y - 5,
            self.cursor_x + 5, self.cursor_y + 5,
            fill="", outline=self.brush_color, width=2
        )

    def _save_canvas(self):
        """Save canvas as PNG."""
        filepath = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG Image", "*.png")],
            title="Save Artwork"
        )
        if filepath:
            try:
                self.pil_image.save(filepath)
                messagebox.showinfo("Saved", f"Artwork saved to:\n{filepath}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save: {e}")

    def on_close(self):
        """Cleanup on close."""
        self.sensor.stop()
        self.root.destroy()


def main():
    root = tk.Tk()

    # Style configuration
    style = ttk.Style()
    style.theme_use('clam')
    style.configure("TScale", background="#12121a", troughcolor="#1e1e2e")

    app = DriftPaintApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()


if __name__ == "__main__":
    main()
