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
from PIL import Image
# Diverse import:
#   Kivy til UI
#   RemBG til baggrundsfjernelse
#   Tkinter til at kunne anvende Windows dialog vindue
#   Pillow (PIL forkortet) til at håndtere billedfiler, samt konvertere
#   eksempelvis fra AVIF til PNG


class PixelWipe(BoxLayout): # Hovedklasse, som matcher med klassen i kivy koden

    def __init__(self, **kwargs): # Standard-kaldbare-attributes defineres her
        super().__init__(**kwargs)
        self.selected_path = None
        self.output_folder = None
        # ^ standardvædier i den forstand, at programmet ikke har valgt et billede, eller en mappe, idet programmet starter.
        self.processed_images = [] # Laver en tom liste, hvor output ryger ind

        self.default_output_folder = os.path.join(os.path.expanduser("~"), "Overførsler") # Når man behandler et billede (el. mappe)
                                                                                          # så er downloads standard-output, med mindre
                                                                                          # brugeren vælger en placering

        self.tk_root = tk.Tk()
        self.tk_root.withdraw()
        # ^ Lader os anvende tkinter med Stifinder uden tk-pop-up vinduer

        Window.bind(on_dropfile=self.on_drop) # Når filer bliver drag & dropped, skal det køre on_drop funktionen

    def on_drop(self, window, file_path): # Funktion, som håndterer drag-and-drop
        path = file_path.decode("utf-8")  # Når man drag and dropper vil Kivy gerne have
                                          # et input i bytes, derfor decoder vi med utf-8 fra str til bytes

        if os.path.isdir(path):  # Hvis det er en mappe (dir for directory/mappe)
            self.selected_path = path
            self.update_file_info(self.selected_path, "Output: Ikke valgt") # Standardtekst, indtil man vælger outputsti

        elif path.lower().endswith((".png", ".jpg", ".jpeg",".webp")): # Hvis det er en enkel fil i følgende format
            self.reset_images() # Sørger for et rent canvas, altså, ikke nogen gamle processed billeder
            self.selected_path = path
            self.update_file_info(self.selected_path, "Output: Ikke valgt")
            self.show_image(self.selected_path, self.ids.before_image) # Viser før og efter billede

        elif path.lower().endswith((".avif")): # Konvertering af AVIF til PNG
            img = Image.open(path) # Åbner filen med Image.open fra Pillow
            img.save(path,"PNG") # Gemmer path som AVIF filen konverteret til en png
            self.reset_images()
            self.selected_path = path
            self.update_file_info(self.selected_path, "Output: Ikke Valgt")
            self.show_image(self.selected_path, self.ids.before_image)

    def reset_images(self):
        self.ids.before_image.source = ''
        self.ids.after_image.source = ''
        # Opdaterer self til at være tom (som hermed giver os et blank canvas, når vi vælger nye filer/mapper)

    def select_file(self): # Funktion til når man vælger et billede vha. knappen i programmets UI
        file_path = filedialog.askopenfilename(filetypes=[("Billedformater", "*.png;*.jpg;*.jpeg;*.webp;*.avif")])
        # Åbner Windows dialogvindue, som kun tillader, at man vælger overstående filformater
        if file_path:
            self.reset_images()
            self.selected_path = file_path
            self.update_file_info(self.selected_path, "Output: Ikke valgt")
            self.show_image(self.selected_path, self.ids.before_image)


    def select_folder(self): # Funktion til når man vælger en mappe  vha. knappen i programmets UI
        folder_path = filedialog.askdirectory() # askdirectory gør at Windows dialogvinduet kun viser mapper og ikke enkelte filer
        if folder_path:
            self.reset_images()
            self.selected_path = folder_path
            self.update_file_info(self.selected_path, "Output: Ikke valgt")

    def ask_output_folder(self):
        folder = filedialog.askdirectory(title="Vælg mappesti")
        return folder if folder else self.create_unique_output_folder(self.default_output_folder) # Hvis brugeren ikke selv vælger en mappe
                                                                                                  # så kører create_unique_output_folder
                                                                                                  # som laver en mappe i Downloads

    def create_unique_output_folder(self, base_folder):
        output_folder = os.path.join(base_folder, "Behandlede billeder") # Laver en mappe, hvis brugeren ikke vælger en
        counter = 1
        while os.path.exists(output_folder):
            output_folder = os.path.join(base_folder, f"Processed_Images_{counter}")
            counter += 1
        os.makedirs(output_folder)
        return output_folder

    def update_file_info(self, selected, saving):
        # Opdaterer UI til at vise den valgte fil/mappe, og dens eksporteringssti
        self.ids.file_label.text = f"Fra: {selected}\nTil: {saving}"

    def show_image(self, image_path, widget):
        # Lambda bruges til at få programmet til at vente med at opdatere widget før
        # process er klar - og clock..._once sørger for, at det kun sker én gang. Ellers vil output
        # image bare være blank, da programmet ikke kan process billedet "instant"
        # https://kivy.org/doc/stable/api-kivy.clock.html
        Clock.schedule_once(lambda dt: setattr(widget, 'source', image_path), 0)

    def start_processing(self):
        """ Asks for output folder and starts processing """
        if not self.selected_path:
            self.update_file_info("Ingen fil eller mappe valgt!", "")
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
            input_img = Image.open(image_path)
            if input_img.mode != "RGBA":
                input_img = input_img.convert("RGBA")

            # Process the image
            output_img = remove(input_img)

            # Ensure output path ends with .png
            output_filename = os.path.splitext(os.path.basename(image_path))[0] + "ingen_baggrund.png"
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
                Clock.schedule_once(lambda dt: self.update_file_info("Ingen billeder fundet!", ""), 0)
                return

            for index, file in enumerate(files):
                input_path = os.path.join(self.selected_path, file)
                self.process_image(input_path)

                # Update progress bar dynamically
                progress_value = int(((index + 1) / len(files)) * 100)
                Clock.schedule_once(lambda dt: setattr(self.ids.progress, 'value', progress_value), 0)

            Clock.schedule_once(lambda dt: self.update_file_info(self.selected_path, self.output_folder), 0)
        except Exception as fejl:
            fejl_besked = f"Fejl: {str(fejl)}"
            Clock.schedule_once(lambda dt: self.update_file_info("Fejl", fejl_besked), 0)


class PixelWipeApp(App):
    def build(self):
        Builder.load_file("design.kv") # Indlæser design fra Kivy
        return PixelWipe()


if __name__ == "__main__":
    PixelWipeApp().run()
