import os
import requests
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.spinner import Spinner
from kivy.graphics import Rectangle, Color
from kivy.uix.widget import Widget
from kivy.uix.image import AsyncImage

# Hugging Face API Setup
HF_API_URLS = {
    "fr": "https://api-inference.huggingface.co/models/Helsinki-NLP/opus-mt-en-fr",
    "es": "https://api-inference.huggingface.co/models/Helsinki-NLP/opus-mt-en-es",
    "de": "https://api-inference.huggingface.co/models/Helsinki-NLP/opus-mt-en-de",
    "hi": "https://api-inference.huggingface.co/models/facebook/nllb-200-distilled-600M",
    "it": "https://api-inference.huggingface.co/models/Helsinki-NLP/opus-mt-en-it",
    "pt": "https://api-inference.huggingface.co/models/Helsinki-NLP/opus-mt-en-pt",
    "nl": "https://api-inference.huggingface.co/models/Helsinki-NLP/opus-mt-en-nl",
}

HEADERS = {"Authorization": "Bearer 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"}
session = requests.Session()

# ------------------------------
# 🔹 Menu Screen
# ------------------------------
class MenuScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)

        layout.add_widget(Label(text='Menu Page', font_size='30sp', bold=True))
        start_button = Button(text='Go to Translator', background_color=(0, 0, 0, 1))
        start_button.bind(on_press=self.go_to_translator)
        layout.add_widget(start_button)

        self.add_widget(layout)

    def go_to_translator(self, instance):
        self.manager.current = "translator"


# ------------------------------
# 🔹 Translator Screen
# ------------------------------
class TranslatorScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        self.add_widget(layout)

        # Background
        with self.canvas.before:
            Color(76/255, 94/255, 132/255, 1)
            self.bg = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self.update_bg, pos=self.update_bg)

        # Header with Back Button
        header_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.1))
        back_button = Button(text='⬅ Back', size_hint=(None, None), size=(80, 40))
        back_button.bind(on_press=self.go_back)
        header_layout.add_widget(back_button)
        header_layout.add_widget(Label(text='Language Translator', font_size='28sp', bold=True))
        layout.add_widget(header_layout)

        # Language Selection
        self.language_spinner = Spinner(
            text='Select Language',
            values=list(HF_API_URLS.keys()),
            size_hint=(1, 0.1)
        )
        layout.add_widget(self.language_spinner)

        # User Input
        self.user_input = TextInput(hint_text='Enter text to translate...', multiline=False,
                                    background_color=(190/255, 208/255, 244/255, 1),
                                    foreground_color=(0, 0, 0, 1),
                                    font_size='16sp', size_hint=(1, 0.1))
        layout.add_widget(self.user_input)

        # Response Output
        self.response_output = TextInput(readonly=True,
                                        background_color=(190/255, 208/255, 244/255, 1),
                                        foreground_color=(0, 0, 0, 1),
                                        hint_text='Translated text will appear here...',
                                        size_hint=(1, 0.6))
        layout.add_widget(self.response_output)

        # Buttons
        button_layout = BoxLayout(size_hint=(1, 0.1), spacing=10)
        translate_button = Button(text='Translate', background_color=(0, 0, 0, 1))
        clear_button = Button(text='Clear', background_color=(0, 0, 0, 1))
        translate_button.bind(on_press=self.translate_text)
        clear_button.bind(on_press=self.clear_inputs)
        button_layout.add_widget(translate_button)
        button_layout.add_widget(clear_button)
        layout.add_widget(button_layout)

        # Feedback Label
        self.feedback_label = Label(text='', color=(0, 0, 0, 1), size_hint=(1, 0.05))
        layout.add_widget(self.feedback_label)

    def update_bg(self, *args):
        self.bg.size = self.size
        self.bg.pos = self.pos

    def go_back(self, instance):
        self.manager.current = "menu"

    def translate_text(self, instance):
        user_text = self.user_input.text.strip()
        selected_language = self.language_spinner.text
        api_url = HF_API_URLS.get(selected_language)

        if user_text and api_url:
            try:
                payload = {"inputs": user_text}
                response = session.post(api_url, headers=HEADERS, json=payload)
                translated_text = response.json()[0]['translation_text'].strip()
                self.response_output.text = translated_text
                self.feedback_label.text = "Translation successful!"
            except Exception as e:
                self.feedback_label.text = f"Error: {str(e)}"
        else:
            self.feedback_label.text = "Please enter text and select a language."

    def clear_inputs(self, instance):
        self.user_input.text = ''
        self.response_output.text = ''
        self.feedback_label.text = ''


# ------------------------------
# 🔹 Main App
# ------------------------------
class TranslatorApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(MenuScreen(name="menu"))
        sm.add_widget(TranslatorScreen(name="translator"))
        return sm


if __name__ == '__main__':
    TranslatorApp().run()
