import kivy
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.image import Image
from kivy.graphics import Color, Rectangle, RoundedRectangle, Ellipse, Line
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.properties import NumericProperty, BooleanProperty
from kivy.core.window import Window
from functools import partial
from imagegenereation import ImageGeneratorScreen
import random
import math

# Define the minimum Kivy version required
kivy.require('2.0.0')

# ------------------------------
# 🔹 Animated Background - Same as home.py
# ------------------------------
class Particle:
    def __init__(self, x, y, size):
        self.x = x
        self.y = y
        self.size = size
        self.speed = random.uniform(0.5, 2)
        self.alpha = random.uniform(0.1, 0.5)
        self.direction = random.uniform(0, 360)
        self.dx = self.speed * math.cos(math.radians(self.direction))
        self.dy = self.speed * math.sin(math.radians(self.direction))
        # Unique colors with purple/blue theme
        self.color = random.choice([
            (0.9, 0.95, 1),  # White-blue
            (0.7, 0.8, 1),   # Light blue
            (0.6, 0.7, 0.9), # Blue
            (0.7, 0.6, 0.9)  # Purple-blue
        ])

class AnimatedBackground(FloatLayout):
    particles = []
    time = NumericProperty(0)
    
    def __init__(self, **kwargs):
        super(AnimatedBackground, self).__init__(**kwargs)
        self.create_particles()
        Clock.schedule_interval(self.update, 1/60)
        
    def create_particles(self):
        self.particles = []
        for _ in range(60):  # Number of particles
            x = random.uniform(0, Window.width)
            y = random.uniform(0, Window.height)
            size = random.uniform(2, 6)
            self.particles.append(Particle(x, y, size))
            
    def update(self, dt):
        self.time += dt
        self.canvas.clear()
        with self.canvas:
            # Create a subtle glow effect in center - no rectangle overlay
            radius = 180 + 40 * math.sin(self.time * 0.5)
            Color(0.3, 0.5, 0.9, 0.2)  # Lighter blue glow
            Ellipse(pos=(Window.width/2 - radius, Window.height/2 - radius), 
                   size=(radius*2, radius*2))
            
            for particle in self.particles:
                # Update particle position
                particle.x += particle.dx
                particle.y += particle.dy
                
                # Keep particles within the screen bounds
                if particle.x < 0 or particle.x > Window.width:
                    particle.dx *= -1
                if particle.y < 0 or particle.y > Window.height:
                    particle.dy *= -1
                
                # Draw particle with pulsating effect
                alpha = particle.alpha * (0.5 + 0.5 * math.sin(self.time + particle.x * 0.01))
                Color(particle.color[0], particle.color[1], particle.color[2], alpha)
                Ellipse(pos=(particle.x - particle.size/2, particle.y - particle.size/2), 
                       size=(particle.size, particle.size))
                
                # Connecting lines between particles
                if random.random() < 0.02:
                    other = random.choice(self.particles)
                    dist = ((particle.x - other.x)**2 + (particle.y - other.y)**2)**0.5
                    if dist < 120:
                        Color(particle.color[0], particle.color[1], particle.color[2], 0.1 * (1 - dist/120))
                        Line(points=[particle.x, particle.y, other.x, other.y], width=1)

# ------------------------------
# 🔹 Enhanced Rounded Button (For Back & Profile)
# ------------------------------
class RoundedButton(Button):
    def __init__(self, **kwargs):
        super(RoundedButton, self).__init__(**kwargs)
        self.size_hint = (None, None)
        self.size = (50, 50)  # Circular button
        self.background_normal = ''
        self.background_color = (0, 0, 0, 0)  # Transparent background
        self.color = (1, 1, 1, 1)  # White text
        self.bold = True
        # Track button state
        self.pressed = False
        self.bind(pos=self.update_canvas, size=self.update_canvas)
                
    def update_canvas(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            # Light blue button
            Color(100/255, 180/255, 240/255, 1)
            Ellipse(pos=self.pos, size=self.size)
            Color(120/255, 200/255, 255/255, 0.8)
            Ellipse(pos=(self.pos[0] + 5, self.pos[1] + 5),
                size=(self.size[0] * 0.8, self.size[1] * 0.8))
            # Add subtle shine effect
            Color(1, 1, 1, 0.2)
            Rectangle(pos=(self.pos[0] + self.size[0] * 0.25, self.pos[1] + self.size[1] * 0.7),
                   size=(self.size[0] * 0.5, self.size[1] * 0.3))

# ------------------------------
# 🔹 Enhanced Clickable Model Box
# ------------------------------
class ModelBox(BoxLayout):
    def __init__(self, name, description, on_select_callback, **kwargs):
        super(ModelBox, self).__init__(**kwargs)
        self.orientation = 'vertical'
        self.size_hint_y = None
        self.height = 140
        self.padding = 10
        self.spacing = 5
        self.name = name
        self.description = description
        self.callback = on_select_callback
        # Track button state
        self.clicked = False

        # Background with a rounded design matching the theme
        with self.canvas.before:
            # Dark blue background - matches dark blue layout in home.py
            Color(8/255, 20/255, 45/255, 0.9)
            self.rect = RoundedRectangle(size=self.size, pos=self.pos, radius=[15])
            # Light blue border
            Color(50/255, 130/255, 240/255, 0.7)
            self.border = Line(rounded_rectangle=[self.pos[0], self.pos[1], self.size[0], self.size[1], 15], width=1.5)

        self.bind(size=self.update_rect, pos=self.update_rect)

        # Model box content
        content_layout = GridLayout(cols=1, spacing=5)
        
        # Model Name
        self.name_label = Label(
            text=name, 
            font_size=22, 
            bold=True, 
            color=(1, 1, 1, 1),
            size_hint_y=None,
            height=50,
            halign='left',
            valign='middle'
        )
        self.name_label.bind(size=self.name_label.setter('text_size'))
        content_layout.add_widget(self.name_label)
        
        # Model Description
        self.desc_label = Label(
            text=description, 
            font_size=14, 
            color=(0.9, 0.9, 1, 0.8),
            size_hint_y=None,
            height=60,
            halign='left',
            valign='top'
        )
        self.desc_label.bind(size=self.desc_label.setter('text_size'))
        content_layout.add_widget(self.desc_label)
        
        self.add_widget(content_layout)
        
        # Create a transparent button to handle clicks
        self.button = Button(
            background_color=(0, 0, 0, 0),
            size_hint=(1, 1),
            pos_hint={'center_x': 0.5, 'center_y': 0.5}
        )
        self.button.bind(on_press=self._on_press, on_release=self._on_release)
        self.add_widget(self.button)

    def _on_press(self, instance):
        # Visual feedback on press
        self.clicked = True
        with self.canvas.before:
            Color(70/255, 150/255, 255/255, 0.8)
            self.highlight = RoundedRectangle(size=self.size, pos=self.pos, radius=[15])

    def _on_release(self, instance):
        # Remove highlight and call callback if still clicked
        if self.clicked:
            self.canvas.before.remove(self.highlight)
            self.clicked = False
            Clock.schedule_once(lambda dt: self.callback(self.name), 0.01)

    def update_rect(self, *args):
        self.rect.size = self.size
        self.rect.pos = self.pos
        self.border.rounded_rectangle = [self.pos[0], self.pos[1], self.size[0], self.size[1], 15]

# ------------------------------
# 🔹 Enhanced Menu Screen Layout
# ------------------------------
class MenuScreen(Screen):
    def __init__(self, **kwargs):
        super(MenuScreen, self).__init__(**kwargs)
        self.layout = FloatLayout()
        # Button cooldown timer
        self.last_click_time = 0
        self.click_cooldown = 0.5  # seconds

        # Set background color
        with self.canvas.before:
            Color(30/255, 40/255, 80/255, 1)  # Dark blue background
            self.bg = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.update_rect, size=self.update_rect)
        
        # Add animated background
        self.animated_bg = AnimatedBackground()
        self.layout.add_widget(self.animated_bg)

        # Top Bar Layout - removed the title
        top_bar = BoxLayout(
            orientation='horizontal',
            size_hint=(1, None),
            height=80,
            pos_hint={'top': 1}
        )
        
        # Left container for back button
        left_container = BoxLayout(
            size_hint=(0.2, 1),
            padding=[10, 15, 0, 0]
        )
        
        # Back Button
        back_button = RoundedButton(
            text="<",
            font_size=24
        )
        back_button.bind(on_press=self.handle_back_press)
        back_button.pos_hint = {'center_y': 0.5, 'left': 0}
        left_container.add_widget(back_button)
        top_bar.add_widget(left_container)
        
        # Center container - no title, just empty space
        center_container = BoxLayout(
            size_hint=(0.6, 1)
        )
        top_bar.add_widget(center_container)
        
        # Right container for layout balance
        right_container = BoxLayout(
            size_hint=(0.2, 1)
        )
        top_bar.add_widget(right_container)
        
        self.layout.add_widget(top_bar)
        
        # Profile Button - positioned at extreme right
        profile_button = RoundedButton(
            text="U",
            font_size=20
        )
        profile_button.bind(on_press=self.handle_profile_press)
        profile_button.pos = (Window.width - 60, Window.height - 65)
        self.layout.add_widget(profile_button)

        # ------------------------------
        # 🔹 Scrollable AI Models Section
        # ------------------------------
        self.scroll_view = ScrollView(
            pos_hint={"center_x": 0.5, "center_y": 0.45}, 
            size_hint=(0.9, 0.7),
            bar_color=(100/255, 180/255, 240/255, 0.7),
            bar_width=4,
            scroll_type=['bars', 'content']
        )
        
        self.models_layout = GridLayout(cols=1, size_hint_y=None, spacing=15, padding=15)
        self.models_layout.bind(minimum_height=self.models_layout.setter('height'))

        models = [
            {"name": "Image Generation", "description": "Generate AI-powered images"},
            {"name": "Code Generation", "description": "Create AI-generated code"},
            {"name": "Text Generation", "description": "Chat with AI"},
            {"name": "Audio Generation", "description": "Generate AI-based audio"},
            {"name": "Poetry Generation", "description": "Generate AI-based poem"},
            {"name": "Problem Solver", "description": "Generate AI-based solver"},
            {"name": "Story Generation", "description": "Generate AI-based Story"},
            {"name": "Language Translator", "description": "Generate AI-based translator"},
            {"name": "Text To Speech", "description": "Generate AI-based Text to Audio"},
            {"name": "Text Summarization", "description": "Generate AI-based summarize the given text"}
        ]

        for model in models:
            model_box = ModelBox(
                name=model["name"],
                description=model["description"],
                on_select_callback=self.handle_model_select
            )
            self.models_layout.add_widget(model_box)

        self.scroll_view.add_widget(self.models_layout)
        self.layout.add_widget(self.scroll_view)
        self.add_widget(self.layout)
        
        # Bind window resize to update profile button position
        Window.bind(on_resize=self.on_window_resize)

    def on_window_resize(self, instance, width, height):
        """Update profile button position when window is resized"""
        for child in self.layout.children:
            if isinstance(child, RoundedButton) and child.text == "U":
                child.pos = (width - 60, height - 65)

    def update_rect(self, *args):
        """Update background size when window resizes."""
        self.bg.pos = self.pos
        self.bg.size = self.size

    def handle_back_press(self, instance):
        current_time = Clock.get_time()
        if current_time - self.last_click_time > self.click_cooldown:
            self.last_click_time = current_time
            # Use schedule_once to improve responsiveness
            Clock.schedule_once(lambda dt: self.go_home(), 0.01)

    def handle_profile_press(self, instance):
        current_time = Clock.get_time()
        if current_time - self.last_click_time > self.click_cooldown:
            self.last_click_time = current_time
            # Use schedule_once to improve responsiveness
            Clock.schedule_once(lambda dt: self.go_to_profile(), 0.01)

    def handle_model_select(self, model_name):
        current_time = Clock.get_time()
        if current_time - self.last_click_time > self.click_cooldown:
            self.last_click_time = current_time
            # Use schedule_once to improve responsiveness
            Clock.schedule_once(lambda dt: self.transition_to_screen(model_name), 0.01)

    def go_home(self):
        App.get_running_app().root.current = "main"
        App.get_running_app().root.transition.direction = "right"

    def go_to_profile(self):
        App.get_running_app().root.current = "profile"
        App.get_running_app().root.transition.direction = "left"
    
    def transition_to_screen(self, model_name):
        # Dictionary to map model names to screen names
        screen_mappings = {
            "Image Generation": "image",
            "Code Generation": "code",
            "Text Generation": "textbot",
            "Audio Generation": "audio",
            "Poetry Generation": "poem",
            "Problem Solver": "solve",
            "Story Generation": "story",
            "Language Translator": "trans",
            "Text To Speech": "speech",
            "Text Summarization": "summarize"
        }
        
        # Get the screen name, default to "menu" if not found
        screen_name = screen_mappings.get(model_name, "menu")
        
        try:
            app = App.get_running_app()
            # Check if screen exists in screen manager
            screen_names = [screen.name for screen in app.root.screens]
            
            if screen_name in screen_names:
                app.root.current = screen_name
                app.root.transition.direction = "left"
            else:
                print(f"Screen '{screen_name}' not found in {screen_names}")
        except Exception as e:
            print(f"Error transitioning to screen: {e}")

# ------------------------------
# 🔹 App Manager
# ------------------------------
class GenAIApp(App):
    def build(self):
        sm = ScreenManager()
        
        # Add all screens here
        sm.add_widget(MenuScreen(name="menu"))
        sm.add_widget(ImageGeneratorScreen(name="image"))
        
        # Create placeholder screens using a better method
        for screen_name in ["code", "textbot", "audio", "poem", "solve", "story", "trans", "speech", "summarize"]:
            placeholder = Screen(name=screen_name)
            with placeholder.canvas:
                Color(0.2, 0.3, 0.5, 1)
                Rectangle(pos=(0, 0), size=Window.size)
            
            # Add a title and back button to each placeholder
            layout = FloatLayout()
            
            # Title
            title = Label(
                text=f"{screen_name.capitalize()} Generation",
                font_size=30,
                bold=True,
                pos_hint={'center_x': 0.5, 'top': 0.95}
            )
            layout.add_widget(title)
            
            # Back button - using partial for proper callback
            back_btn = Button(
                text="Back to Menu",
                size_hint=(0.5, 0.1),
                pos_hint={'center_x': 0.5, 'center_y': 0.5},
                background_color=(0.1, 0.4, 0.8, 1)
            )
            back_btn.bind(on_press=partial(self.go_back_to_menu))
            layout.add_widget(back_btn)
            
            placeholder.add_widget(layout)
            sm.add_widget(placeholder)
        
        return sm
    
    def go_back_to_menu(self, instance):
        self.root.current = "menu"
        self.root.transition.direction = "right"

# ------------------------------
# 🔹 Run the App
# ------------------------------
if __name__ == '__main__':
    Window.size = (400, 700)
    GenAIApp().run()