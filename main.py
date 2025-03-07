from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.progressbar import ProgressBar
from kivy.uix.label import Label
from kivy.core.window import Window
from rembg import remove
from PIL import Image as PILImage
from io import BytesIO
from tkinter import Tk, filedialog
import threading
import os
import datetime

class RembgApp(App):
    def build(self):
        self.root = MainLayout()
        Window.bind(on_dropfile=self.on_drop_file)
        return self.root

    def on_drop_file(self, window, file_path):
        file_path = file_path.decode("utf-8")
        self.root.handle_file_drop(file_path)

class MainLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.progress.value = 0
        self.progress_label.text = "Ingen behandling"

    def open_filechooser(self):
        Tk().withdraw()
        file_path = filedialog.askopenfilename(filetypes=[("Billeder", "*.png *.jpg *.jpeg *.webp")])
        if file_path:
            self.image_path = file_path
            self.ids.image_widget.source = file_path
            self.ids.image_widget.reload()

    def handle_file_drop(self, file_path):
        if os.path.isfile(file_path) and file_path.lower().endswith(('png', 'jpg', 'jpeg', 'webp')):
            self.image_path = file_path
            self.ids.image_widget.source = file_path
            self.ids.image_widget.reload()

    def process_image(self, output_directory):
        try:
            with PILImage.open(self.image_path) as img:
                output = remove(img)
                output_path = os.path.join(output_directory, os.path.basename(self.image_path).replace(".jpg", "_no_bg.png"))
                output.save(output_path)
                self.ids.image_widget.source = output_path
                self.ids.image_widget.reload()
                self.ids.progress_label.text = "Færdig!"
        except Exception as e:
            self.ids.progress_label.text = f"Fejl: {str(e)}"