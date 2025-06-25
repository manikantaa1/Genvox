from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.graphics import Color, Rectangle, RoundedRectangle, Ellipse
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.core.window import Window
from kivy.clock import Clock
from together import Together
import speech_recognition as sr
import threading
from plyer import vibrator
import os
from kivy.utils import platform

# Set window background color to match the blue theme from code 1
Window.clearcolor = (64/255, 89/255, 140/255, 1)  # Darker blue background

# API client initialization
client = Together(api_key="6fcd9484266e33a4e349a09c463bd9b5b0c1f6b66277631ef78e634c65d8ac2c")

# Define the Kivy language string for styling to match code 1's theme
KV = '''
<CustomButton@Button>:
    background_color: 0, 0, 0, 0
    background_normal: ''
    canvas.before:
        Color:
            rgba: (1, 1, 1, 1) if self.state == 'normal' else (0.9, 0.9, 0.9, 1)
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [10]

<IconButton@Button>:
    background_color: 0, 0, 0, 0
    background_normal: ''
    size_hint: None, None
    size: dp(40), dp(40)

<CircularButton@Button>:
    background_color: 64/255, 89/255, 140/255, 1  # Dark blue background
    background_normal: ''
    size_hint: None, None
    size: dp(50), dp(50)
    canvas.before:
        Color:
            rgba: self.background_color
        Ellipse:
            pos: self.pos
            size: self.size
    font_size: '14sp'
    color: 1, 1, 1, 1  # White text
    bold: True

<CustomTextInput@TextInput>:
    background_color: 150/255, 178/255, 222/255, 1  # Light blue
    foreground_color: 0, 0, 0, 1  # Black text
    cursor_color: 0, 0, 0, 1  # Black cursor
    hint_text_color: 1, 1, 1, 0.7  # White hint text with some transparency
    font_size: '16sp'
    padding: [10, 10, 10, 10]

<RoundedBoxLayout@BoxLayout>:
    canvas.before:
        Color:
            rgba: 150/255, 178/255, 222/255, 1  # Light blue
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [20]

<TextGeneratorScreen>:
    canvas.before:
        Color:
            rgba: 64/255, 89/255, 140/255, 1  # Dark blue background
        Rectangle:
            pos: self.pos
            size: self.size
            
    BoxLayout:
        orientation: 'vertical'
        spacing: dp(12)
        padding: dp(16)
        
        # Top bar with title and back button
        BoxLayout:
            orientation: 'horizontal'
            size_hint_y: None
            height: dp(50)
            padding: [0, 0, 0, 0]
            
            CircularButton:
                text: "<"
                on_press: root.go_back()
                pos_hint: {"center_y": 0.5}
            
            Label:
                text: "Text Generator"
                font_size: '20sp'
                color: 1, 1, 1, 1
                size_hint_x: 0.8
                
            Widget:
                size_hint_x: None
                width: dp(40)
        
        # Spacing
        Widget:
            size_hint_y: None
            height: dp(20)
            
        # User Input Text Area with Voice Button
        BoxLayout:
            orientation: 'horizontal'
            size_hint_y: None
            height: dp(100)
            spacing: dp(10)
            
            CustomTextInput:
                id: prompt_input
                hint_text: "Enter your prompt here..."
                multiline: True
                size_hint_x: 0.85
            
            CircularButton:
                id: voice_button
                text: "🎤"
                size_hint_x: None
                width: dp(50)
                on_press: root.toggle_voice_input()
                pos_hint: {"center_y": 0.5}
        
        # Spacing
        Widget:
            size_hint_y: None
            height: dp(10)
            
        # Buttons
        BoxLayout:
            orientation: 'horizontal'
            size_hint_y: None
            height: dp(50)
            spacing: dp(10)
            
            CustomButton:
                text: "Generate Text"
                font_size: '16sp'
                size_hint_x: 0.5
                color: 64/255, 89/255, 140/255, 1  # Dark blue text
                on_press: root.generate_text()
                
            CustomButton:
                text: "Clear"
                font_size: '16sp'
                size_hint_x: 0.5
                color: 64/255, 89/255, 140/255, 1  # Dark blue text
                on_press: root.clear_inputs()
        
        # Status label
        Label:
            id: feedback_label
            text: ""
            color: 1, 1, 1, 1
            size_hint_y: None
            height: dp(30)
            
        # Response Output Area - rounded rectangle
        RoundedBoxLayout:
            orientation: "vertical"
            size_hint_y: 0.6
            padding: dp(10)
            
            CustomTextInput:
                id: response_output
                hint_text: "Generated text will appear here..."
                background_color: 190/255, 208/255, 244/255, 1
                foreground_color: 0, 0, 0, 1
                readonly: True
                multiline: True
'''

Builder.load_string(KV)

# ------------------------------
# 🔹 Text Generator Screen
# ------------------------------
class TextGeneratorScreen(Screen):
    def __init__(self, **kwargs):
        super(TextGeneratorScreen, self).__init__(**kwargs)
        self.client = Together(api_key="a77f068040638cbe4879024a9d83a58f7b6775708fad8483d0802c468ff79566")
        self.recording = False
        self.recognizer = sr.Recognizer()
    
    def go_back(self):
        if self.recording:
            self.toggle_voice_input()  # Stop recording if active
        self.manager.current = "menu"
    
    def toggle_voice_input(self):
        if self.recording:
            # Stop recording
            self.recording = False
            self.ids.voice_button.text = "🎤"
            self.ids.voice_button.background_color = (64/255, 89/255, 140/255, 1)  # Reset to default color
            self.ids.feedback_label.text = ""
        else:
            # Start recording
            self.recording = True
            self.ids.voice_button.text = "⏹️"
            self.ids.voice_button.background_color = (1, 0, 0, 1)  # Red color for recording
            self.ids.feedback_label.text = "Listening..."
            
            # Provide haptic feedback on devices that support it
            if platform == 'android' and hasattr(vibrator, 'vibrate'):
                vibrator.vibrate(0.1)  # Short vibration
                
            # Start listening in a separate thread
            threading.Thread(target=self.listen_for_speech).start()
    
    def listen_for_speech(self):
        try:
            with sr.Microphone() as source:
                # Adjust for ambient noise
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.listen(source, timeout=10.0)
                
            # Try to recognize the speech
            try:
                text = self.recognizer.recognize_google(audio)
                # Update the UI in the main thread and auto-generate response
                Clock.schedule_once(lambda dt: self.update_text_and_generate(text), 0)
            except sr.UnknownValueError:
                # Use a function that doesn't depend on accessing the exception variable
                Clock.schedule_once(lambda dt: self.update_feedback("Could not understand audio"), 0)
            except sr.RequestError:
                # Pass the error message directly to avoid lambda scope issues
                error_msg = "Error connecting to Google Speech Recognition service"
                Clock.schedule_once(lambda dt: self.update_feedback(error_msg), 0)
                
        except Exception as e:
            # Create a local variable with the error message to avoid lambda scope issues
            error_message = f"Error: {str(e)}"
            Clock.schedule_once(lambda dt: self.update_feedback(error_message), 0)
        
        # Reset recording state in the main thread
        Clock.schedule_once(lambda dt: self.reset_recording_state(), 0)
    
    def update_text_and_generate(self, text):
        # First update the text input
        current_text = self.ids.prompt_input.text
        if current_text and not current_text.endswith(' '):
            self.ids.prompt_input.text = f"{current_text} {text}"
        else:
            self.ids.prompt_input.text = f"{current_text}{text}"
        
        self.ids.feedback_label.text = "Voice input added, generating text..."
        
        # Now automatically generate the response
        # Use a small delay to ensure UI updates before starting the API call
        Clock.schedule_once(lambda dt: self.generate_text(), 0.5)
    
    def update_feedback(self, message):
        self.ids.feedback_label.text = message
    
    def reset_recording_state(self):
        self.recording = False
        self.ids.voice_button.text = "🎤"
        self.ids.voice_button.background_color = (64/255, 89/255, 140/255, 1)
    
    def generate_text(self):
        user_query = self.ids.prompt_input.text.strip()
        if user_query:
            # Show loading message
            self.ids.feedback_label.text = "Generating text..."
            
            # Run the API call in a background thread to avoid freezing the UI
            threading.Thread(target=self._execute_api_call, args=(user_query,)).start()
        else:
            self.ids.feedback_label.text = "Please enter a valid prompt."
    
    def _execute_api_call(self, user_query):
        try:
            response = self.client.chat.completions.create(
                model="meta-llama/Llama-3.3-70B-Instruct-Turbo",
                messages=[{"role": "user", "content": user_query}],
            )
            response_text = response.choices[0].message.content.strip()
            
            # Update UI in main thread
            Clock.schedule_once(lambda dt: self._update_response(response_text), 0)
        except Exception as e:
            # Create a local variable to avoid lambda scope issues
            error_message = f"Error: {str(e)}"
            Clock.schedule_once(lambda dt: self.update_feedback(error_message), 0)
            
    def _update_response(self, response_text):
        self.ids.response_output.text = response_text
        self.ids.feedback_label.text = "Text generated successfully!"
    
    def clear_inputs(self):
        self.ids.prompt_input.text = ''
        self.ids.response_output.text = ''
        self.ids.feedback_label.text = ''

# ------------------------------
# 🔹 Main App Setup
# ------------------------------
class TextGeneratorApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(TextGeneratorScreen(name="text_generator"))
        # You would add a menu screen here in a full app
        sm.current = "text_generator"
        return sm

if __name__ == '__main__':
    TextGeneratorApp().run()