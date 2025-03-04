from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.progressbar import ProgressBar
from kivy.uix.label import Label
from kivy.uix.behaviors import DragBehavior
from kivy.core.window import Window
from rembg import remove
from PIL import Image as PILImage
from io import BytesIO
from tkinter import Tk, filedialog
import threading
import os
import shutil
import datetime


class DraggableImage(DragBehavior, Image):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.drag_rectangle = self.x, self.y, self.width, self.height
        self.drag_timeout = 100000
        self.drag_distance = 0


class RembgApp(App):
    def build(self):
        self.layout = BoxLayout(orientation='vertical', spacing=10, padding=10)
        Window.bind(on_dropfile=self.on_drop_file)

        self.image_widget = DraggableImage(size_hint=(1, 0.7), allow_stretch=True, keep_ratio=True)
        self.layout.add_widget(self.image_widget)

        self.progress = ProgressBar(max=100, size_hint=(1, 0.05))
        self.layout.add_widget(self.progress)
        self.progress_label = Label(text="Ingen behandling", size_hint=(1, 0.05))
        self.layout.add_widget(self.progress_label)

        self.select_button = Button(text="Vælg billede eller mappe", size_hint=(1, 0.1))
        self.select_button.bind(on_press=self.open_filechooser)
        self.layout.add_widget(self.select_button)

        self.remove_bg_button = Button(text="Fjern baggrund", size_hint=(1, 0.1))
        self.remove_bg_button.bind(on_press=self.select_output_directory)
        self.layout.add_widget(self.remove_bg_button)

        return self.layout

    def open_filechooser(self, instance):
        Tk().withdraw()
        file_path = filedialog.askopenfilename(
            title="Vælg billede",
            filetypes=[("Billeder", "*.png *.jpg *.jpeg *.webp")]
        )
        if file_path:
            self.image_path = file_path
            self.image_widget.source = file_path
            self.image_widget.reload()

    def select_output_directory(self, instance):
        Tk().withdraw()
        output_directory = filedialog.askdirectory(title="Vælg hvor filen(e) skal gemmes")
        if output_directory:
            self.output_directory = output_directory
            if hasattr(self, "image_path"):
                threading.Thread(target=self.process_image).start()
            elif hasattr(self, "folder_path"):
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                self.folder_output_directory = os.path.join(self.output_directory, f"Behandlet_{timestamp}")
                os.makedirs(self.folder_output_directory, exist_ok=True)
                threading.Thread(target=self.process_folder, args=(self.folder_path,)).start()

    def on_drop_file(self, window, file_path):
        file_path = file_path.decode("utf-8")
        if os.path.isfile(file_path) and file_path.lower().endswith(('png', 'jpg', 'jpeg', 'webp')):
            self.image_path = file_path
            self.image_widget.source = file_path
            self.image_widget.reload()
        elif os.path.isdir(file_path):
            self.folder_path = file_path
            self.progress_label.text = "Behandler mappe..."

    def process_image(self):
        self.progress.value = 0
        self.progress_label.text = "Behandler..."
        input_path = self.image_path
        output_path = os.path.join(self.output_directory,
                                   os.path.basename(input_path).replace(".jpg", "_no_bg.png").replace(".jpeg",
                                                                                                      "_no_bg.png").replace(
                                       ".png", "_no_bg.png").replace(".webp", "_no_bg.png"))

        try:
            with PILImage.open(input_path) as img:
                output = remove(img)
                output.save(output_path)

            self.progress.value = 100
            self.progress_label.text = "Færdig!"
            self.image_widget.source = output_path
            self.image_widget.reload()
        except Exception as e:
            self.progress_label.text = f"Fejl: {str(e)}"

    def process_folder(self, folder_path):
        images = [f for f in os.listdir(folder_path) if f.lower().endswith(('png', 'jpg', 'jpeg', 'webp'))]
        total_images = len(images)
        if total_images == 0:
            self.progress_label.text = "Ingen billeder fundet i mappen"
            return

        self.progress.value = 0
        increment = 100 / total_images
        for index, image in enumerate(images):
            input_path = os.path.join(folder_path, image)
            output_path = os.path.join(self.folder_output_directory,
                                       image.replace(".jpg", "_no_bg.png").replace(".jpeg", "_no_bg.png").replace(
                                           ".png", "_no_bg.png").replace(".webp", "_no_bg.png"))
            try:
                with PILImage.open(input_path) as img:
                    output = remove(img)
                    output.save(output_path)
                    self.progress.value += increment
                    self.progress_label.text = f"Behandler... {index + 1}/{total_images}"
                    self.image_widget.source = output_path
                    self.image_widget.reload()
                    threading.Event().wait(0.5)
            except Exception as e:
                self.progress_label.text = f"Fejl med {image}: {str(e)}"

        self.progress_label.text = "Mappebehandling færdig!"
        self.progress.value = 100


if __name__ == "__main__":
    RembgApp().run()
