from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.graphics import Color, Rectangle, RoundedRectangle, Ellipse
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.core.window import Window
from kivy.clock import Clock
import requests
import speech_recognition as sr
import threading
from plyer import vibrator
import os
from kivy.utils import platform
# Add text-to-speech library
import pyttsx3

# Set window background color to match the blue theme
Window.clearcolor = (64/255, 89/255, 140/255, 1)  # Darker blue background

# Hugging Face API Setup
API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.1"
HEADERS = {"Authorization": "Bearer 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"}
session = requests.Session()

# Define the Kivy language string for styling
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

<PoetryGeneratorScreen>:
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
                text: "Poetry Generator"
                font_size: '20sp'
                color: 1, 1, 1, 1
                size_hint_x: 0.8
                
            Widget:
                size_hint_x: None
                width: dp(40)
        
        # Spacing
        Widget:
            size_hint_y: None
            height: dp(10)
            
        # User Input Text Area with Voice Button
        BoxLayout:
            orientation: 'horizontal'
            size_hint_y: None
            height: dp(70)
            spacing: dp(10)
            
            CustomTextInput:
                id: theme_input
                hint_text: "Enter a theme for your poem..."
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
                text: "Generate Poem"
                font_size: '16sp'
                size_hint_x: 0.5
                color: 64/255, 89/255, 140/255, 1  # Dark blue text
                on_press: root.generate_poem()
                
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
            
        # Poem Output Area - rounded rectangle with voice button
        BoxLayout:
            orientation: 'vertical'
            size_hint_y: 0.6
            
            RoundedBoxLayout:
                orientation: "vertical"
                padding: dp(10)
                
                CustomTextInput:
                    id: poem_output
                    hint_text: "Your poem will appear here..."
                    background_color: 190/255, 208/255, 244/255, 1
                    foreground_color: 0, 0, 0, 1
                    readonly: True
                    multiline: True
            
            # Voice output button
            BoxLayout:
                orientation: 'horizontal'
                size_hint_y: None
                height: dp(50)
                padding: [0, dp(10), 0, 0]
                
                Widget:
                    size_hint_x: 0.7
                
                CircularButton:
                    id: speak_button
                    text: "🔊"
                    size_hint_x: None
                    width: dp(50)
                    on_press: root.speak_poem()
                    disabled: not poem_output.text
'''

Builder.load_string(KV)

# ------------------------------
# 🔹 Poetry Generator Screen
# ------------------------------
class PoetryGeneratorScreen(Screen):
    def __init__(self, **kwargs):
        super(PoetryGeneratorScreen, self).__init__(**kwargs)
        self.recording = False
        self.recognizer = sr.Recognizer()
        self.speaking = False
        self.init_tts_engine()
        self.auto_speak = True  # Flag to control auto-speaking feature
        
    def init_tts_engine(self):
        # Initialize text-to-speech engine
        try:
            self.tts_engine = pyttsx3.init()
            # Configure properties for poetry reading
            self.tts_engine.setProperty('rate', 140)  # Slightly slower rate for poetry
            self.tts_engine.setProperty('volume', 1.0)  # Full volume
            
            # Try to find a voice that sounds good for poetry
            voices = self.tts_engine.getProperty('voices')
            for voice in voices:
                if "female" in voice.name.lower():  # Female voices often work well for poetry
                    self.tts_engine.setProperty('voice', voice.id)
                    break
        except Exception as e:
            print(f"TTS initialization error: {str(e)}")
            self.tts_engine = None
        
    def go_back(self):
        if self.recording:
            self.toggle_voice_input()  # Stop recording if active
        if self.speaking:
            self.stop_speaking()  # Stop speaking if active
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
                # Update the UI in the main thread
                Clock.schedule_once(lambda dt: self.update_text(text), 0)
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
    
    def update_text(self, text):
        # First update the text input
        current_text = self.ids.theme_input.text
        if current_text and not current_text.endswith(' '):
            self.ids.theme_input.text = f"{current_text} {text}"
        else:
            self.ids.theme_input.text = f"{current_text}{text}"
        
        self.ids.feedback_label.text = "Voice input received! Generating poem..."
        
        # Automatically generate poem after voice input is received
        # Use a short delay to allow the UI to update first
        Clock.schedule_once(lambda dt: self.generate_poem(), 0.5)
    
    def update_feedback(self, message):
        self.ids.feedback_label.text = message
    
    def reset_recording_state(self):
        self.recording = False
        self.ids.voice_button.text = "🎤"
        self.ids.voice_button.background_color = (64/255, 89/255, 140/255, 1)
    
    def generate_poem(self):
        theme = self.ids.theme_input.text.strip()
        if theme:
            # Show loading message
            self.ids.feedback_label.text = "Generating poem..."
            
            # Run the API call in a background thread to avoid freezing the UI
            threading.Thread(target=self._execute_api_call, args=(theme,)).start()
        else:
            self.ids.feedback_label.text = "Please enter a theme for your poem."
    
    def _execute_api_call(self, theme):
        try:
            # Use the Hugging Face API to generate a poem
            response = session.post(
                API_URL, 
                headers=HEADERS, 
                json={"inputs": f"Write a structured poem about: {theme}"}
            )
            
            # Parse the response
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0 and 'generated_text' in result[0]:
                    generated_text = result[0]['generated_text'].strip()
                    # Update UI in main thread
                    Clock.schedule_once(lambda dt: self._update_poem(generated_text), 0)
                else:
                    # Handle unexpected response format
                    Clock.schedule_once(
                        lambda dt: self.update_feedback("Error: Unexpected response format from API"), 
                        0
                    )
            else:
                # Handle HTTP errors
                error_message = f"API Error ({response.status_code}): {response.text}"
                Clock.schedule_once(lambda dt: self.update_feedback(error_message), 0)
                
        except Exception as e:
            # Create a local variable to avoid lambda scope issues
            error_message = f"Error: {str(e)}"
            Clock.schedule_once(lambda dt: self.update_feedback(error_message), 0)
    
    def _update_poem(self, poem_text):
        self.ids.poem_output.text = poem_text
        self.ids.feedback_label.text = "Poem generated successfully!"
        
        # Enable the speak button now that we have a poem
        try:
            self.ids.speak_button.disabled = False
        except:
            pass
        
        # Automatically speak the poem after generation
        if self.auto_speak:
            Clock.schedule_once(lambda dt: self.speak_poem(), 1)
    
    def speak_poem(self):
        """Read the poem aloud using text-to-speech"""
        if not self.tts_engine:
            self.ids.feedback_label.text = "Text-to-speech engine not available"
            return
            
        poem_text = self.ids.poem_output.text.strip()
        if not poem_text:
            return
            
        # Change button appearance
        self.ids.speak_button.text = "⏹️"
        self.ids.speak_button.background_color = (1, 0, 0, 1)  # Red for speaking
        self.speaking = True
        
        # Update feedback
        self.ids.feedback_label.text = "Reading poem..."
        
        # Start speaking in a separate thread
        threading.Thread(target=self._speak_text, args=(poem_text,)).start()
    
    def _speak_text(self, text):
        try:
            # Format the poem for better TTS reading
            # For poetry, we want to add slight pauses at the end of lines
            formatted_text = self._format_poem_for_speech(text)
            
            # Speak the text
            self.tts_engine.say(formatted_text)
            self.tts_engine.runAndWait()
        except Exception as e:
            error_message = f"Speech error: {str(e)}"
            Clock.schedule_once(lambda dt: self.update_feedback(error_message), 0)
        
        # Reset button in the main thread
        Clock.schedule_once(lambda dt: self.reset_speaking_state(), 0)
    
    def _format_poem_for_speech(self, poem):
        """Format the poem to make it sound better when read aloud
        - Add pauses at the end of lines
        - Emphasize certain words
        - Add proper inflection
        """
        # Simple implementation - add commas at the end of lines for natural pauses
        lines = poem.split('\n')
        formatted_lines = []
        
        for line in lines:
            if line.strip():  # Skip empty lines
                # If the line doesn't end with punctuation, add a comma for a pause
                if not line.strip()[-1] in ['.', ',', '!', '?', ':', ';']:
                    line += ','
                formatted_lines.append(line)
            else:
                # Add a longer pause for stanza breaks (empty lines)
                formatted_lines.append(".")  # Period causes a longer pause
                
        return '\n'.join(formatted_lines)
    
    def stop_speaking(self):
        """Stop the TTS engine if it's speaking"""
        if self.tts_engine and self.speaking:
            self.tts_engine.stop()
            self.reset_speaking_state()
    
    def reset_speaking_state(self):
        """Reset the speaking button state"""
        self.speaking = False
        self.ids.speak_button.text = "🔊"
        self.ids.speak_button.background_color = (64/255, 89/255, 140/255, 1)
        self.ids.feedback_label.text = ""
    
    def clear_inputs(self):
        self.ids.theme_input.text = ''
        self.ids.poem_output.text = ''
        self.ids.feedback_label.text = ''
        
        # Disable speak button when there's no poem
        try:
            self.ids.speak_button.disabled = True
        except:
            pass

# ------------------------------
# 🔹 Main App Setup
# ------------------------------
class PoetryApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(PoetryGeneratorScreen(name="poetry"))
        # Add a menu screen (placeholder)
        return sm

if __name__ == '__main__':
    PoetryApp().run()