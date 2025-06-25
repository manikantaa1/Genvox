from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.image import AsyncImage
from kivy.clock import Clock
from kivy.graphics import Color, RoundedRectangle
import threading
from together import Together
import speech_recognition as sr  # <-- Voice recognition

PRIMARY_COLOR = (4/255, 44/255, 52/255, 1)
BUTTON_COLOR = (30/255, 112/255, 122/255, 1)

class ImageGenerationScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Main layout
        self.layout = BoxLayout(orientation='vertical', padding=15, spacing=10)

        # Back Button
        back_btn = Button(text="⬅ Back to Menu", size_hint=(1, 0.1), background_color=BUTTON_COLOR)
        back_btn.bind(on_press=self.go_back)
        self.layout.add_widget(back_btn)

        # Prompt input & voice button in horizontal box
        input_box = BoxLayout(orientation='horizontal', size_hint=(1, 0.1), spacing=10)
        
        self.prompt_input = TextInput(
            hint_text="Enter your prompt here", 
            size_hint=(0.85, 1),
            foreground_color=(1,1,1,1), 
            background_color=PRIMARY_COLOR, 
            cursor_color=(1,1,1,1)
        )
        input_box.add_widget(self.prompt_input)

        voice_btn = Button(text="🎤", size_hint=(0.15, 1), background_color=BUTTON_COLOR)
        voice_btn.bind(on_press=self.start_voice_input)
        input_box.add_widget(voice_btn)

        self.layout.add_widget(input_box)

        # Generate Button
        self.generate_btn = Button(text="Generate Image", size_hint=(1, 0.1), background_color=BUTTON_COLOR)
        self.generate_btn.bind(on_press=self.start_image_generation)
        self.layout.add_widget(self.generate_btn)

        # Status Label
        self.status_label = Label(text="Status: Waiting...", size_hint=(1, 0.1), color=(1,1,1,1))
        self.layout.add_widget(self.status_label)

        # Image Display
        self.image_display = AsyncImage(size_hint=(1, 0.6))
        self.layout.add_widget(self.image_display)

        # Background Color
        with self.canvas.before:
            Color(*PRIMARY_COLOR)
            self.rect = RoundedRectangle(size=self.size, pos=self.pos)
        self.bind(size=self.update_rect, pos=self.update_rect)

        self.add_widget(self.layout)

    def update_rect(self, *args):
        self.rect.size = self.size
        self.rect.pos = self.pos

    def go_back(self, instance):
        self.manager.current = "menu"

    # ✅ Voice Input Handler
    def start_voice_input(self, instance):
        threading.Thread(target=self.capture_voice, daemon=True).start()

    def capture_voice(self):
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            print("Listening for voice input...")
            Clock.schedule_once(lambda dt: self.update_status("🎙️ Listening..."))
            try:
                audio = recognizer.listen(source, timeout=5)
                Clock.schedule_once(lambda dt: self.update_status("Processing voice..."))
                text = recognizer.recognize_google(audio)
                print("Voice Input Recognized:", text)
                Clock.schedule_once(lambda dt: self.prompt_input_update(text))
            except Exception as e:
                print(f"Voice input error: {e}")
                Clock.schedule_once(lambda dt: self.update_status("❌ Voice input failed!"))

    def prompt_input_update(self, text):
        self.prompt_input.text = text
        self.status_label.text = "✅ Voice input received!"

    # Image Generation
    def start_image_generation(self, instance):
        prompt = self.prompt_input.text.strip()
        if not prompt:
            self.status_label.text = "❗ Please enter a prompt!"
            return

        self.status_label.text = "⏳ Generating image..."
        self.image_display.source = ""  # Clear previous image

        threading.Thread(target=self.generate_image_thread, args=(prompt,), daemon=True).start()

    def generate_image_thread(self, prompt):
        try:
            client = Together(api_key="6fcd9484266e33a4e349a09c463bd9b5b0c1f6b66277631ef78e634c65d8ac2c")
            response = client.images.generate(
                prompt=prompt,
                model="stabilityai/stable-diffusion-xl-base-1.0",
                width=1024,
                height=1024,
                num_images=1
            )

            print("Full API Response:", response)  # For debug

            if response and hasattr(response, "data") and response.data:
                image_url = response.data[0].url
                print("Generated Image URL:", image_url)
                Clock.schedule_once(lambda dt: self.display_image(image_url))
            else:
                Clock.schedule_once(lambda dt: self.update_status("❌ Failed to get image from API!"))

        except Exception as e:
            print(f"Error Occurred: {str(e)}")
            Clock.schedule_once(lambda dt: self.update_status(f"Error: {str(e)}"))

    def display_image(self, url):
        if url:
            print("Displaying image...")
            self.image_display.source = url
            self.status_label.text = "✅ Image Generated Successfully!"
        else:
            self.status_label.text = "❌ No image URL received!"

    def update_status(self, msg):
        self.status_label.text = msg
