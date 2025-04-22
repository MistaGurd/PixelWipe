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
#   Threading til multitasking
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

        self.default_output_folder = os.path.join(os.path.expanduser("~"), "Downloads") # Når man behandler et billede (el. mappe)
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

        elif path.lower().endswith((".png", ".jpg", ".jpeg",".webp", ".avif")): # Hvis det er en enkel fil i følgende format
            self.reset_images() # Sørger for et rent canvas, altså, ikke nogen gamle processed billeder
            self.selected_path = path
            self.update_file_info(self.selected_path, "Output: Ikke valgt")
            self.show_image(self.selected_path, self.ids.before_image) # Viser før og efter billede

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
        counter = 1  # Programmet navngiver filer, og starter med billede 1
        while os.path.exists(output_folder):
            output_folder = os.path.join(base_folder, f"Billednummer_{counter}") # her navngives de
            counter += 1 # og tæller op for hvert billede
        os.makedirs(output_folder) # Opretter mappen
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
        if not self.selected_path:
            self.update_file_info("Ingen fil eller mappe valgt!", "")
            return
        # Hvis man prøver at køre programmet, uden at have valgt en fil eller mappe
        # så vil koden returnere "Ingen fil eller mappe valgt!"

        self.output_folder = self.ask_output_folder() # Definerer outputstien
        self.processed_images = [] # Starter med en tom liste af billeder

        Clock.schedule_once(lambda dt: setattr(self.ids.progress, 'value', 0), 0)
        # Sørger for, at progressbaren stemmer overens med de behandlede biller
        # ids.progress kalder på progressBar i Kivy koden

        if os.path.isfile(self.selected_path): # Hvis det er en fil
            threading.Thread(target=self.process_image, args=(self.selected_path,), daemon=True).start()
        elif os.path.isdir(self.selected_path): # Hvis det er en mappe
            threading.Thread(target=self.process_folder, daemon=True).start()
        # Kort fortalt: Threading sørger for multitasking i programmet. Lidt på samme måde som en computers CPU

        # Når programmet kører, er det en tråd (eller én opgave). Når brugeren
        # derefter vælger at fjerne baggrunden, skal programmet både køre
        # UI, men også rembg til at fjerne baggrunden. Threading lader programmet
        # opdele arbejdet, således at UI stadig er responsiv.

    def process_image(self, image_path):
        try:
            input_img = Image.open(image_path) # Pillow åbner billedet
            if input_img.mode != "RGBA": # Tjekker, om billedet er i alm. RGB farver og alpha (gennemsigtighed/styrke) via !=
                input_img = input_img.convert("RGBA") # Hvis ikke, anvender vi .convert til at sørge for, at billedet er i det rigtige format
                                                      # Især Alpha kanalen er vigtig her, ellers er det ikke muligt at have en gennemsigtig baggrund.

            output_img = remove(input_img) # .remove stammer fra rembg, og gemmer her billedet uden baggrund.

            output_filename = os.path.splitext(os.path.basename(image_path))[0] + "_ingen_baggrund.png" # Tager det originale filnavn, og tilføjer "ingen_baggrund"
            output_path = os.path.join(self.output_folder, output_filename) # Sørger for at ligge det i outputstien

            output_img.save(output_path, format="PNG") # Gemmer i PNG filformat med .save fra Pillow

            self.show_image(image_path, self.ids.before_image) # Opdaterer show_image widget i Kivy til at være billedet før behandling
            self.show_image(output_path, self.ids.after_image) # Opdaterer show_image widget i Kivy til at være billedet efter behandling

            Clock.schedule_once(lambda dt: self.update_file_info(image_path, output_path), 0)
            # Når programmet er færdig med at behandle et billede, opdaterer den update_file_info
        except Exception as error: # Hvis en fejl forekommer
            error_message = f"Error: {str(error)}" # Udskriver programmet Error... også fejlen
            Clock.schedule_once(lambda dt: setattr(self.ids.file_label, 'text', error_message), 0) # Opdaterer ids.file_label til at vise fejlbeskeden

    def process_folder(self):
        try:
            files = [f for f in os.listdir(self.selected_path) if f.lower().endswith(('.png', '.jpg', '.jpeg','.webp','.avif'))]
            # Når en mappe er valgt, laver den en liste af de filer, som er i formatet png, jpg, jpeg, webp og avif.
            if not files:
                Clock.schedule_once(lambda dt: self.update_file_info("Ingen billeder fundet!", ""), 0)
                return # Hvis programmet ikke finder nogle kompatible filer, udskriver den en error til brugeren

            for index, file in enumerate(files): # Hver fil bliver gemt som et index hvor enumerate sørger for at nummerere dem
                input_path = os.path.join(self.selected_path, file)
                self.process_image(input_path) # Kører hvert billede i mappen gennem process_image funktionen

                progress_value = int(((index + 1) / len(files)) * 100) # Ud fra længden af files, altså, filerne i den valgte mappe
                                                                       # defineres procentdelen hver fil udgør
                Clock.schedule_once(lambda dt: setattr(self.ids.progress, 'value', progress_value), 0) # Opdaterer progressbar ud fra hvor langt i mappen programmet er

            Clock.schedule_once(lambda dt: self.update_file_info(self.selected_path, self.output_folder), 0) # Når færdig, opdateres update_file_info
        except Exception as fejl:
            fejl_besked = f"Fejl: {str(fejl)}"
            Clock.schedule_once(lambda dt: self.update_file_info("Fejl", fejl_besked), 0)


class PixelWipeApp(App):
    def build(self):
        Builder.load_file("design.kv") # Indlæser design fra Kivy
        return PixelWipe()


if __name__ == "__main__":
    PixelWipeApp().run()
