import os
import threading
import random
import math
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.core.window import Window
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics import Color, RoundedRectangle, Ellipse, Rectangle, Line
from kivy.utils import get_color_from_hex
from kivy.animation import Animation
from kivy.metrics import dp, sp
from kivy.clock import Clock
from kivy.properties import NumericProperty, BooleanProperty, ObjectProperty
from kivy.uix.image import AsyncImage
from together import Together  # Ensure this import is correct and the module is available

# Voice recognition and synthesis imports
import speech_recognition as sr
import pyttsx3
import queue
import time

# Get API Key from environment variable for security
TOGETHER_API_KEY = "6fcd9484266e33a4e349a09c463bd9b5b0c1f6b66277631ef78e634c65d8ac2c"
client = Together(api_key=TOGETHER_API_KEY)

# Color Palette
PRIMARY_COLOR = get_color_from_hex("#6a5acd")  # Purple for bot messages
SECONDARY_COLOR = get_color_from_hex("#8360c3")  # Light purple for user messages
ACCENT_COLOR = get_color_from_hex("#ff6f61")  # Coral for buttons
BACKGROUND_COLOR = get_color_from_hex("#1e1e2f")  # Dark Blue background
TEXT_COLOR = get_color_from_hex("#ffffff")  # White text
LIGHT_BACKGROUND_COLOR = get_color_from_hex("#ffffff")  # White background for light theme
LIGHT_TEXT_COLOR = get_color_from_hex("#000000")  # Black text for light theme

# ------------------------------
# 🔹 Custom Image Button (for back and profile buttons)
# ------------------------------
class ImageButton(Button):
    source = ObjectProperty(None)
    hover = BooleanProperty(False)
    
    def __init__(self, **kwargs):
        super(ImageButton, self).__init__(**kwargs)
        self.size_hint = (None, None)
        self.size = (50, 50)
        self.background_normal = ''
        self.background_color = (0, 0, 0, 0)  # Transparent background
        self.bind(pos=self.update_canvas, size=self.update_canvas)
        Clock.schedule_once(self.update_canvas, 0)
    
    def update_canvas(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            # Light blue circle background for the image
            Color(100/255, 180/255, 240/255, 1 if not self.hover else 120/255, 190/255, 250/255, 1)
            Ellipse(pos=self.pos, size=self.size)
        
        # Remove the image widget if it exists
        if hasattr(self, 'image'):
            self.remove_widget(self.image)
        
        # Add the image widget
        if self.source:
            from kivy.uix.image import Image
            self.image = Image(source=self.source, 
                              size=(self.size[0] * 0.8, self.size[1] * 0.8),
                              pos=(self.pos[0] + self.size[0] * 0.1, self.pos[1] + self.size[1] * 0.1))
            self.add_widget(self.image)
    
    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            anim = Animation(size=(45, 45), duration=0.1)
            anim.start(self)
        return super(ImageButton, self).on_touch_down(touch)
    
    def on_touch_up(self, touch):
        if self.collide_point(*touch.pos):
            anim = Animation(size=(50, 50), duration=0.2, t='out_back')
            anim.start(self)
        return super(ImageButton, self).on_touch_up(touch)
    
    def on_mouse_pos(self, *args):
        if not self.get_root_window():
            return
        pos = args[1]
        if self.collide_point(*self.to_widget(*pos)):
            if not self.hover:
                self.hover = True
                anim = Animation(size=(52, 52), duration=0.1)
                anim.start(self)
                self.update_canvas()
        else:
            if self.hover:
                self.hover = False
                anim = Animation(size=(50, 50), duration=0.1)
                anim.start(self)
                self.update_canvas()

# ------------------------------
# 🔹 Particle Class for Animated Background
# ------------------------------
class Particle:
    def __init__(self, x, y, size):
        self.x = x
        self.y = y
        self.size = size
        self.max_size = size
        self.min_size = size * 0.7
        self.speed = random.uniform(0.5, 2.5)
        self.alpha = random.uniform(0.1, 0.5)
        self.direction = random.uniform(0, 360)
        self.dx = self.speed * math.cos(math.radians(self.direction))
        self.dy = self.speed * math.sin(math.radians(self.direction))
        # Enhanced color palette with more variety
        self.color = random.choice([
            (0.9, 0.95, 1),    # White-blue
            (0.7, 0.8, 1),     # Light blue
            (0.6, 0.7, 0.9),   # Blue
            (0.7, 0.6, 0.9),   # Purple-blue
            (0.5, 0.7, 1),     # Sky blue
            (0.8, 0.6, 1),     # Lavender
            (0.6, 0.9, 1)      # Cyan-blue
        ])
        # Random phase offset for individual particle pulsing
        self.phase_offset = random.uniform(0, 2 * math.pi)
        # Random lifetime for particle renewal
        self.lifetime = random.uniform(10, 20)
        self.age = 0

# ------------------------------
# 🔹 Animated Background Widget
# ------------------------------
class AnimatedBackground(FloatLayout):
    particles = []
    time = NumericProperty(0)
    glow_points = []
    mouse_x = NumericProperty(0)
    mouse_y = NumericProperty(0)
    mouse_time = NumericProperty(0)
    
    def __init__(self, **kwargs):
        super(AnimatedBackground, self).__init__(**kwargs)
        self.create_particles()
        self.create_glow_points()
        Clock.schedule_interval(self.update, 1/60)
        # Track mouse position for interactive effects
        Window.bind(mouse_pos=self.on_mouse_pos)
        
    def on_mouse_pos(self, window, pos):
        self.mouse_x = pos[0]
        self.mouse_y = pos[1]
        self.mouse_time = 0  # Reset mouse effect timer
    
    def create_particles(self):
        self.particles = []
        # Increase number of particles for a denser effect
        for _ in range(80):
            x = random.uniform(0, Window.width)
            y = random.uniform(0, Window.height)
            size = random.uniform(2, 7)
            self.particles.append(Particle(x, y, size))
    
    def create_glow_points(self):
        # Create glow points for additional ambient lighting effects
        self.glow_points = []
        for _ in range(3):
            x = random.uniform(Window.width * 0.2, Window.width * 0.8)
            y = random.uniform(Window.height * 0.2, Window.height * 0.8)
            size = random.uniform(150, 300)
            color = random.choice([
                (0.3, 0.5, 0.9),  # Blue
                (0.4, 0.3, 0.8),  # Purple
                (0.2, 0.6, 0.8),  # Teal
            ])
            alpha = random.uniform(0.05, 0.15)
            self.glow_points.append((x, y, size, color, alpha))
            
    def update(self, dt):
        self.time += dt
        self.mouse_time += dt
        self.canvas.clear()
        
        with self.canvas:
            # Background gradient
            Color(0.12, 0.15, 0.3, 1)  # Dark blue base
            Rectangle(pos=(0, 0), size=(Window.width, Window.height))
            
            # Multiple ambient glow points that slowly move
            for i, (x, y, size, color, alpha) in enumerate(self.glow_points):
                # Slowly move glow points
                new_x = x + math.sin(self.time * 0.2 + i) * 0.5
                new_y = y + math.cos(self.time * 0.15 + i * 0.7) * 0.5
                
                # Pulsating size
                pulse_size = size + size * 0.2 * math.sin(self.time * 0.3 + i)
                
                # Draw glow
                Color(color[0], color[1], color[2], alpha * (0.7 + 0.3 * math.sin(self.time * 0.2 + i)))
                Ellipse(pos=(new_x - pulse_size/2, new_y - pulse_size/2), 
                       size=(pulse_size, pulse_size))
                
                # Update position for next frame
                self.glow_points[i] = (new_x, new_y, size, color, alpha)
            
            # Center glow effect with improved pulsation
            radius = 180 + 50 * math.sin(self.time * 0.5)
            # Subtle color shifting over time
            r = 0.3 + 0.1 * math.sin(self.time * 0.2)
            g = 0.5 + 0.1 * math.sin(self.time * 0.3 + 1)
            b = 0.9
            
            # Main center glow
            Color(r, g, b, 0.15 + 0.05 * math.sin(self.time * 0.7))
            Ellipse(pos=(Window.width/2 - radius, Window.height/2 - radius), 
                   size=(radius*2, radius*2))
                   
            # Smaller, brighter core
            Color(r+0.1, g+0.2, b, 0.2 + 0.05 * math.sin(self.time * 0.5))
            inner_radius = radius * 0.6
            Ellipse(pos=(Window.width/2 - inner_radius, Window.height/2 - inner_radius), 
                   size=(inner_radius*2, inner_radius*2))
            
            # Mouse interaction effect (responsive glow that follows cursor)
            if self.mouse_time < 2.0:  # Fade out after 2 seconds
                mouse_alpha = 0.3 * max(0, 1 - self.mouse_time/2.0)
                mouse_radius = 100 + 20 * math.sin(self.time * 2)
                Color(0.5, 0.7, 1.0, mouse_alpha)
                Ellipse(pos=(self.mouse_x - mouse_radius/2, self.mouse_y - mouse_radius/2), 
                      size=(mouse_radius, mouse_radius))
            
            # Draw and update particles with more complex behavior
            for i, particle in enumerate(self.particles):
                # Update particle age and renewal
                particle.age += dt
                if particle.age > particle.lifetime:
                    # Reset particle at a random position
                    particle.x = random.uniform(0, Window.width)
                    particle.y = random.uniform(0, Window.height)
                    particle.age = 0
                    particle.lifetime = random.uniform(10, 20)
                    particle.direction = random.uniform(0, 360)
                    particle.dx = particle.speed * math.cos(math.radians(particle.direction))
                    particle.dy = particle.speed * math.sin(math.radians(particle.direction))
                
                # Update particle position with slight wave motion
                particle.dx += math.sin(self.time * 0.5 + i * 0.1) * 0.01
                particle.dy += math.cos(self.time * 0.4 + i * 0.1) * 0.01
                
                # Apply velocity
                particle.x += particle.dx
                particle.y += particle.dy
                
                # Boundary behavior: particles now wrap around screen edges
                if particle.x < -10:
                    particle.x = Window.width + 10
                elif particle.x > Window.width + 10:
                    particle.x = -10
                
                if particle.y < -10:
                    particle.y = Window.height + 10
                elif particle.y > Window.height + 10:
                    particle.y = -10
                
                # Calculate pulsating size
                size_factor = 0.5 + 0.5 * math.sin(self.time * 1.5 + particle.phase_offset)
                current_size = particle.min_size + (particle.max_size - particle.min_size) * size_factor
                
                # Pulsating alpha based on individual particle phase
                alpha = particle.alpha * (0.6 + 0.4 * math.sin(self.time * 0.8 + particle.phase_offset))
                
                # Draw particle
                Color(particle.color[0], particle.color[1], particle.color[2], alpha)
                Ellipse(pos=(particle.x - current_size/2, particle.y - current_size/2), 
                      size=(current_size, current_size))
                
                # Mouse proximity effect
                dist_to_mouse = ((particle.x - self.mouse_x)**2 + (particle.y - self.mouse_y)**2)**0.5
                if dist_to_mouse < 150 and self.mouse_time < 2.0:
                    # Particles close to mouse glow brighter and move away slightly
                    glow_factor = max(0, 1 - dist_to_mouse/150) * max(0, 1 - self.mouse_time/2.0)
                    
                    # Draw additional glow
                    Color(particle.color[0], particle.color[1], particle.color[2], glow_factor * 0.5)
                    glow_size = current_size * (1.5 + glow_factor)
                    Ellipse(pos=(particle.x - glow_size/2, particle.y - glow_size/2), 
                           size=(glow_size, glow_size))
                    
                    # Push particle away from mouse
                    angle = math.atan2(particle.y - self.mouse_y, particle.x - self.mouse_x)
                    particle.dx += math.cos(angle) * 0.1 * glow_factor
                    particle.dy += math.sin(angle) * 0.1 * glow_factor
                
                # Draw connecting lines between particles
                if i % 3 == 0:  # Only process every third particle for better performance
                    for j in range(i + 1, min(i + 10, len(self.particles))):
                        other = self.particles[j]
                        dist = ((particle.x - other.x)**2 + (particle.y - other.y)**2)**0.5
                        if dist < 150:
                            # Line transparency based on distance
                            line_alpha = 0.15 * (1 - dist/150)
                            
                            # Pulsating line effect
                            line_alpha *= 0.7 + 0.3 * math.sin(self.time * 0.5 + (i+j) * 0.05)
                            
                            # Harmonize colors between particles
                            r = (particle.color[0] + other.color[0]) * 0.5
                            g = (particle.color[1] + other.color[1]) * 0.5
                            b = (particle.color[2] + other.color[2]) * 0.5
                            
                            Color(r, g, b, line_alpha)
                            Line(points=[particle.x, particle.y, other.x, other.y], width=1)
                            
                            # Occasionally add a small node at the midpoint
                            if random.random() < 0.01:
                                mid_x = (particle.x + other.x) * 0.5
                                mid_y = (particle.y + other.y) * 0.5
                                mid_size = 2 + random.random() * 3
                                Color(r, g, b, line_alpha * 2)
                                Ellipse(pos=(mid_x - mid_size/2, mid_y - mid_size/2), 
                                       size=(mid_size, mid_size))

# ------------------------------
# 🔹 Speech Recognition and Synthesis Manager
# ------------------------------
class VoiceManager:
    def __init__(self):
        # Initialize speech recognizer
        self.recognizer = sr.Recognizer()
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.energy_threshold = 300  # Adjust sensitivity
        
        # Initialize text-to-speech engine
        self.engine = pyttsx3.init()
        voices = self.engine.getProperty('voices')
        # Set female voice if available
        for voice in voices:
            if 'female' in voice.name.lower():
                self.engine.setProperty('voice', voice.id)
                break
        
        # Set speech rate (default is 200)
        self.engine.setProperty('rate', 180)
        
        # Queue for speech output
        self.speech_queue = queue.Queue()
        
        # Thread for speech output
        self.speech_thread = threading.Thread(target=self._speech_worker, daemon=True)
        self.speech_thread.start()
        
        # Variables for recording and speech state
        self.is_listening = False
        self.listening_thread = None
        self.is_speaking = False
    
    def start_listening(self, callback):
        """Start listening for voice input"""
        with self.thread_lock:
            if self.is_listening:
                return
                
            self.is_listening = True
            self.listening_thread = threading.Thread(target=self._listen_worker, args=(callback,), daemon=True)
            self.listening_thread.start()
    
    def stop_listening(self):
        """Stop listening for voice input"""
        self.is_listening = False
        if self.listening_thread:
            self.listening_thread.join(timeout=1)
            self.listening_thread = None
    
    def _listen_worker(self, callback):
        """Background worker for voice recognition"""
        with sr.Microphone() as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            
            while self.is_listening:
                try:
                    print("Listening...")
                    audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
                    print("Processing speech...")
                    
                    # Perform speech recognition
                    text = self.recognizer.recognize_google(audio)
                    print(f"Recognized: {text}")
                    
                    # Call the callback with the recognized text
                    callback(text)
                    
                except sr.WaitTimeoutError:
                    print("Listening timed out, listening again...")
                except sr.UnknownValueError:
                    print("Could not understand audio")
                except sr.RequestError as e:
                    print(f"Could not request results: {e}")
                except Exception as e:
                    print(f"Error in speech recognition: {e}")
    
    def speak(self, text):
        """Queue text to be spoken"""
        self.speech_queue.put(text)
    
    def _speech_worker(self):
        """Background worker for text-to-speech"""
        while True:
            try:
                text = self.speech_queue.get()
                if text:
                    self.is_speaking = True
                    
                    # Split text into smaller chunks for more natural speech
                    chunks = self._split_text_into_chunks(text)
                    for chunk in chunks:
                        self.engine.say(chunk)
                        self.engine.runAndWait()
                        
                    self.is_speaking = False
                    
                self.speech_queue.task_done()
            except Exception as e:
                print(f"Error in speech synthesis: {e}")
                self.is_speaking = False
    
    def _split_text_into_chunks(self, text, max_length=200):
        """Split text into smaller chunks for more natural speech"""
        if len(text) <= max_length:
            return [text]
            
        chunks = []
        sentences = text.split('. ')
        current_chunk = ""
        
        for sentence in sentences:
            if len(current_chunk) + len(sentence) <= max_length:
                current_chunk += sentence + ". "
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + ". "
        
        if current_chunk:
            chunks.append(current_chunk.strip())
            
        return chunks

class ChatBubble(BoxLayout):
    def __init__(self, message="", bot=False, **kwargs):
        super().__init__(orientation="horizontal", size_hint=(None, None), padding=(dp(10), dp(5)), spacing=dp(5), **kwargs)
        self.bot = bot
        self.bubble_width = min(dp(300), Window.width * 0.75)  # Responsive width
        self.width = self.bubble_width
        self.height = dp(40)  # Initial height, will be adjusted later

        # Determine alignment and colors based on whether the message is from the bot or the user
        if bot:
            bg_color = (40/255, 80/255, 170/255, 0.7)  # Translucent blue for bot
            align = "left"
        else:
            bg_color = (80/255, 50/255, 160/255, 0.7)  # Translucent purple for user
            align = "right"

        with self.canvas.before:
            Color(*bg_color)
            self.bg_rect = RoundedRectangle(size=self.size, pos=self.pos, radius=[dp(20)])

        self.bind(
            size=self._update_rect,
            pos=self._update_rect
        )

        # Use BoxLayout as container for label to ensure proper alignment
        self.label_container = BoxLayout(orientation='vertical', size_hint=(1, None))
        
        # Create the message label with dynamic font size and proper text wrapping
        self.msg_label = Label(
            text=message,
            font_size=sp(16),
            size_hint=(1, None),
            color=TEXT_COLOR,
            halign=align,
            valign="middle",
            text_size=(self.bubble_width - dp(20), None),
            padding=(dp(10), dp(10)),
            markup=True,
            shorten=False,
            line_height=1.2
        )
        
        self.msg_label.bind(texture_size=self._adjust_label_size)
        self.label_container.add_widget(self.msg_label)
        self.label_container.bind(minimum_height=self.label_container.setter('height'))
        
        self.add_widget(self.label_container)
        
        # Bind to window size changes for responsiveness
        Window.bind(on_resize=self._on_window_resize)

    def _on_window_resize(self, instance, width, height):
        # Update bubble width when window size changes
        new_width = min(dp(300), width * 0.75)
        if self.bubble_width != new_width:
            self.bubble_width = new_width
            self.width = self.bubble_width
            self.msg_label.text_size = (self.bubble_width - dp(20), None)

    def _adjust_label_size(self, instance, texture_size):
        # Ensure label takes the full width of the container
        instance.height = texture_size[1]
        instance.width = self.bubble_width - dp(20)
        
        # Update container height to match content
        self.label_container.height = texture_size[1] + dp(10)
        
        # Update bubble height to contain the label
        self.height = self.label_container.height + dp(10)
        
        # Ensure text is properly aligned and wrapped
        instance.text_size = (self.bubble_width - dp(20), None)

    def _update_rect(self, *args):
        self.bg_rect.size = self.size
        self.bg_rect.pos = self.pos

# Add this new class for image message bubbles
class ImageChatBubble(BoxLayout):
    def __init__(self, image_url="", bot=True, **kwargs):
        super().__init__(orientation="vertical", size_hint=(None, None), padding=(dp(10), dp(5)), spacing=dp(5), **kwargs)
        self.bot = bot
        self.bubble_width = min(dp(300), Window.width * 0.75)
        self.width = self.bubble_width
        self.height = dp(300)  # Starting height for image

        # Background color for bot messages
        bg_color = (40/255, 80/255, 170/255, 0.7)  # Translucent blue for bot

        with self.canvas.before:
            Color(*bg_color)
            self.bg_rect = RoundedRectangle(size=self.size, pos=self.pos, radius=[dp(20)])

        self.bind(
            size=self._update_rect,
            pos=self._update_rect
        )

        # Create an AsyncImage to load the image
        self.image = AsyncImage(
            source=image_url,
            size_hint=(1, None),
            height=dp(250),
            allow_stretch=True,
            keep_ratio=True
        )
        
        # Add a caption label
        self.caption = Label(
            text="Generated Image",
            font_size=sp(14),
            size_hint=(1, None),
            height=dp(30),
            color=TEXT_COLOR,
            halign="center"
        )

        self.add_widget(self.image)
        self.add_widget(self.caption)
        
        # Bind to window size changes for responsiveness
        Window.bind(on_resize=self._on_window_resize)

    def _on_window_resize(self, instance, width, height):
        # Update bubble width when window size changes
        new_width = min(dp(300), width * 0.75)
        if self.bubble_width != new_width:
            self.bubble_width = new_width
            self.width = self.bubble_width

    def _update_rect(self, *args):
        self.bg_rect.size = self.size
        self.bg_rect.pos = self.pos

# ------------------------------
# 🔹 Voice Assistant UI
# ------------------------------
class VoiceAssistantUI(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Initialize voice manager
        self.voice_manager = VoiceManager()
        
        # Initial chat bubbles list to track for responsive updates
        self.chat_bubbles = []
        
        # Add animated background first (so it's behind everything)
        self.animated_bg = AnimatedBackground()
        self.add_widget(self.animated_bg)
        
        # Main layout to hold all the elements
        self.main_layout = BoxLayout(orientation="vertical", padding=dp(10), spacing=dp(10))
        
        # Header with responsive elements
        self.header = RelativeLayout(size_hint_y=None, height=dp(60))
        
        # Back button with custom image
        self.back_btn = ImageButton(
            source="back.png",  # Use your back button image
            pos_hint={"x": 0, "center_y": 0.5}
        )
        self.back_btn.bind(on_press=self.go_home)
        
        self.title = Label(
            text="GenVox Voice", 
            font_size=sp(24), 
            bold=True,
            pos_hint={"center_x": 0.5, "center_y": 0.5},
            color=TEXT_COLOR
        )
        
        # Profile button with custom image
        self.profile_btn = ImageButton(
            source="profile.png",  # Use your profile image
            pos_hint={"right": 1, "center_y": 0.5}
        )
        self.profile_btn.bind(on_press=self.go_to_profile)
        
        self.header.add_widget(self.back_btn)
        self.header.add_widget(self.title)
        self.header.add_widget(self.profile_btn)
        self.main_layout.add_widget(self.header)

        # Chat History with improved scrolling
        self.chat_scroll = ScrollView(
            size_hint=(1, 1), 
            do_scroll_y=True, 
            bar_width=dp(10),
            bar_color=[0.7, 0.7, 0.7, 0.9],
            bar_inactive_color=[0.5, 0.5, 0.5, 0.5],
            scroll_type=['bars', 'content']
        )
        
        self.chat_layout = GridLayout(
            cols=1, 
            size_hint_y=None, 
            spacing=dp(15), 
            padding=dp(15)
        )
        self.chat_layout.bind(minimum_height=self.chat_layout.setter('height'))
        self.chat_scroll.add_widget(self.chat_layout)
        self.main_layout.add_widget(self.chat_scroll)

        # Input Area with stylish rounded design and voice controls
        self.input_box = BoxLayout(size_hint_y=None, height=dp(70), spacing=dp(10))
        
        # Create a container for input to apply rounded corners
        self.input_container = BoxLayout(size_hint=(0.70, None), height=dp(50))
        with self.input_container.canvas.before:
            Color(0.2, 0.2, 0.3, 0.8)  # Semi-transparent dark background
            self.input_bg = RoundedRectangle(size=self.input_container.size, pos=self.input_container.pos, radius=[dp(25)])
        self.input_container.bind(pos=self._update_input_bg, size=self._update_input_bg)
        
        self.user_input = TextInput(
    hint_text="Type your message...",
    background_normal="",
    background_active="",
    background_color=(0, 0, 0, 0),  # Transparent background
    foreground_color=TEXT_COLOR,
    cursor_color=TEXT_COLOR,
    font_size=sp(16),
    padding=[dp(15), dp(10)],
    multiline=False,
    size_hint=(1, None),
    height=dp(50)
)
        self.input_container.add_widget(self.user_input)
        self.input_box.add_widget(self.input_container)

        # Voice input button with animation
        self.voice_btn = Button(
            text="",
            background_normal="",
            background_color=ACCENT_COLOR,
            size_hint=(None, None),
            size=(dp(50), dp(50)),
            border=(0, 0, 0, 0)
        )
        with self.voice_btn.canvas.before:
            Color(*get_color_from_hex("#ff6f61"))
            self.voice_btn_bg = Ellipse(size=self.voice_btn.size, pos=self.voice_btn.pos)
        self.voice_btn.bind(pos=self._update_voice_btn, size=self._update_voice_btn)
        self.voice_btn.bind(on_press=self.toggle_voice_input)

        # Add microphone icon to voice button
        self.voice_icon = Label(
            text="🎤",
            font_size=sp(24),
            color=TEXT_COLOR
        )
        self.voice_btn.add_widget(self.voice_icon)
        self.input_box.add_widget(self.voice_btn)

        # Send button with animation
        self.send_btn = Button(
            text="",
            background_normal="",
            background_color=PRIMARY_COLOR,
            size_hint=(None, None),
            size=(dp(50), dp(50)),
            border=(0, 0, 0, 0)
        )
        with self.send_btn.canvas.before:
            Color(*PRIMARY_COLOR)
            self.send_btn_bg = Ellipse(size=self.send_btn.size, pos=self.send_btn.pos)
        self.send_btn.bind(pos=self._update_send_btn, size=self._update_send_btn)
        self.send_btn.bind(on_press=self.send_message)

        # Add send icon to send button
        self.send_icon = Label(
            text="➤",
            font_size=sp(24),
            color=TEXT_COLOR
        )
        self.send_btn.add_widget(self.send_icon)
        self.input_box.add_widget(self.send_btn)

        self.main_layout.add_widget(self.input_box)
        self.add_widget(self.main_layout)

        # Add welcome message
        Clock.schedule_once(self.add_welcome_message, 0.5)

        # Bind keyboard events
        self.user_input.bind(on_text_validate=self.send_message)
        Window.bind(on_key_down=self._on_keyboard_down)

        # Initialize last user input time for auto-focusing
        self.last_input_time = time.time()
        Clock.schedule_interval(self.check_focus, 0.5)

        # Initialize voice processing status
        self.processing_voice = False

        # Queue for handling API requests
        self.request_queue = queue.Queue()
        self.processing_thread = threading.Thread(target=self._process_api_requests, daemon=True)
        self.processing_thread.start()

    def _update_input_bg(self, *args):
        self.input_bg.pos = self.input_container.pos
        self.input_bg.size = self.input_container.size

    def _update_voice_btn(self, *args):
        self.voice_btn_bg.pos = self.voice_btn.pos
        self.voice_btn_bg.size = self.voice_btn.size

    def _update_send_btn(self, *args):
        self.send_btn_bg.pos = self.send_btn.pos
        self.send_btn_bg.size = self.send_btn.size

    def check_focus(self, dt):
        # Auto-focus the text input after a period of inactivity
        current_time = time.time()
        if current_time - self.last_input_time > 10 and not self.user_input.focus:
            self.user_input.focus = True

    def _on_keyboard_down(self, instance, keyboard, keycode, text, modifiers):
        # Handle Enter key to send message
        if keycode == 40:  # 40 is Enter key
            self.send_message(None)
            return True
        return False

    def add_welcome_message(self, dt):
        welcome_message = "Hi there! I'm GenVox, your voice assistant. You can type or speak to me by pressing the microphone button. How can I help you today?"
        self.add_message(welcome_message, bot=True)
        # Speak the welcome message
        self.voice_manager.speak(welcome_message)

    def go_home(self, instance):
        # Handle back button action
        print("Going back to home screen")
        # Implementation would depend on your app's navigation structure

    def go_to_profile(self, instance):
        # Handle profile button action
        print("Going to profile screen")
        # Implementation would depend on your app's navigation structure

    def toggle_voice_input(self, instance):
        if not self.voice_manager.is_listening:
            # Visual feedback when starting to listen
            Animation(
                background_color=(1, 0.3, 0.3, 1),
                size=(dp(55), dp(55)),
                t='out_back',
                duration=0.2
            ).start(self.voice_btn)
            
            # Start voice recognition
            self.voice_manager.start_listening(self.on_voice_recognized)
            
            # Add a visual indicator that we're listening
            self.add_message("Listening...", bot=True)
        else:
            # Visual feedback when stopping
            Animation(
                background_color=ACCENT_COLOR,
                size=(dp(50), dp(50)),
                duration=0.2
            ).start(self.voice_btn)
            
            # Stop voice recognition
            self.voice_manager.stop_listening()

    def on_voice_recognized(self, text):
        if not text:
            return
            
        # Stop listening after receiving input
        self.voice_manager.stop_listening()
        
        # Reset button appearance
        Animation(
            background_color=ACCENT_COLOR,
            size=(dp(50), dp(50)),
            duration=0.2
        ).start(self.voice_btn)
        
        # Display the recognized text
        self.add_message(text, bot=False)
        
        # Process the message
        self.process_user_input(text)

    def send_message(self, instance):
        text = self.user_input.text.strip()
        if not text:
            return
            
        # Add user message to chat
        self.add_message(text, bot=False)
        
        # Clear input
        self.user_input.text = ""
        
        # Process the message
        self.process_user_input(text)
        
        # Update last input time
        self.last_input_time = time.time()

    def process_user_input(self, text):
        # Show typing indicator
        typing_bubble = self.add_message("Thinking...", bot=True)
        
        # Queue the API request
        self.request_queue.put((text, typing_bubble))

    def _process_api_requests(self):
        """Worker thread to process API requests"""
        while True:
            try:
                user_text, typing_bubble = self.request_queue.get()
                
                try:
                    # Make API call to Together API
                    response = client.chat.completions.create(
                        model="mistralai/Mistral-7B-Instruct-v0.1",
                        messages=[
                            {"role": "system", "content": "You are GenVox, a helpful, concise, and friendly voice assistant. Provide clear and direct answers."},
                            {"role": "user", "content": user_text}
                        ],
                        temperature=0.7,
                        max_tokens=500
                    )
                    
                    # Get assistant's response
                    assistant_response = response.choices[0].message.content
                    
                    # Remove the typing indicator
                    Clock.schedule_once(lambda dt: self.remove_typing_indicator(typing_bubble, assistant_response), 0)
                    
                except Exception as e:
                    error_message = f"Sorry, I encountered an error: {str(e)}"
                    Clock.schedule_once(lambda dt: self.remove_typing_indicator(typing_bubble, error_message), 0)
                
                self.request_queue.task_done()
                
            except Exception as e:
                print(f"Error in API processing thread: {e}")

    def remove_typing_indicator(self, typing_bubble, new_message):
        # Remove typing indicator
        self.chat_layout.remove_widget(typing_bubble)
        self.chat_bubbles.remove(typing_bubble)
        
        # Add the actual response
        self.add_message(new_message, bot=True)
        
        # Speak the response
        self.voice_manager.speak(new_message)

    def add_message(self, message, bot=True):
        # Create a chat bubble for the message
        bubble = ChatBubble(message=message, bot=bot)
        
        # Add the bubble to the chat layout
        self.chat_layout.add_widget(bubble)
        self.chat_bubbles.append(bubble)
        
        # Scroll to the bottom to show the latest message
        Clock.schedule_once(self._scroll_to_bottom, 0.1)
        
        return bubble

    def add_image_message(self, image_url):
        # Create an image chat bubble
        bubble = ImageChatBubble(image_url=image_url)
        
        # Add the bubble to the chat layout
        self.chat_layout.add_widget(bubble)
        self.chat_bubbles.append(bubble)
        
        # Scroll to the bottom
        Clock.schedule_once(self._scroll_to_bottom, 0.1)
        
        return bubble

    def _scroll_to_bottom(self, dt):
        self.chat_scroll.scroll_y = 0

    # ------------------------------
    # 🔹 Main App Class
    # ------------------------------
class VoiceAssistantApp(App):
    def build(self):
        self.title = 'GenVox Voice Assistant'
        # Set window size - adjust for your testing
        Window.size = (400, 700)
        return VoiceAssistantUI()

if __name__ == '__main__':
    VoiceAssistantApp().run()