from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from rembg import remove
from PIL import Image as PILImage
from tkinter import Tk, filedialog


class RembgApp(App):
    def build(self):
        self.layout = BoxLayout(orientation='vertical', spacing=10, padding=10)

        # Billedevisning
        self.image_widget = Image(size_hint=(1, 0.7))
        self.layout.add_widget(self.image_widget)

        # Vælg billede knap
        self.select_button = Button(text="Vælg billede", size_hint=(1, 0.15))
        self.select_button.bind(on_press=self.open_filechooser)
        self.layout.add_widget(self.select_button)

        # Fjern baggrund knap
        self.remove_bg_button = Button(text="Fjern baggrund", size_hint=(1, 0.15))
        self.remove_bg_button.bind(on_press=self.remove_background)
        self.layout.add_widget(self.remove_bg_button)

        return self.layout

    def open_filechooser(self, instance):
        # Deaktiver Tkinter GUI-vindue
        Tk().withdraw()

        # Åbn Windows' filvælger
        file_path = filedialog.askopenfilename(
            title="Vælg billede",
            filetypes=[("Billeder", "*.png *.jpg *.jpeg *.webp")]
        )

        if file_path:
            self.image_path = file_path
            self.image_widget.source = self.image_path
            self.image_widget.reload()

    def remove_background(self, instance):
        if hasattr(self, "image_path"):
            input_path = self.image_path
            output_path = input_path.replace(".jpg", "_no_bg.png").replace(".jpeg", "_no_bg.png").replace(".png", "_no_bg.png").replace(".webp", "_no_bg.png")

            # Åbn billedet, fjern baggrunden og gem resultatet
            with PILImage.open(input_path) as img:
                output = remove(img)
                output.save(output_path)

            # Opdater GUI med resultat
            self.image_widget.source = output_path
            self.image_widget.reload()


if __name__ == "__main__":
    RembgApp().run()
