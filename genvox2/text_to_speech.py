from kivy.lang import Builder
from kivy.uix.screenmanager import Screen
from kivy.core.audio import SoundLoader
from kivy.clock import Clock
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.slider import Slider
from kivy.utils import platform
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.graphics import Color, Rectangle, RoundedRectangle
import os
from gtts import gTTS
from plyer import filechooser  # Ensure plyer is installed for file operations
from tkinter import filedialog, Tk  # For desktop file dialogs

if platform == "android":
    from android.storage import primary_external_storage
    from android.permissions import request_permissions, Permission
    request_permissions([Permission.WRITE_EXTERNAL_STORAGE, Permission.READ_EXTERNAL_STORAGE])

# Set the background color to match the blue theme
Window.clearcolor = (64/255, 89/255, 140/255, 1)  # Darker blue background

# Define the Kivy language string for our app
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
    hint_text: "Type here..."  # Test if placeholder text appears
    hint_text_color: 1, 1, 1, 1  # White hint text to see if it's working
    font_size: '16sp'
    multiline: False
    padding: [10, 10, 10, 10]

<RoundedBoxLayout@BoxLayout>:
    canvas.before:
        Color:
            rgba: 150/255, 178/255, 222/255, 1  # Light blue
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [20]

<MenuScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: dp(16)
        spacing: dp(10)
        
        Label:
            text: 'Menu Screen'
            font_size: '24sp'
            size_hint_y: None
            height: dp(50)
            
        Widget:
            # Spacer

<SpeechScreen>:
    name: "speech"

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
                text: "AI Speech Generator"
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

        # Text input area with rounded corners
        BoxLayout:
            orientation: 'horizontal'
            size_hint_y: None
            height: dp(60)
            spacing: dp(10)
            
            CustomTextInput:
                id: text_input
                hint_text: "Enter text here..."
                size_hint_x: 0.85
            
            CircularButton:
                text: "U"
                on_press: root.upload_file()
                pos_hint: {"center_y": 0.5}
        
        # Generate button
        BoxLayout:
            orientation: 'vertical'
            size_hint_y: None
            height: dp(80)
            padding: [dp(0), dp(15), dp(0), dp(15)]
            
            CustomButton:
                text: "Generate Speech"
                font_size: '16sp'
                size_hint: None, None
                size: dp(200), dp(50)
                pos_hint: {"center_x": 0.5}
                color: 64/255, 89/255, 140/255, 1  # Dark blue text
                on_press: root.generate_speech()
            
        # Status label (hidden by default)
        Label:
            id: loading_label
            text: ""
            color: 1, 1, 1, 1
            size_hint_y: None
            height: dp(0)
            opacity: 0
                
        # Player controls - rounded rectangle
        RoundedBoxLayout:
            orientation: "vertical"
            size_hint_y: None
            height: dp(120)
            padding: dp(16)
            spacing: dp(10)
            
            Slider:
                id: progress_bar
                min: 0
                max: 1
                value: 0
                size_hint_x: 1
                cursor_size: (dp(20), dp(20))
                
            BoxLayout:
                orientation: "horizontal"
                size_hint_y: None
                height: dp(50)
                spacing: dp(10)
                pos_hint: {"center_x": 0.5}

                CircularButton:
                    id: play_button
                    text: "play"
                    on_press: root.play_audio()
                    pos_hint: {"center_y": 0.5}

                Label:
                    id: audio_status
                    text: "00 / 00"
                    color: 1, 1, 1, 1
                    size_hint_x: 0.6

                CircularButton:
                    id: volume_button
                    text: "vol"
                    on_press: root.adjust_volume()
                    pos_hint: {"center_y": 0.5}

                CircularButton:
                    text: "Dwnld"
                    on_press: root.download_audio()
                    pos_hint: {"center_y": 0.5}
        
        # Flexible spacer at the bottom to push content up
        Widget:
            size_hint_y: 1
'''
Builder.load_string(KV)

class SpeechScreen(Screen):
    def __init__(self, **kwargs):
        super(SpeechScreen, self).__init__(**kwargs)
        self.audio_path = "temp_speech.mp3"
        self.sound = None
        self.paused_position = 0
        self.volume = 1.0
        Clock.schedule_once(self.init_ui, 0.1)
    
    def init_ui(self, dt):
        # Initialize UI elements
        self.ids.loading_label.opacity = 0
        self.ids.loading_label.height = dp(0)
        self.ids.progress_bar.value = 0
        self.ids.audio_status.text = "00 / 00"
        self.ids.play_button.text = "play"
    
    def on_enter(self):
        # Reset UI elements when entering the screen
        self.ids.loading_label.opacity = 0
        self.ids.loading_label.height = dp(0)
        self.ids.progress_bar.value = 0
        self.ids.audio_status.text = "00 / 00"
        self.ids.play_button.text = "play"
    
    def generate_speech(self):
        # Get the text input
        text_input = self.ids.text_input.text.strip()
        if not text_input:
            self.show_loading_label("Please enter some text!")
            return
        
        # Show loading label
        self.show_loading_label("Generating speech...")
        
        try:
            tts = gTTS(text=text_input, lang="en")
            tts.save(self.audio_path)
            self.sound = SoundLoader.load(self.audio_path)
            if self.sound:
                self.sound.volume = self.volume
                self.ids.audio_status.text = f"00 / {int(self.sound.length)}"
                self.ids.progress_bar.max = self.sound.length
            self.show_loading_label("Speech generated!")
            Clock.schedule_once(lambda dt: self.hide_loading_label(), 2)
        except Exception as e:
            self.show_loading_label(f"Error: {str(e)}")
    
    def show_loading_label(self, message):
        self.ids.loading_label.text = message
        self.ids.loading_label.opacity = 1
        self.ids.loading_label.height = dp(30)
    
    def hide_loading_label(self):
        self.ids.loading_label.opacity = 0
        self.ids.loading_label.height = dp(0)
    
    def go_back(self):
        self.manager.current = "menu"
    
    def play_audio(self):
        if self.sound:
            try:
                if self.sound.state == "play":
                    self.paused_position = self.sound.get_pos()
                    self.sound.stop()
                    self.ids.play_button.text = "play"
                else:
                    self.sound.seek(self.paused_position)
                    self.sound.play()
                    self.ids.play_button.text = "⏸"
                    Clock.schedule_interval(self.update_audio_status, 1)
            except Exception as e:
                print(f"Error playing audio: {str(e)}")
    
    def update_audio_status(self, dt):
        if self.sound and self.sound.state == "play":
            current_time = int(self.sound.get_pos())
            duration = int(self.sound.length)
            self.ids.audio_status.text = f"{current_time:02d} / {duration:02d}"
            self.ids.progress_bar.value = current_time
        elif self.sound and self.sound.state == "stop":
            self.ids.play_button.text = "play"
            return False
        return True
    
    def adjust_volume(self):
        if self.sound:
            try:
                if self.volume == 1.0:
                    self.volume = 0.5
                    self.ids.volume_button.text = "🔉"
                else:
                    self.volume = 1.0
                    self.ids.volume_button.text = "🔊"
                self.sound.volume = self.volume
            except Exception as e:
                print(f"Error adjusting volume: {str(e)}")
    
    def download_audio(self):
        if platform == "android":
            self.download_audio_android()
        else:
            self.download_audio_desktop()
    
    def download_audio_desktop(self):
        try:
            save_path = filedialog.asksaveasfilename(
                defaultextension=".mp3",
                filetypes=[("MP3 files", "*.mp3")],
                title="Save Audio File"
            )
            if save_path:
                import shutil
                shutil.copy2(self.audio_path, save_path)
                self.show_loading_label("File saved successfully")
                Clock.schedule_once(lambda dt: self.hide_loading_label(), 2)
        except Exception as e:
            self.show_loading_label(f"Error saving file: {str(e)}")
    
    def download_audio_android(self):
        try:
            storage_path = primary_external_storage()
            downloads_dir = os.path.join(storage_path, "Download")
            if not os.path.exists(downloads_dir):
                os.makedirs(downloads_dir)
            save_path = os.path.join(downloads_dir, "speech_output.mp3")
            import shutil
            shutil.copy2(self.audio_path, save_path)
            self.show_loading_label("Saved to Downloads folder")
            Clock.schedule_once(lambda dt: self.hide_loading_label(), 2)
        except Exception as e:
            self.show_loading_label(f"Error saving: {str(e)}")
    
    def upload_file(self):
        if platform == "android":
            self.upload_file_android()
        else:
            self.upload_file_desktop()
    
    def upload_file_desktop(self):
        try:
            file_path = filedialog.askopenfilename(
                filetypes=[("Text files", "*.txt")],
                title="Select a Text File"
            )
            if file_path:
                with open(file_path, "r", encoding="utf-8") as file:
                    text_content = file.read()
                    self.ids.text_input.text = text_content
        except Exception as e:
            self.show_loading_label(f"Error loading file: {str(e)}")
    
    def upload_file_android(self):
        try:
            file_path = filechooser.open_file(filters=[("*.txt")])[0]
            if file_path:
                with open(file_path, "r", encoding="utf-8") as file:
                    text_content = file.read()
                    self.ids.text_input.text = text_content
        except Exception as e:
            self.show_loading_label(f"Error loading file: {str(e)}")