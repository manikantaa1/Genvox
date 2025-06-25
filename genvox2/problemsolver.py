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
from kivy.utils import platform
# Add text-to-speech library
import pyttsx3
try:
    from plyer import vibrator
except ImportError:
    vibrator = None

# Set window background color to match the blue theme
Window.clearcolor = (64/255, 89/255, 140/255, 1)  # Darker blue background

# Together API Setup
TOGETHER_API_URL = "https://api.together.xyz/v1/completions"
TOGETHER_API_KEY = "6fcd9484266e33a4e349a09c463bd9b5b0c1f6b66277631ef78e634c65d8ac2c"  # Replace with your actual API key
session = requests.Session()

# Define the Kivy language string for styling - same style as the Poetry Generator
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

<ProblemSolverScreen>:
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
                text: "Problem Solver"
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
            
        # Problem description input with voice button
        BoxLayout:
            orientation: 'horizontal'
            size_hint_y: None
            height: dp(120)
            spacing: dp(10)
            
            CustomTextInput:
                id: problem_input
                hint_text: "Describe your problem here..."
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
                text: "Solve Problem"
                font_size: '16sp'
                size_hint_x: 0.5
                color: 64/255, 89/255, 140/255, 1  # Dark blue text
                on_press: root.solve_problem()
                
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
            
        # Solution Output Area
        BoxLayout:
            orientation: 'vertical'
            size_hint_y: 0.5
            
            RoundedBoxLayout:
                orientation: "vertical"
                padding: dp(10)
                
                CustomTextInput:
                    id: solution_output
                    hint_text: "Your solution will appear here..."
                    background_color: 190/255, 208/255, 244/255, 1
                    foreground_color: 0, 0, 0, 1
                    readonly: True
                    multiline: True
            
            # Action buttons
            BoxLayout:
                orientation: 'horizontal'
                size_hint_y: None
                height: dp(50)
                padding: [0, dp(10), 0, 0]
                spacing: dp(10)
                
                Widget:
                    size_hint_x: 0.5
                
                CircularButton:
                    id: speak_button
                    text: "🔊"
                    size_hint_x: None
                    width: dp(50)
                    on_press: root.speak_solution()
                    disabled: not solution_output.text
                
                CircularButton:
                    id: copy_button
                    text: "📋"
                    size_hint_x: None
                    width: dp(50)
                    on_press: root.copy_solution()
                    disabled: not solution_output.text
'''

Builder.load_string(KV)

# ------------------------------
# 🔹 Problem Solver Screen
# ------------------------------
class ProblemSolverScreen(Screen):
    def __init__(self, **kwargs):
        super(ProblemSolverScreen, self).__init__(**kwargs)
        self.recording = False
        self.speaking = False
        self.recognizer = sr.Recognizer()
        self.init_tts_engine()
        self.auto_speak = False  # Not automatically speaking solutions
        self.auto_solve_after_voice = True  # Automatically solve problems after voice input
        
    def init_tts_engine(self):
        # Initialize text-to-speech engine
        try:
            self.tts_engine = pyttsx3.init()
            # Configure properties for clear speech
            self.tts_engine.setProperty('rate', 150)  # Normal speaking rate
            self.tts_engine.setProperty('volume', 1.0)  # Full volume
            
            # Try to find a suitable voice
            voices = self.tts_engine.getProperty('voices')
            for voice in voices:
                # Choose a clear, neutral voice
                if "english" in voice.name.lower():
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
            if platform == 'android' and vibrator and hasattr(vibrator, 'vibrate'):
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
                Clock.schedule_once(lambda dt: self.update_feedback("Could not understand audio"), 0)
            except sr.RequestError:
                error_msg = "Error connecting to Google Speech Recognition service"
                Clock.schedule_once(lambda dt: self.update_feedback(error_msg), 0)
                
        except Exception as e:
            error_message = f"Error: {str(e)}"
            Clock.schedule_once(lambda dt: self.update_feedback(error_message), 0)
        
        # Reset recording state in the main thread
        Clock.schedule_once(lambda dt: self.reset_recording_state(), 0)
    
    def update_text(self, text):
        # First update the text input
        current_text = self.ids.problem_input.text
        if current_text and not current_text.endswith(' '):
            self.ids.problem_input.text = f"{current_text} {text}"
        else:
            self.ids.problem_input.text = f"{current_text}{text}"
        
        # Auto-solve after voice input if enabled
        if self.auto_solve_after_voice:
            self.ids.feedback_label.text = "Voice input received! Solving problem..."
            Clock.schedule_once(lambda dt: self.solve_problem(), 0.5)
        else:
            self.ids.feedback_label.text = "Voice input received!"
    
    def update_feedback(self, message):
        self.ids.feedback_label.text = message
    
    def reset_recording_state(self):
        self.recording = False
        self.ids.voice_button.text = "🎤"
        self.ids.voice_button.background_color = (64/255, 89/255, 140/255, 1)
    
    def solve_problem(self):
        problem = self.ids.problem_input.text.strip()
        if problem:
            # Show loading message
            self.ids.feedback_label.text = "Analyzing problem..."
            
            # Provide haptic feedback if on Android
            if platform == 'android' and vibrator and hasattr(vibrator, 'vibrate'):
                vibrator.vibrate(0.1)  # Short vibration
            
            # Run the API call in a background thread to avoid freezing the UI
            threading.Thread(target=self._generate_solution, args=(problem,)).start()
        else:
            self.ids.feedback_label.text = "Please describe your problem first."
    
    def _generate_solution(self, problem):
        try:
            # Using Together API for the problem solving
            headers = {
                "Authorization": f"Bearer {TOGETHER_API_KEY}",
                "Content-Type": "application/json"
            }
            
            # Prepare the request payload for Together API
            # Adjust model and parameters as needed
            payload = {
                "model": "mistralai/Mixtral-8x7B-Instruct-v0.1",  # Or any other model from Together
                "prompt": f"I need to solve the following problem step by step:\n\n{problem}\n\n",
                "max_tokens": 1024,
                "temperature": 0.7,
                "top_p": 0.9,
                "frequency_penalty": 0,
                "presence_penalty": 0
            }
            
            # Make the API request
            response = session.post(TOGETHER_API_URL, headers=headers, json=payload)
            
            # Parse the response
            if response.status_code == 200:
                result = response.json()
                # Extract solution from the response
                # Note: Adjust this based on the actual structure of Together API response
                if 'choices' in result and len(result['choices']) > 0:
                    solution_text = result['choices'][0]['text'].strip()
                    # Update UI in main thread
                    Clock.schedule_once(lambda dt: self._update_solution(solution_text), 0)
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
    
    def _update_solution(self, solution_text):
        self.ids.solution_output.text = solution_text
        self.ids.feedback_label.text = "Solution generated!"
        
        # Enable the buttons now that we have a solution
        self.ids.speak_button.disabled = False
        self.ids.copy_button.disabled = False
        
        # Automatically speak the solution if auto_speak is enabled
        if self.auto_speak:
            Clock.schedule_once(lambda dt: self.speak_solution(), 0.5)
    
    def speak_solution(self):
        """Read the solution aloud using text-to-speech"""
        if not self.tts_engine:
            self.ids.feedback_label.text = "Text-to-speech engine not available"
            return
            
        solution_text = self.ids.solution_output.text.strip()
        if not solution_text:
            return
            
        # Change button appearance
        self.ids.speak_button.text = "⏹️"
        self.ids.speak_button.background_color = (1, 0, 0, 1)  # Red for speaking
        self.speaking = True
        
        # Update feedback
        self.ids.feedback_label.text = "Reading solution..."
        
        # Start speaking in a separate thread
        threading.Thread(target=self._speak_text, args=(solution_text,)).start()
    
    def _speak_text(self, text):
        try:
            # Format the text for better TTS reading
            formatted_text = self._format_text_for_speech(text)
            
            # Speak the text
            self.tts_engine.say(formatted_text)
            self.tts_engine.runAndWait()
        except Exception as e:
            error_message = f"Speech error: {str(e)}"
            Clock.schedule_once(lambda dt: self.update_feedback(error_message), 0)
        
        # Reset button in the main thread
        Clock.schedule_once(lambda dt: self.reset_speaking_state(), 0)
    
    def _format_text_for_speech(self, text):
        """Format the text to make it sound better when read aloud"""
        # Add pauses at appropriate points
        # Replace certain symbols with their spoken equivalents
        text = text.replace('=', 'equals')
        text = text.replace('+', 'plus')
        text = text.replace('-', 'minus')
        text = text.replace('*', 'times')
        text = text.replace('/', 'divided by')
        text = text.replace('√', 'square root of')
        text = text.replace('^', 'to the power of')
        
        # Add pauses after sentences
        text = text.replace('. ', '. <break> ')
        
        return text
    
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
        self.ids.feedback_label.text = "Solution ready"
    
    def copy_solution(self):
        """Copy the solution to clipboard"""
        solution = self.ids.solution_output.text
        if solution:
            from kivy.core.clipboard import Clipboard
            Clipboard.copy(solution)
            self.ids.feedback_label.text = "Solution copied to clipboard!"
            
            # Provide haptic feedback if on Android
            if platform == 'android' and vibrator and hasattr(vibrator, 'vibrate'):
                vibrator.vibrate(0.1)  # Short vibration
    
    def clear_inputs(self):
        self.ids.problem_input.text = ''
        self.ids.solution_output.text = ''
        self.ids.feedback_label.text = ''
        self.ids.speak_button.disabled = True
        self.ids.copy_button.disabled = True
        
        # Stop speech if it's currently speaking
        if self.speaking:
            self.stop_speaking()

# ------------------------------
# 🔹 Main App Setup
# ------------------------------
class ProblemSolverApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(ProblemSolverScreen(name="problemsolver"))
        # To add a menu screen:
        # sm.add_widget(MenuScreen(name="menu"))
        return sm

if __name__ == '__main__':
    ProblemSolverApp().run()