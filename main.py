import os
import threading
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.core.window import Window
from tkinter import filedialog
import tkinter as tk
from rembg import remove
from PIL import Image as PILImage
from PIL import Image
import pillow_avif


class ImageProcessor(BoxLayout):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.selected_path = None
        self.output_folder = None
        self.processed_images = []

        # Set default output folder to "Downloads"
        self.default_output_folder = os.path.join(os.path.expanduser("~"), "Downloads")

        # Hide Tkinter root window
        self.tk_root = tk.Tk()
        self.tk_root.withdraw()

        # Enable drag & drop
        Window.bind(on_dropfile=self.on_drop)

    def on_drop(self, window, file_path):
        """ Handles drag & drop for files or folders """
        path = file_path.decode("utf-8")

        if os.path.isdir(path):  # If it's a folder
            self.selected_path = path
            self.update_file_info(self.selected_path, "Output: Ikke valgt")
        elif path.lower().endswith((".png", ".jpg", ".jpeg",".webp")):
            self.reset_images()
            self.selected_path = path
            self.update_file_info(self.selected_path, "Output: Ikke valgt")
            self.show_image(self.selected_path, self.ids.before_image)
        elif path.lower().endswith((".avif")):
            img = Image.open(path)
            img.save(path,"PNG")
            self.reset_images()
            self.selected_path = path
            self.update_file_info(self.selected_path, "Output: Ikke Valgt")
            self.show_image(self.selected_path, self.ids.before_image)

    def reset_images(self):
        """ Clears the Before & After images when selecting a new file or folder """
        Clock.schedule_once(lambda dt: setattr(self.ids.before_image, 'source', ''), 0)
        Clock.schedule_once(lambda dt: setattr(self.ids.after_image, 'source', ''), 0)

    def select_file(self):
        """ Opens a file dialog to select an image """
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.webp;*.avif")])
        if file_path:
            self.reset_images()
            self.selected_path = file_path
            self.update_file_info(self.selected_path, "Output: Ikke valgt")
            self.show_image(self.selected_path, self.ids.before_image)


    def select_folder(self):
        """ Opens a folder dialog to select a folder """
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.reset_images()
            self.selected_path = folder_path
            self.update_file_info(self.selected_path, "Output: Ikke valgt")

    def ask_output_folder(self):
        """ Asks user for an output folder when clicking Process, defaults to Downloads """
        folder = filedialog.askdirectory(title="Select Output Folder")
        return folder if folder else self.create_unique_output_folder(self.default_output_folder)

    def create_unique_output_folder(self, base_folder):
        """ Creates a unique folder for processed images if one exists """
        output_folder = os.path.join(base_folder, "Processed_Images")
        counter = 1
        while os.path.exists(output_folder):
            output_folder = os.path.join(base_folder, f"Processed_Images_{counter}")
            counter += 1
        os.makedirs(output_folder)
        return output_folder

    def update_file_info(self, selected, saving):
        """ Updates the UI to show the selected file/folder and where it will be saved """
        Clock.schedule_once(lambda dt: setattr(self.ids.file_label, 'text', f"Fra: {selected}\nTil: {saving}"), 0)

    def show_image(self, image_path, widget):
        """ Displays an image in a Kivy Image widget """
        Clock.schedule_once(lambda dt: setattr(widget, 'source', image_path), 0)

    def start_processing(self):
        """ Asks for output folder and starts processing """
        if not self.selected_path:
            self.update_file_info("No file or folder selected!", "None")
            return

        self.output_folder = self.ask_output_folder()
        self.processed_images = []

        # Reset progress bar correctly
        Clock.schedule_once(lambda dt: setattr(self.ids.progress, 'value', 0), 0)

        if os.path.isfile(self.selected_path):
            threading.Thread(target=self.process_image, args=(self.selected_path,), daemon=True).start()
        elif os.path.isdir(self.selected_path):
            threading.Thread(target=self.process_folder, daemon=True).start()

    def process_image(self, image_path):
        """ Removes the background from a single image and saves it properly """
        try:
            # Open the image and ensure it's in RGBA mode
            input_img = PILImage.open(image_path)
            if input_img.mode != "RGBA":
                input_img = input_img.convert("RGBA")

            # Process the image
            output_img = remove(input_img)

            # Ensure output path ends with .png
            output_filename = os.path.splitext(os.path.basename(image_path))[0] + "_no_bg.png"
            output_path = os.path.join(self.output_folder, output_filename)

            # Save as PNG to prevent corruption
            output_img.save(output_path, format="PNG")

            # Show Before image
            self.show_image(image_path, self.ids.before_image)

            # Show processed After image
            self.show_image(output_path, self.ids.after_image)

            Clock.schedule_once(lambda dt: self.update_file_info(image_path, output_path), 0)
        except Exception as error:
            error_message = f"Error: {str(error)}"
            Clock.schedule_once(lambda dt: setattr(self.ids.file_label, 'text', error_message), 0)

    def process_folder(self):
        """ Processes all images in a folder and saves them in a new folder """
        try:
            files = [f for f in os.listdir(self.selected_path) if f.lower().endswith(('.png', '.jpg', '.jpeg','.webp','.avif'))]
            if not files:
                Clock.schedule_once(lambda dt: self.update_file_info("No images found!", "None"), 0)
                return

            for index, file in enumerate(files):
                input_path = os.path.join(self.selected_path, file)
                self.process_image(input_path)

                # Update progress bar dynamically
                progress_value = int(((index + 1) / len(files)) * 100)
                Clock.schedule_once(lambda dt: setattr(self.ids.progress, 'value', progress_value), 0)

            Clock.schedule_once(lambda dt: self.update_file_info(self.selected_path, self.output_folder), 0)
        except Exception as error:
            error_message = f"Error: {str(error)}"
            Clock.schedule_once(lambda dt: self.update_file_info("Error", error_message), 0)


class ImageProcessorApp(App):
    def build(self):
        Builder.load_file("design.kv")
        return ImageProcessor()


if __name__ == "__main__":
    ImageProcessorApp().run()
