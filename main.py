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
        self.output_folder = None
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
            self.output_folder = None  # Reset output folder until user selects
            self.update_file_info(self.selected_path, "Not Selected")
            self.show_image(self.selected_path, self.ids.before_image)

    def select_folder(self):
        """ Opens a folder dialog to select a folder """
        root = tk.Tk()
        root.withdraw()
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.reset_before_image()
            self.selected_path = folder_path
            self.output_folder = None  # Reset output folder until user selects
            self.update_file_info(self.selected_path, "Not Selected")

    def choose_output_folder(self):
        """ Asks the user where to save the converted files, or defaults to a new folder """
        root = tk.Tk()
        root.withdraw()
        folder_path = filedialog.askdirectory(title="Select Output Folder")
        if folder_path:  # User selected a folder
            return folder_path
        else:  # Default to a new "processed_images" folder
            return self.create_output_folder(os.path.dirname(self.selected_path))

    def create_output_folder(self, base_folder):
        """ Creates a new output folder with a unique name if needed """
        output_folder = os.path.join(base_folder, "processed_images")
        counter = 1
        while os.path.exists(output_folder):
            output_folder = os.path.join(base_folder, f"processed_images_{counter}")
            counter += 1
        os.makedirs(output_folder)
        return output_folder

    def update_file_info(self, selected, saving):
        """ Updates the UI to show selected file/folder and output path """
        Clock.schedule_once(lambda dt: setattr(self.ids.file_label, 'text', f"From: {selected}\nTo: {saving}"), 0)

    def show_image(self, image_path, widget):
        """ Displays the selected image on the UI """
        Clock.schedule_once(lambda dt: setattr(widget, 'source', image_path), 0)

    def start_processing(self):
        """ Prompts user for output location and starts processing """
        if not self.selected_path:
            return

        # Ask user for save location
        self.output_folder = self.choose_output_folder()
        self.update_file_info(self.selected_path, self.output_folder)

        # Process file or folder
        if os.path.isfile(self.selected_path):
            threading.Thread(target=self.process_image, args=(self.selected_path,), daemon=True).start()
        elif os.path.isdir(self.selected_path):
            threading.Thread(target=self.process_folder, daemon=True).start()

    def process_image(self, image_path):
        """ Removes the background from a single image and saves it in the correct folder """
        try:
            input_img = PILImage.open(image_path)
            output_img = remove(input_img)
            output_path = os.path.join(self.output_folder, os.path.basename(image_path))
            output_img.save(output_path)

            # Show BEFORE image on the left side
            self.show_image(image_path, self.ids.before_image)

            # Show AFTER image on the right side
            self.show_image(output_path, self.ids.after_image)

            self.update_file_info(image_path, output_path)
        except Exception as e:
            Clock.schedule_once(lambda dt: setattr(self.ids.file_label, 'text', f"Error: {str(e)}"), 0)

    def process_folder(self):
        """ Removes the background from all images in a selected folder and saves them in a new folder """
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
