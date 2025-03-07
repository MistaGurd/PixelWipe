import os
import threading
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from kivy.clock import Clock
from tkinter import filedialog
import tkinter as tk
from rembg import remove
from PIL import Image as PILImage


class ImageProcessor(BoxLayout):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.selected_path = None
        self.output_path = None
        self.processed_images = []

    def reset_before_image(self):
        """ Clears the Before Image when selecting a new file or folder """
        Clock.schedule_once(lambda dt: setattr(self.ids.before_image, 'source', ''), 0)

    def select_file(self):
        """ Opens a file dialog to select an image """
        root = tk.Tk()
        root.withdraw()
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg")])
        if file_path:
            self.reset_before_image()
            self.selected_path = file_path
            self.output_path = self.get_output_path(file_path)
            self.update_file_info(self.selected_path, self.output_path)
            self.show_image(self.selected_path, self.ids.before_image)  # Show original on left side

    def select_folder(self):
        """ Opens a folder dialog to select a folder """
        root = tk.Tk()
        root.withdraw()
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.reset_before_image()
            self.selected_path = folder_path
            self.output_path = self.get_output_path(folder_path, is_folder=True)
            self.update_file_info(self.selected_path, self.output_path)

    def get_output_path(self, path, is_folder=False):
        """ Generates the output path for processed images """
        if is_folder:
            output_folder = f"{path}_processed"
            counter = 1
            while os.path.exists(output_folder):
                output_folder = f"{path}_processed_{counter}"
                counter += 1
            os.makedirs(output_folder)
            return output_folder
        else:
            base, ext = os.path.splitext(path)
            return f"{base}_bg_removed{ext}"

    def update_file_info(self, selected, saving):
        """ Updates the UI to show selected file/folder and output path """
        Clock.schedule_once(lambda dt: setattr(self.ids.file_label, 'text', f"From: {selected}\nTo: {saving}"), 0)

    def show_image(self, image_path, widget):
        """ Displays the selected image on the UI """
        Clock.schedule_once(lambda dt: setattr(widget, 'source', image_path), 0)

    def start_processing(self):
        """ Automatically detects whether to process a file or a folder """
        if not self.selected_path:
            return

        if os.path.isfile(self.selected_path):
            threading.Thread(target=self.process_image, args=(self.selected_path,), daemon=True).start()
        elif os.path.isdir(self.selected_path):
            threading.Thread(target=self.process_folder, daemon=True).start()

    def process_image(self, image_path):
        """ Removes the background from a single image """
        try:
            input_img = PILImage.open(image_path)
            output_img = remove(input_img)
            output_path = self.get_output_path(image_path)
            output_img.save(output_path)

            # Show BEFORE image on the left side
            self.show_image(image_path, self.ids.before_image)

            # Show AFTER image on the right side
            self.show_image(output_path, self.ids.after_image)

            self.update_file_info(image_path, output_path)
        except Exception as e:
            Clock.schedule_once(lambda dt: setattr(self.ids.file_label, 'text', f"Error: {str(e)}"), 0)

    def process_folder(self):
        """ Removes the background from all images in a selected folder """
        try:
            self.processed_images.clear()  # Reset processed images list
            files = [f for f in os.listdir(self.selected_path) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
            for file in files:
                image_path = os.path.join(self.selected_path, file)
                self.process_image(image_path)
                self.processed_images.append(image_path)
        except Exception as e:
            Clock.schedule_once(lambda dt: setattr(self.ids.file_label, 'text', f"Error: {str(e)}"), 0)


class ImageProcessorApp(App):
    def build(self):
        Builder.load_file("design.kv")
        return ImageProcessor()


if __name__ == "__main__":
    ImageProcessorApp().run()
