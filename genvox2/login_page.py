import kivy
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.graphics import Color, Rectangle, Ellipse, RoundedRectangle, Line
from kivy.core.window import Window
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.properties import NumericProperty, BooleanProperty, ObjectProperty
from database import authenticate_user, get_user, update_user
import random
import math

# Define the minimum Kivy version required
kivy.require('2.0.0')

# ------------------------------
# 🔹 Custom Image Button (for back button)
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
# 🔹 Animated Background
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
# 🔹 Curved Edge Buttons with hover effects
# ------------------------------
class CurvedButton(Button):
    hover = BooleanProperty(False)
    ripple_alpha = NumericProperty(0)
    ripple_size = NumericProperty(0)
    
    def __init__(self, **kwargs):
        super(CurvedButton, self).__init__(**kwargs)
        self.size_hint = (None, None)
        self.size = (220, 60)
        self.background_normal = ''
        self.background_color = (0, 0, 0, 0)  # Transparent background
        self.color = (15/255, 30/255, 100/255, 1)  # Dark blue text
        self.bold = True
        self.bind(pos=self.update_canvas, size=self.update_canvas)
        
    def update_canvas(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            # Light blue color for the buttons
            Color(100/255, 180/255, 240/255, 1 if not self.hover else 120/255, 190/255, 250/255, 1)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[30, 30, 30, 30])
    
    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            anim = Animation(size=(220, 55), duration=0.1)
            anim.start(self)
            
            # Add ripple effect
            self.ripple_size = 0
            self.ripple_alpha = 0.3
            anim_ripple = Animation(ripple_size=self.width*2, ripple_alpha=0, duration=0.6)
            anim_ripple.start(self)
            
        return super(CurvedButton, self).on_touch_down(touch)
    
    def on_touch_up(self, touch):
        if self.collide_point(*touch.pos):
            anim = Animation(size=(220, 60), duration=0.2, t='out_back')
            anim.start(self)
        return super(CurvedButton, self).on_touch_up(touch)
    
    def on_mouse_pos(self, *args):
        if not self.get_root_window():
            return
        pos = args[1]
        if self.collide_point(*self.to_widget(*pos)):
            if not self.hover:
                self.hover = True
                anim = Animation(font_size=19, duration=0.1)
                anim.start(self)
                self.update_canvas()
        else:
            if self.hover:
                self.hover = False
                anim = Animation(font_size=18, duration=0.1)
                anim.start(self)
                self.update_canvas()

class DarkBlueLayout(BoxLayout):
    def __init__(self, **kwargs):
        super(DarkBlueLayout, self).__init__(**kwargs)
        self.bind(pos=self.update_canvas, size=self.update_canvas)
        Clock.schedule_once(self.update_canvas, 0)
        
    def update_canvas(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(8/255, 20/255, 45/255, 0.9)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[20, 20, 20, 20])
            # Light blue border
            Color(50/255, 130/255, 240/255, 0.7)
            Line(rounded_rectangle=[self.pos[0], self.pos[1], self.size[0], self.size[1], 20], width=1.5)

# ------------------------------
# 🔹 Login Screen Layout
# ------------------------------
class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Base layout
        layout = FloatLayout()
        
        # Set background color
        with self.canvas.before:
            Color(30/255, 40/255, 80/255, 1)  # Dark blue background
            self.bg = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.update_rect, size=self.update_rect)
        
        # Add animated background
        animated_bg = AnimatedBackground()
        layout.add_widget(animated_bg)

        # Back Button (Top Left) with image
        back_button = ImageButton(
            source="back.png",  # Use back icon image
            pos_hint={"x": 0.02, "top": 0.98}  # Top-left corner
        )
        back_button.bind(on_press=self.go_back)
        layout.add_widget(back_button)

        # Title Label (Top Center)
        title_label = Label(
            text="GenVox",
            font_size=40,
            bold=True,
            size_hint_y=None,
            height=100,
            color=(1, 1, 1, 1),
            pos_hint={"center_x": 0.5, "top": 0.94}
        )
        layout.add_widget(title_label)

        # Message Label to Display Errors
        self.message_label = Label(
            text="",
            font_size=18,
            color=(1, 0, 0, 1),  # Red color for errors
            pos_hint={"center_x": 0.5, "y": 0.1}
        )
        layout.add_widget(self.message_label)

        # Form Container with dark blue styling
        form_container = DarkBlueLayout(
            orientation="vertical",
            padding=20,
            spacing=15,
            size_hint=(None, None),
            size=(350, 400),
            pos_hint={"center_x": 0.5, "center_y": 0.5}
        )

        # LOGIN Label
        login_label = Label(
            text="LOGIN",
            font_size=24,
            bold=True,
            size_hint_y=None,
            height=60,
            color=(1, 1, 1, 1)  # White text on dark background
        )
        form_container.add_widget(login_label)

        # Form Fields (Email, Password)
        form_layout = GridLayout(cols=1, spacing=10, size_hint_y=None, height=120)
        self.email_input = TextInput(
            hint_text='Enter your email', 
            size_hint_y=None, 
            height=40,
            background_color=(1, 1, 1, 0.8),  # Slightly transparent white
            foreground_color=(15/255, 30/255, 100/255, 1)  # Dark blue text
        )
        self.password_input = TextInput(
            hint_text='Enter your password', 
            password=True, 
            size_hint_y=None, 
            height=40,
            background_color=(1, 1, 1, 0.8),
            foreground_color=(15/255, 30/255, 100/255, 1)
        )

        form_layout.add_widget(self.email_input)
        form_layout.add_widget(self.password_input)
        form_container.add_widget(form_layout)

        # Submit Button with light blue style
        submit_button = CurvedButton(
            text='SUBMIT',
            font_size=18,
            size_hint=(None, None),
            pos_hint={"center_x": 0.5}
        )
        submit_button.bind(pos=submit_button.update_canvas)
        submit_button.bind(on_press=self.submit)
        form_container.add_widget(submit_button)

        # Create Account Link
        create_account_label = Label(
            text="Don't have an account? [ref=create]Create[/ref]",
            markup=True,  # Enables clickable text
            font_size=16,
            color=(1, 1, 1, 1),  # White text
            size_hint_y=None,
            height=40
        )
        create_account_label.bind(on_ref_press=self.go_to_create)
        form_container.add_widget(create_account_label)

        layout.add_widget(form_container)
        self.add_widget(layout)
        
        # Apply entry animations
        Clock.schedule_once(self.apply_entrance_animations, 0.1)
        
        # Bind mouse position to button hover events
        Window.bind(mouse_pos=self.on_mouse_pos)

    def apply_entrance_animations(self, dt):
        # Animate form container to fade in with a slight bounce
        for child in self.children:
            if isinstance(child, FloatLayout):
                for widget in child.children:
                    if isinstance(widget, DarkBlueLayout):
                        widget.opacity = 0  # Start invisible
                        anim = Animation(opacity=1, duration=0.8, t='out_back')
                        anim.start(widget)

    def on_mouse_pos(self, window, pos):
        # Update button hover states for all buttons in the layout
        for widget in self.walk():
            if isinstance(widget, (CurvedButton, ImageButton)) and hasattr(widget, 'on_mouse_pos'):
                widget.on_mouse_pos(window, pos)

    def update_rect(self, *args):
        """Update background size when window resizes."""
        self.bg.pos = self.pos
        self.bg.size = self.size

    def submit(self, instance):
        """Check credentials before login"""
        email = self.email_input.text.strip()
        password = self.password_input.text.strip()

        if not email or not password:
            self.display_message("Please enter email and password!")
            return

        if authenticate_user(email, password):
            self.display_message("Login Successful!")
            # Add a subtle fade-out animation before changing screens
            fade_out = Animation(opacity=0, duration=0.3)
            fade_out.bind(on_complete=lambda *args: self.go_to_home_transition())
            fade_out.start(self)
        else:
            self.display_message("Invalid email or password! User does not exist.")

    def go_to_home_transition(self):
        self.manager.current = "home"  # Navigate to home only if login is successful
        App.get_running_app().user_email = self.email_input.text.strip()
        self.opacity = 1  # Reset opacity for next time

    def display_message(self, message):
        """Show message on screen with animation"""
        self.message_label.opacity = 0
        self.message_label.text = message
        anim = Animation(opacity=1, duration=0.3)
        anim.start(self.message_label)

    def go_to_create(self, instance, value):
        """Navigates to SignIn Page when 'Create' is clicked"""
        fade_out = Animation(opacity=0, duration=0.3)
        fade_out.bind(on_complete=lambda *args: self.go_to_create_transition())
        fade_out.start(self)
        
    def go_to_create_transition(self):
        self.manager.current = "signin"
        self.opacity = 1  # Reset opacity for next time

    def go_back(self, instance):
        """Navigates to Index Page when back button is pressed"""
        fade_out = Animation(opacity=0, duration=0.3)
        fade_out.bind(on_complete=lambda *args: self.go_to_index_transition())
        fade_out.start(self)
        
    def go_to_index_transition(self):
        self.manager.current = "index"
        self.opacity = 1  # Reset opacity for next time

# ------------------------------
# 🔹 Main App with ScreenManager
# ------------------------------
class MyApp(App):
    def build(self):
        from signin_page import SignInScreen
        sm = ScreenManager()
        sm.add_widget(LoginScreen(name="login"))
        sm.add_widget(SignInScreen(name="signin"))
        return sm

if __name__ == "__main__":
    MyApp().run()