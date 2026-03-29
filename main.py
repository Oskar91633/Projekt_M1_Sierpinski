from PIL import Image, ImageTk
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure

from spiral import generate_spiral
from sierpinski import collect_sierpinski_triangles


class ScrollableFrame(ttk.Frame):
    def __init__(self, parent, width=360, height=800):
        super().__init__(parent)

        self.canvas = tk.Canvas(self, highlightthickness=0, width=width, height=height)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)

        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.window_id = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")

        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.canvas.bind("<Configure>", self._on_canvas_configure)

        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)      # Windows
        self.canvas.bind_all("<Button-4>", self._on_mousewheel_linux)  # Linux up
        self.canvas.bind_all("<Button-5>", self._on_mousewheel_linux)  # Linux down

    def _on_canvas_configure(self, event):
        self.canvas.itemconfig(self.window_id, width=event.width)

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _on_mousewheel_linux(self, event):
        if event.num == 4:
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5:
            self.canvas.yview_scroll(1, "units")


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Projekt M1 - Wizualizacja i Animacja Struktur Algorytmicznych")
        self.root.geometry("1380x850")
        self.root.minsize(1180, 760)

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
        self.apply_theme()
        self.redraw_current_view()
    
    def build_ui(self):
        container = ttk.Frame(self.root, padding=10)
        container.pack(fill="both", expand=True)

        left_panel = ScrollableFrame(container, width=380, height=800)
        left_panel.pack(side="left", fill="y", padx=(0, 10))

        control_panel = left_panel.scrollable_frame

        plot_panel = ttk.Frame(container)
        plot_panel.pack(side="right", fill="both", expand=True)

        # ===== LOGO =====
        image = Image.open("logo.jpg")
        image = image.resize((200, 80))  # zmienisz rozmiar jak chcesz
        self.logo_img = ImageTk.PhotoImage(image)

        logo_label = ttk.Label(control_panel, image=self.logo_img)
        logo_label.pack(pady=(0, 10))

        title = ttk.Label(
            control_panel,
            text="Panel sterowania",
            font=("Arial", 16, "bold")
        )
        title.pack(anchor="w", pady=(0, 10), padx=5)

        mode_frame = ttk.LabelFrame(control_panel, text="Tryb pracy", padding=10)
        mode_frame.pack(fill="x", pady=5, padx=5)

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
        spiral_frame.pack(fill="x", pady=5, padx=5)

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

        self.show_points_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            spiral_frame,
            text="Pokaż punkty spirali",
            variable=self.show_points_var,
            command=self.on_scale_change
        ).pack(anchor="w", pady=(5, 0))

        sierpinski_frame = ttk.LabelFrame(control_panel, text="Parametry Sierpińskiego", padding=10)
        sierpinski_frame.pack(fill="x", pady=5, padx=5)

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
        animation_frame.pack(fill="x", pady=5, padx=5)

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
        buttons_frame.pack(fill="x", pady=8, padx=5)

        self.start_button = ttk.Button(buttons_frame, text="Start / Rysuj", command=self.start)
        self.start_button.pack(fill="x", pady=4)

        self.pause_button = ttk.Button(buttons_frame, text="Pauza / Wznów", command=self.pause_resume)
        self.pause_button.pack(fill="x", pady=4)

        self.stop_button = ttk.Button(buttons_frame, text="Stop", command=self.stop)
        self.stop_button.pack(fill="x", pady=4)

        self.reset_button = ttk.Button(buttons_frame, text="Reset widoku", command=self.reset_plot)
        self.reset_button.pack(fill="x", pady=4)

        self.save_button = ttk.Button(buttons_frame, text="Zapisz PNG", command=self.save_png)
        self.save_button.pack(fill="x", pady=4)

        info_frame = ttk.LabelFrame(control_panel, text="Informacje", padding=10)
        info_frame.pack(fill="x", pady=8, padx=5)

        self.status_var = tk.StringVar(value="Tryb gotowy.")
        self.frame_var = tk.StringVar(value="Klatka / poziom: -")
        self.count_var = tk.StringVar(value="Liczba elementów: -")

        ttk.Label(info_frame, textvariable=self.status_var, wraplength=320, justify="left").pack(anchor="w", pady=2)
        ttk.Label(info_frame, textvariable=self.frame_var).pack(anchor="w", pady=2)
        ttk.Label(info_frame, textvariable=self.count_var).pack(anchor="w", pady=2)

        desc_frame = ttk.LabelFrame(control_panel, text="Opis trybu", padding=10)
        desc_frame.pack(fill="x", pady=8, padx=5)

        self.desc_label = ttk.Label(
            desc_frame,
            text="",
            wraplength=320,
            justify="left"
        )
        self.desc_label.pack(anchor="nw")

        appearance_frame = ttk.LabelFrame(control_panel, text="Wygląd", padding=10)
        appearance_frame.pack(fill="x", pady=8, padx=5)

        self.theme_var = tk.StringVar(value="dark")
        ttk.Radiobutton(
            appearance_frame,
            text="Motyw ciemny",
            value="dark",
            variable=self.theme_var,
            command=self.on_theme_change
        ).pack(anchor="w", pady=2)
        ttk.Radiobutton(
            appearance_frame,
            text="Motyw jasny",
            value="light",
            variable=self.theme_var,
            command=self.on_theme_change
        ).pack(anchor="w", pady=2)

        bottom_space = ttk.Frame(control_panel, height=10)
        bottom_space.pack(fill="x", pady=5)

        self.figure = Figure(figsize=(8, 6), dpi=100)
        self.ax = self.figure.add_subplot(111)

        self.canvas = FigureCanvasTkAgg(self.figure, master=plot_panel)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        toolbar = NavigationToolbar2Tk(self.canvas, plot_panel)
        toolbar.update()

    def current_colors(self):
        if self.theme_var.get() == "dark":
            return {
                "fig_bg": "#111827",
                "ax_bg": "#1f2937",
                "grid": "#374151",
                "text": "#f9fafb",
                "spiral": "#60a5fa",
                "points": "#f59e0b",
                "triangles": [
                    "#60a5fa",
                    "#34d399",
                    "#fbbf24",
                    "#f87171",
                    "#a78bfa",
                    "#22d3ee",
                    "#fb7185",
                    "#4ade80",
                ],
            }
        return {
            "fig_bg": "#ffffff",
            "ax_bg": "#f8fafc",
            "grid": "#cbd5e1",
            "text": "#111827",
            "spiral": "#2563eb",
            "points": "#d97706",
            "triangles": [
                "#2563eb",
                "#059669",
                "#d97706",
                "#dc2626",
                "#7c3aed",
                "#0891b2",
                "#db2777",
                "#16a34a",
            ],
        }

    def apply_theme(self):
        colors = self.current_colors()
        self.figure.patch.set_facecolor(colors["fig_bg"])
        self.ax.set_facecolor(colors["ax_bg"])
        self.canvas.draw_idle()

    def update_description(self):
        descriptions = {
            "spiral_static": (
                "Tryb statyczny w czasie rzeczywistym.\n\n"
                "Porusz suwakami spirali, a wykres zmieni się od razu."
            ),
            "spiral_animated": (
                "Animacja spirali Archimedesa.\n\n"
                "W czasie animacji możesz zmieniać prędkość suwakiem opóźnienia."
            ),
            "sierpinski_static": (
                "Tryb statyczny w czasie rzeczywistym.\n\n"
                "Porusz suwakiem poziomu rekurencji, a fraktal zmieni się od razu."
            ),
            "sierpinski_animated": (
                "Animacja Trójkąta Sierpińskiego.\n\n"
                "Każdy kolejny etap pokazuje wzrost złożoności fraktala."
            ),
        }
        self.desc_label.config(text=descriptions[self.mode_var.get()])

    def get_values(self):
        a = max(0.01, float(self.a_scale.get()))
        t_max = max(1.0, float(self.t_scale.get()))
        points = max(100, int(float(self.points_scale.get())))
        level = max(0, min(7, int(float(self.level_scale.get()))))
        delay = max(1, int(float(self.delay_scale.get())))
        return a, t_max, points, level, delay

    def style_axes_for_cartesian(self, title):
        colors = self.current_colors()
        self.ax.clear()
        self.ax.set_facecolor(colors["ax_bg"])
        self.ax.set_title(title, color=colors["text"])
        self.ax.set_xlabel("X", color=colors["text"])
        self.ax.set_ylabel("Y", color=colors["text"])
        self.ax.grid(True, color=colors["grid"], alpha=0.6)
        self.ax.set_aspect("equal")
        self.ax.tick_params(colors=colors["text"])

    def style_axes_for_fractal(self, title):
        colors = self.current_colors()
        self.ax.clear()
        self.ax.set_facecolor(colors["ax_bg"])
        self.ax.set_title(title, color=colors["text"])
        self.ax.set_xlim(0, 1)
        self.ax.set_ylim(0, 0.9)
        self.ax.set_aspect("equal")
        self.ax.axis("off")

    def prepare_empty_plot(self):
        self.style_axes_for_cartesian("Obszar wizualizacji")
        self.canvas.draw_idle()

    def stop(self):
        self.animation_running = False
        self.animation_paused = False
        self.current_animation_mode = None
        self.status_var.set("Animacja zatrzymana.")
        if self.job is not None:
            self.root.after_cancel(self.job)
            self.job = None

    def reset_plot(self):
        self.stop()
        self.frame = 0
        self.spiral_x = None
        self.spiral_y = None
        self.sierpinski_levels = []
        self.frame_var.set("Klatka / poziom: -")
        self.count_var.set("Liczba elementów: -")
        self.redraw_current_view()

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
        self.redraw_current_view()

    def on_theme_change(self):
        self.apply_theme()
        self.redraw_current_view()

    def on_scale_change(self, _=None):
        if self.mode_var.get() in ("spiral_static", "sierpinski_static"):
            self.redraw_current_view()

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
            self.job = self.root.after(delay, self.animate_spiral)
        elif self.current_animation_mode == "sierpinski_animated":
            self.job = self.root.after(delay, self.animate_sierpinski)

    def redraw_current_view(self):
        a, t_max, points, level, _ = self.get_values()
        mode = self.mode_var.get()

        if mode == "spiral_static":
            self.draw_spiral_static(a, t_max, points)
        elif mode == "sierpinski_static":
            self.draw_sierpinski_static(level)
        else:
            self.prepare_empty_plot()
            self.status_var.set("Tryb animowany gotowy do uruchomienia.")
            self.frame_var.set("Klatka / poziom: -")
            self.count_var.set("Liczba elementów: -")

    def start(self):
        self.stop()
        self.frame = 0

        a, t_max, points, level, _ = self.get_values()
        mode = self.mode_var.get()

        if mode == "spiral_static":
            self.draw_spiral_static(a, t_max, points)
        elif mode == "spiral_animated":
            self.start_spiral_animation(a, t_max, points)
        elif mode == "sierpinski_static":
            self.draw_sierpinski_static(level)
        elif mode == "sierpinski_animated":
            self.start_sierpinski_animation(level)

    def pause_resume(self):
        mode = self.mode_var.get()
        if mode not in ("spiral_animated", "sierpinski_animated"):
            self.status_var.set("Pauza działa tylko dla trybów animowanych.")
            return

        if not self.animation_running and not self.animation_paused:
            return

        if self.animation_running:
            self.animation_paused = True
            self.animation_running = False
            self.status_var.set("Animacja wstrzymana.")
            if self.job is not None:
                self.root.after_cancel(self.job)
                self.job = None
        else:
            self.animation_paused = False
            self.animation_running = True
            self.status_var.set("Animacja wznowiona.")
            self.restart_animation_timer()

    def draw_spiral_static(self, a, t_max, points):
        colors = self.current_colors()
        x, y = generate_spiral(a, t_max, points)

        self.style_axes_for_cartesian("Spirala Archimedesa - statycznie (real-time)")
        self.ax.plot(x, y, linewidth=2.5, color=colors["spiral"])

        if self.show_points_var.get():
            step = max(1, points // 150)
            self.ax.scatter(x[::step], y[::step], s=12, color=colors["points"])

        self.canvas.draw_idle()

        self.status_var.set("Tryb statyczny spirali aktywny.")
        self.frame_var.set("Klatka / poziom: statyczny")
        self.count_var.set(f"Liczba punktów: {points}")

    def start_spiral_animation(self, a, t_max, points):
        colors = self.current_colors()
        self.spiral_x, self.spiral_y = generate_spiral(a, t_max, points)
        self.animation_running = True
        self.animation_paused = False
        self.current_animation_mode = "spiral_animated"

        self.style_axes_for_cartesian("Spirala Archimedesa - animacja")

        margin = 0.5
        self.ax.set_xlim(np.min(self.spiral_x) - margin, np.max(self.spiral_x) + margin)
        self.ax.set_ylim(np.min(self.spiral_y) - margin, np.max(self.spiral_y) + margin)

        self.line, = self.ax.plot([], [], linewidth=2.5, color=colors["spiral"])
        self.canvas.draw_idle()

        self.status_var.set("Animacja spirali uruchomiona.")
        self.animate_spiral()

    def animate_spiral(self):
        if not self.animation_running:
            return

        self.line.set_data(
            self.spiral_x[: self.frame + 1],
            self.spiral_y[: self.frame + 1]
        )

        self.canvas.draw_idle()

        self.frame_var.set(f"Klatka / poziom: {self.frame}")
        self.count_var.set(f"Narysowane punkty: {self.frame + 1}")

        self.frame += 1
        if self.frame < len(self.spiral_x):
            delay = self.get_values()[4]
            self.job = self.root.after(delay, self.animate_spiral)
        else:
            self.animation_running = False
            self.job = None
            self.current_animation_mode = None
            self.status_var.set("Animacja spirali zakończona.")

    def triangle_color(self, level):
        colors = self.current_colors()
        palette = colors["triangles"]
        return palette[level % len(palette)]

    def draw_sierpinski_static(self, level):
        p1 = (0, 0)
        p2 = (1, 0)
        p3 = (0.5, 0.86602540378)

        triangles = collect_sierpinski_triangles(p1, p2, p3, level)

        self.style_axes_for_fractal(f"Trójkąt Sierpińskiego - poziom {level} (real-time)")

        color = self.triangle_color(level)
        for triangle in triangles:
            x = [triangle[0][0], triangle[1][0], triangle[2][0], triangle[0][0]]
            y = [triangle[0][1], triangle[1][1], triangle[2][1], triangle[0][1]]
            self.ax.fill(x, y, color=color, edgecolor=color)

        self.canvas.draw_idle()

        self.status_var.set("Tryb statyczny Sierpińskiego aktywny.")
        self.frame_var.set(f"Klatka / poziom: {level}")
        self.count_var.set(f"Liczba trójkątów: {len(triangles)}")

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
        self.status_var.set("Animacja Sierpińskiego uruchomiona.")
        self.animate_sierpinski()

    def animate_sierpinski(self):
        if not self.animation_running:
            return

        triangles = self.sierpinski_levels[self.frame]
        self.style_axes_for_fractal(f"Trójkąt Sierpińskiego - poziom {self.frame}")

        color = self.triangle_color(self.frame)
        for triangle in triangles:
            x = [triangle[0][0], triangle[1][0], triangle[2][0], triangle[0][0]]
            y = [triangle[0][1], triangle[1][1], triangle[2][1], triangle[0][1]]
            self.ax.fill(x, y, color=color, edgecolor=color)

        self.canvas.draw_idle()

        self.frame_var.set(f"Klatka / poziom: {self.frame}")
        self.count_var.set(f"Liczba trójkątów: {len(triangles)}")

        self.frame += 1
        if self.frame < len(self.sierpinski_levels):
            delay = self.get_values()[4]
            self.job = self.root.after(delay, self.animate_sierpinski)
        else:
            self.animation_running = False
            self.job = None
            self.current_animation_mode = None
            self.status_var.set("Animacja Sierpińskiego zakończona.")


def main():
    root = tk.Tk()
    app = App(root)
    root.mainloop()


if __name__ == "__main__":
    main()