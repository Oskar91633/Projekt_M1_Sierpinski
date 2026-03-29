import tkinter as tk
from tkinter import ttk, filedialog, messagebox

import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure

from spiral import generate_spiral
from sierpinski import collect_sierpinski_triangles


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Projekt M1 - Wizualizacja i Animacja Struktur Algorytmicznych")
        self.root.geometry("1300x800")
        self.root.minsize(1100, 700)

        self.animation_running = False
        self.animation_paused = False
        self.job = None
        self.frame = 0
        self.current_animation_mode = None

        self.spiral_x = None
        self.spiral_y = None
        self.sierpinski_levels = []

        self.build_ui()
        self.update_description()
        self.update_control_states()
        self.redraw_current_static_view()

    def build_ui(self):
        container = ttk.Frame(self.root, padding=10)
        container.pack(fill="both", expand=True)

        control_panel = ttk.Frame(container)
        control_panel.pack(side="left", fill="y", padx=(0, 10))

        plot_panel = ttk.Frame(container)
        plot_panel.pack(side="right", fill="both", expand=True)

        title = ttk.Label(
            control_panel,
            text="Panel sterowania",
            font=("Arial", 16, "bold")
        )
        title.pack(anchor="w", pady=(0, 10))

        mode_frame = ttk.LabelFrame(control_panel, text="Tryb pracy", padding=10)
        mode_frame.pack(fill="x", pady=5)

        self.mode_var = tk.StringVar(value="spiral_static")

        modes = [
            ("Spirala statyczna", "spiral_static"),
            ("Spirala animowana", "spiral_animated"),
            ("Sierpiński statyczny", "sierpinski_static"),
            ("Sierpiński animowany", "sierpinski_animated"),
        ]

        for text, value in modes:
            ttk.Radiobutton(
                mode_frame,
                text=text,
                value=value,
                variable=self.mode_var,
                command=self.on_mode_change
            ).pack(anchor="w", pady=2)

        spiral_frame = ttk.LabelFrame(control_panel, text="Parametry spirali", padding=10)
        spiral_frame.pack(fill="x", pady=5)

        ttk.Label(spiral_frame, text="Skala a").pack(anchor="w")
        self.a_scale = tk.Scale(
            spiral_frame,
            from_=0.05,
            to=1.0,
            resolution=0.01,
            orient="horizontal",
            command=self.on_scale_change
        )
        self.a_scale.set(0.2)
        self.a_scale.pack(fill="x")

        ttk.Label(spiral_frame, text="Maksymalne t").pack(anchor="w")
        self.t_scale = tk.Scale(
            spiral_frame,
            from_=6.28,
            to=62.8,
            resolution=0.1,
            orient="horizontal",
            command=self.on_scale_change
        )
        self.t_scale.set(31.4)
        self.t_scale.pack(fill="x")

        ttk.Label(spiral_frame, text="Liczba punktów").pack(anchor="w")
        self.points_scale = tk.Scale(
            spiral_frame,
            from_=100,
            to=5000,
            resolution=100,
            orient="horizontal",
            command=self.on_scale_change
        )
        self.points_scale.set(1000)
        self.points_scale.pack(fill="x")

        sierpinski_frame = ttk.LabelFrame(control_panel, text="Parametry Sierpińskiego", padding=10)
        sierpinski_frame.pack(fill="x", pady=5)

        ttk.Label(sierpinski_frame, text="Poziom rekurencji").pack(anchor="w")
        self.level_scale = tk.Scale(
            sierpinski_frame,
            from_=0,
            to=7,
            resolution=1,
            orient="horizontal",
            command=self.on_scale_change
        )
        self.level_scale.set(4)
        self.level_scale.pack(fill="x")

        animation_frame = ttk.LabelFrame(control_panel, text="Animacja", padding=10)
        animation_frame.pack(fill="x", pady=5)

        ttk.Label(animation_frame, text="Opóźnienie [ms]").pack(anchor="w")
        self.delay_scale = tk.Scale(
            animation_frame,
            from_=1,
            to=200,
            resolution=1,
            orient="horizontal",
            command=self.on_delay_change
        )
        self.delay_scale.set(30)
        self.delay_scale.pack(fill="x")

        buttons_frame = ttk.LabelFrame(control_panel, text="Akcje", padding=10)
        buttons_frame.pack(fill="x", pady=5)

        self.start_button = ttk.Button(buttons_frame, text="Start animacji", command=self.start)
        self.start_button.pack(fill="x", pady=3)

        self.pause_button = ttk.Button(buttons_frame, text="Pauza / Wznów", command=self.pause_resume)
        self.pause_button.pack(fill="x", pady=3)

        self.stop_button = ttk.Button(buttons_frame, text="Stop", command=self.stop)
        self.stop_button.pack(fill="x", pady=3)

        self.reset_button = ttk.Button(buttons_frame, text="Reset widoku", command=self.reset_plot)
        self.reset_button.pack(fill="x", pady=3)

        self.save_button = ttk.Button(buttons_frame, text="Zapisz PNG", command=self.save_png)
        self.save_button.pack(fill="x", pady=3)

        desc_frame = ttk.LabelFrame(control_panel, text="Opis trybu", padding=10)
        desc_frame.pack(fill="both", expand=True, pady=5)

        self.desc_label = ttk.Label(
            desc_frame,
            text="",
            wraplength=320,
            justify="left"
        )
        self.desc_label.pack(anchor="nw")

        self.figure = Figure(figsize=(8, 6), dpi=100)
        self.ax = self.figure.add_subplot(111)

        self.canvas = FigureCanvasTkAgg(self.figure, master=plot_panel)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        toolbar = NavigationToolbar2Tk(self.canvas, plot_panel)
        toolbar.update()

    def update_description(self):
        descriptions = {
            "spiral_static": (
                "Tryb statyczny w czasie rzeczywistym.\n\n"
                "Porusz suwakami spirali, a wykres zmieni się od razu."
            ),
            "spiral_animated": (
                "Animacja spirali Archimedesa.\n\n"
                "W czasie animacji możesz zmieniać suwak opóźnienia."
            ),
            "sierpinski_static": (
                "Tryb statyczny w czasie rzeczywistym.\n\n"
                "Porusz suwakiem poziomu rekurencji, a fraktal zmieni się od razu."
            ),
            "sierpinski_animated": (
                "Animacja Trójkąta Sierpińskiego.\n\n"
                "W czasie animacji możesz zmieniać suwak opóźnienia."
            ),
        }
        self.desc_label.config(text=descriptions[self.mode_var.get()])

    def update_control_states(self):
        mode = self.mode_var.get()

        spiral_mode = mode in ("spiral_static", "spiral_animated")
        sierpinski_mode = mode in ("sierpinski_static", "sierpinski_animated")
        animated_mode = mode in ("spiral_animated", "sierpinski_animated")
        static_mode = mode in ("spiral_static", "sierpinski_static")

        self.a_scale.config(state="normal" if spiral_mode else "disabled")
        self.t_scale.config(state="normal" if spiral_mode else "disabled")
        self.points_scale.config(state="normal" if spiral_mode else "disabled")
        self.level_scale.config(state="normal" if sierpinski_mode else "disabled")
        self.delay_scale.config(state="normal" if animated_mode else "disabled")

        if static_mode:
            self.start_button.state(["disabled"])
        else:
            self.start_button.state(["!disabled"])

        if animated_mode:
            self.pause_button.state(["!disabled"])
            self.stop_button.state(["!disabled"])
        else:
            self.pause_button.state(["disabled"])
            self.stop_button.state(["disabled"])

    def get_values(self):
        a = max(0.01, float(self.a_scale.get()))
        t_max = max(1.0, float(self.t_scale.get()))
        points = max(100, int(float(self.points_scale.get())))
        level = max(0, min(7, int(float(self.level_scale.get()))))
        delay = max(1, int(float(self.delay_scale.get())))
        return a, t_max, points, level, delay

    def prepare_empty_plot(self):
        self.ax.clear()
        self.ax.set_title("Obszar wizualizacji")
        self.ax.set_xlabel("X")
        self.ax.set_ylabel("Y")
        self.ax.grid(True)
        self.ax.set_aspect("equal")
        self.canvas.draw_idle()

    def stop(self):
        self.animation_running = False
        self.animation_paused = False
        self.current_animation_mode = None
        if self.job is not None:
            self.root.after_cancel(self.job)
            self.job = None

    def reset_plot(self):
        self.stop()
        self.frame = 0
        self.spiral_x = None
        self.spiral_y = None
        self.sierpinski_levels = []
        self.redraw_current_static_view()

    def save_png(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG image", "*.png")],
            title="Zapisz wykres jako PNG"
        )
        if file_path:
            self.figure.savefig(file_path, dpi=200, bbox_inches="tight")
            messagebox.showinfo("Zapisano", "Obraz został zapisany poprawnie.")

    def on_mode_change(self):
        self.stop()
        self.update_description()
        self.update_control_states()
        self.redraw_current_static_view()

    def on_scale_change(self, _=None):
        if self.mode_var.get() in ("spiral_static", "sierpinski_static"):
            self.redraw_current_static_view()

    def on_delay_change(self, _=None):
        if self.animation_running:
            self.restart_animation_timer()

    def restart_animation_timer(self):
        if not self.animation_running or self.current_animation_mode is None:
            return

        if self.job is not None:
            self.root.after_cancel(self.job)
            self.job = None

        delay = self.get_values()[4]

        if self.current_animation_mode == "spiral_animated":
            self.job = self.root.after(delay, lambda: self.animate_spiral())
        elif self.current_animation_mode == "sierpinski_animated":
            self.job = self.root.after(delay, lambda: self.animate_sierpinski())

    def redraw_current_static_view(self):
        a, t_max, points, level, _ = self.get_values()
        mode = self.mode_var.get()

        if mode == "spiral_static":
            self.draw_spiral_static(a, t_max, points)
        elif mode == "sierpinski_static":
            self.draw_sierpinski_static(level)
        else:
            self.prepare_empty_plot()

    def start(self):
        self.stop()
        self.frame = 0

        a, t_max, points, level, _ = self.get_values()
        mode = self.mode_var.get()

        if mode == "spiral_animated":
            self.start_spiral_animation(a, t_max, points)
        elif mode == "sierpinski_animated":
            self.start_sierpinski_animation(level)

    def pause_resume(self):
        mode = self.mode_var.get()
        if mode not in ("spiral_animated", "sierpinski_animated"):
            return

        if not self.animation_running and not self.animation_paused:
            return

        if self.animation_running:
            self.animation_paused = True
            self.animation_running = False
            if self.job is not None:
                self.root.after_cancel(self.job)
                self.job = None
        else:
            self.animation_paused = False
            self.animation_running = True
            self.restart_animation_timer()

    def draw_spiral_static(self, a, t_max, points):
        x, y = generate_spiral(a, t_max, points)

        self.ax.clear()
        self.ax.plot(x, y, linewidth=2)
        self.ax.set_title("Spirala Archimedesa - statycznie (real-time)")
        self.ax.set_xlabel("X")
        self.ax.set_ylabel("Y")
        self.ax.grid(True)
        self.ax.set_aspect("equal")
        self.canvas.draw_idle()

    def start_spiral_animation(self, a, t_max, points):
        self.spiral_x, self.spiral_y = generate_spiral(a, t_max, points)
        self.animation_running = True
        self.animation_paused = False
        self.current_animation_mode = "spiral_animated"

        self.ax.clear()
        self.ax.set_title("Spirala Archimedesa - animacja")
        self.ax.set_xlabel("X")
        self.ax.set_ylabel("Y")
        self.ax.grid(True)
        self.ax.set_aspect("equal")

        margin = 0.5
        self.ax.set_xlim(np.min(self.spiral_x) - margin, np.max(self.spiral_x) + margin)
        self.ax.set_ylim(np.min(self.spiral_y) - margin, np.max(self.spiral_y) + margin)

        self.line, = self.ax.plot([], [], linewidth=2)
        self.canvas.draw_idle()

        self.animate_spiral()

    def animate_spiral(self):
        if not self.animation_running:
            return

        self.line.set_data(
            self.spiral_x[: self.frame + 1],
            self.spiral_y[: self.frame + 1]
        )
        self.canvas.draw_idle()

        self.frame += 1
        if self.frame < len(self.spiral_x):
            delay = self.get_values()[4]
            self.job = self.root.after(delay, lambda: self.animate_spiral())
        else:
            self.animation_running = False
            self.job = None
            self.current_animation_mode = None

    def draw_sierpinski_static(self, level):
        p1 = (0, 0)
        p2 = (1, 0)
        p3 = (0.5, 0.86602540378)

        triangles = collect_sierpinski_triangles(p1, p2, p3, level)

        self.ax.clear()
        for triangle in triangles:
            x = [triangle[0][0], triangle[1][0], triangle[2][0], triangle[0][0]]
            y = [triangle[0][1], triangle[1][1], triangle[2][1], triangle[0][1]]
            self.ax.fill(x, y, color="black")

        self.ax.set_title(f"Trójkąt Sierpińskiego - poziom {level} (real-time)")
        self.ax.set_xlim(0, 1)
        self.ax.set_ylim(0, 0.9)
        self.ax.set_aspect("equal")
        self.ax.axis("off")
        self.canvas.draw_idle()

    def start_sierpinski_animation(self, max_level):
        p1 = (0, 0)
        p2 = (1, 0)
        p3 = (0.5, 0.86602540378)

        self.sierpinski_levels = []
        for level in range(max_level + 1):
            triangles = collect_sierpinski_triangles(p1, p2, p3, level)
            self.sierpinski_levels.append(triangles)

        self.animation_running = True
        self.animation_paused = False
        self.current_animation_mode = "sierpinski_animated"
        self.animate_sierpinski()

    def animate_sierpinski(self):
        if not self.animation_running:
            return

        self.ax.clear()

        triangles = self.sierpinski_levels[self.frame]
        for triangle in triangles:
            x = [triangle[0][0], triangle[1][0], triangle[2][0], triangle[0][0]]
            y = [triangle[0][1], triangle[1][1], triangle[2][1], triangle[0][1]]
            self.ax.fill(x, y, color="black")

        self.ax.set_title(f"Trójkąt Sierpińskiego - poziom {self.frame}")
        self.ax.set_xlim(0, 1)
        self.ax.set_ylim(0, 0.9)
        self.ax.set_aspect("equal")
        self.ax.axis("off")
        self.canvas.draw_idle()

        self.frame += 1
        if self.frame < len(self.sierpinski_levels):
            delay = self.get_values()[4]
            self.job = self.root.after(delay, lambda: self.animate_sierpinski())
        else:
            self.animation_running = False
            self.job = None
            self.current_animation_mode = None


def main():
    root = tk.Tk()
    app = App(root)
    root.mainloop()


if __name__ == "__main__":
    main()