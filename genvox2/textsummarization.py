import os
from together import Together
from kivy.app import App
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.filechooser import FileChooserIconView
from kivy.uix.popup import Popup
from kivy.graphics import Color, Rectangle

# Initialize the Together API client
client = Together(api_key="6fcd9484266e33a4e349a09c463bd9b5b0c1f6b66277631ef78e634c65d8ac2c")

class SummarizationScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        # Set background color
        with layout.canvas.before:
            Color(76/255, 94/255, 132/255, 1)
            self.bg = Rectangle(size=layout.size, pos=layout.pos)
            layout.bind(size=self._update_bg, pos=self._update_bg)
        
        # Back Button
        back_button = Button(text='⬅ Back', size_hint=(1, 0.1), background_color=(0, 0, 0.5, 1), color=(1, 1, 1, 1))
        back_button.bind(on_press=self.go_back)
        layout.add_widget(back_button)
        
        # Title
        self.title_label = Label(text='Text Summarization', font_size='24sp', bold=True, color=(1, 1, 1, 1), size_hint=(1, 0.1))
        layout.add_widget(self.title_label)
        
        # Input Text
        self.input_text = TextInput(hint_text='Enter text to summarize...', multiline=True, 
                                    background_color=(0.95, 0.95, 1, 1), foreground_color=(0, 0, 0, 1), 
                                    font_size='16sp', size_hint=(1, 0.3))
        layout.add_widget(self.input_text)
        
        # Upload File
        self.file_button = Button(text='Upload File', background_color=(0, 0, 0.5, 1), color=(1, 1, 1, 1), font_size='16sp', size_hint=(1, 0.1))
        self.file_button.bind(on_press=self.open_file_chooser)
        layout.add_widget(self.file_button)
        
        # Summarize Button
        self.summarize_button = Button(text='Summarize', background_color=(0, 0, 0.5, 1), color=(1, 1, 1, 1), font_size='16sp', size_hint=(1, 0.1))
        self.summarize_button.bind(on_press=self.summarize_text)
        layout.add_widget(self.summarize_button)
        
        # Output
        self.output_text = TextInput(readonly=True, hint_text='Summary will appear here...', multiline=True, 
                                     background_color=(0.9, 0.9, 1, 1), foreground_color=(0, 0, 0, 1), 
                                     font_size='16sp', size_hint=(1, 0.3))
        layout.add_widget(self.output_text)
        
        # Feedback
        self.feedback_label = Label(text='', color=(1, 1, 1, 1), font_size='14sp', size_hint=(1, 0.1))
        layout.add_widget(self.feedback_label)

        self.add_widget(layout)

    def _update_bg(self, *args):
        self.bg.size = self.children[0].size
        self.bg.pos = self.children[0].pos

    def go_back(self, instance):
        if hasattr(self.manager, 'current'):
            self.manager.current = 'menu'
        else:
            self.feedback_label.text = "Back navigation not available when running standalone"

    def open_file_chooser(self, instance):
        content = FileChooserIconView()
        popup = Popup(title='Select a File', content=content, size_hint=(0.9, 0.9))
        content.bind(on_submit=lambda fc, selection, touch: self.load_file(selection, popup))
        popup.open()
    
    def load_file(self, selection, popup):
        if selection:
            try:
                with open(selection[0], 'r', encoding='utf-8') as file:
                    self.input_text.text = file.read()
                self.feedback_label.text = "File loaded successfully!"
            except Exception as e:
                self.feedback_label.text = f"Error loading file: {str(e)}"
        popup.dismiss()
    
    def summarize_text(self, instance):
        user_input = self.input_text.text.strip()
        if user_input:
            try:
                self.feedback_label.text = "Generating summary, please wait..."
                response = client.chat.completions.create(
                    model="meta-llama/Llama-3.3-70B-Instruct-Turbo",
                    messages=[
                        {"role": "user", "content": f"Summarize the following text clearly and concisely:\n\n{user_input}\n\nSummary:"}
                    ],
                    max_tokens=100,
                    temperature=0.2,
                )
                self.output_text.text = response.choices[0].message.content.strip()
                self.feedback_label.text = "Summary generated successfully!"
            except Exception as e:
                self.feedback_label.text = f"Error: {str(e)}"
        else:
            self.feedback_label.text = "Please enter valid text."

# For integration with main.py
class SummarizationApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(SummarizationScreen(name='summarize'))
        return sm

# For standalone testing
if __name__ == '__main__':
    SummarizationApp().run()
