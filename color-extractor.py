import tkinter as tk
from tkinter import filedialog
from PIL import Image
import numpy as np
import math
from sklearn.cluster import KMeans

DEFAULT_GEOMETRY = "400x190"
DEFAULT_POSITION = "+100+100"
COLUMNS_PER_ROW = 3
def_weight, def_height = DEFAULT_GEOMETRY.split("x")

def count_row_height(number,div_by):
    if number <= div_by:
        return 1
    else:
        return math.ceil(number / div_by)

class ColorExtractorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Color Extractor")
        self.root.geometry(f"{DEFAULT_GEOMETRY}{DEFAULT_POSITION}")
        self.root.minsize(def_weight, def_height)

        self.original_pixels = None
        self.create_widgets()

    def create_widgets(self):
        self.top_frame = tk.Frame(self.root)
        self.top_frame.pack(pady=10)

        self.load_button = tk.Button(self.top_frame, text="Load Image", command=self.load_image)
        self.slider = tk.Scale(self.top_frame, from_=1, to=15, orient=tk.HORIZONTAL,
                               label="Number of Colors", length=200, command=self.slider_changed)
        self.slider.set(9)
        self.reset_button = tk.Button(self.top_frame, text="Reset", command=self.reset, state=tk.DISABLED)


        self.load_button.grid(row=0, column=3, sticky="ew", padx=5, pady=(0,5)) 
        self.slider.grid(row=0, column=0,rowspan=2, columnspan=3, sticky="ew", padx=5, pady=(0,5)) 
        self.reset_button.grid(row=1, column=3, sticky="ew", padx=5)
        self.display_frame = tk.Frame(self.root)
        self.display_frame.pack(pady=10)

        self.feedback_label = tk.Label(self.root, text="", fg="green")
        self.feedback_label.pack()

    def load_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp")])
        if not file_path:
            return

        img = Image.open(file_path).resize((150, 150))
        self.original_pixels = np.array(img).reshape(-1, 3)
        self.update_colors()
        self.reset_button.config(state=tk.NORMAL)

    def reset(self):
        for widget in self.display_frame.winfo_children():
            widget.destroy()
        self.original_pixels = None
        self.root.geometry(f"{DEFAULT_GEOMETRY}{DEFAULT_POSITION}")
        self.feedback_label.config(text="")

    def slider_changed(self, value):
        if self.original_pixels is not None:
            self.update_colors()

    def update_colors(self):
        num_colors = self.slider.get()
        sorted_colors = self.extract_colors_sorted_by_percentage(num_colors)
        self.display_colors(sorted_colors)

    def extract_colors_sorted_by_percentage(self, num_colors):
        kmeans = KMeans(n_clusters=num_colors, n_init='auto')
        labels = kmeans.fit_predict(self.original_pixels)
        counts = np.bincount(labels)
        percentages = counts / len(self.original_pixels)

        # Combine color and percentage
        color_info = []
        for idx, (color, pct) in enumerate(zip(kmeans.cluster_centers_, percentages)):
            rgb = tuple(color.astype(int))
            hex_color = '#{:02x}{:02x}{:02x}'.format(*rgb)
            color_info.append((hex_color, pct))

        # Sort by percentage descending
        color_info.sort(key=lambda x: x[1], reverse=True)
        return color_info

    def display_colors(self, color_info):
        custom_height = count_row_height(len(color_info),COLUMNS_PER_ROW)
        for widget in self.display_frame.winfo_children():
            widget.destroy()

        row = 0
        col = 0
        for hex_color, pct in color_info:
            #display_text = f"{hex_color} ({pct*100:.1f}%)"
            display_text = f"{hex_color}"

            # Dot (40x40)
            dot = tk.Canvas(self.display_frame, width=42, height=42, bg=self.display_frame["bg"], highlightthickness=0)
            oval = dot.create_oval(5, 5, 40, 40, fill=hex_color, outline=hex_color)
            dot.grid(row=row, column=col, padx=10, pady=4)
            dot.tag_bind(oval, "<Button-1>", lambda e, c=hex_color: self.copy_to_clipboard(c))

            # Label
            label = tk.Label(self.display_frame, text=display_text, cursor="hand2")
            label.grid(row=row + 1, column=col, padx=10, pady=2)
            label.bind("<Button-1>", lambda e, c=hex_color: self.copy_to_clipboard(c))

            col += 1
            if col == COLUMNS_PER_ROW: 
                row += 2
                col = 0

        required_height = str(int(def_height) + (custom_height * 65 ) + 20 )
        self.root.geometry(f"{def_weight}x{required_height}{DEFAULT_POSITION}")

    def copy_to_clipboard(self, text):
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        self.feedback_label.config(text=f"Copied: {text}")
        self.root.after(1500, lambda: self.feedback_label.config(text=""))

if __name__ == '__main__':
    root = tk.Tk()
    app = ColorExtractorApp(root)
    root.mainloop()
