from kivy.uix.screenmanager import Screen
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle, RoundedRectangle, Line, Ellipse
from kivy.core.window import Window
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.properties import NumericProperty, BooleanProperty, ObjectProperty
from pymongo import MongoClient
import random
import math

# MongoDB Connection
MONGO_URI = "mongodb://localhost:27017/"
client = MongoClient(MONGO_URI)
db = client["genvox"]
admins_collection = db["genvox"]  # Keep all admin/users in same collection

# Reuse Particle and AnimatedBackground from login_page.py
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
        self.color = random.choice([
            (0.9, 0.95, 1),    # White-blue
            (0.7, 0.8, 1),     # Light blue
            (0.6, 0.7, 0.9),   # Blue
            (0.7, 0.6, 0.9),   # Purple-blue
            (0.5, 0.7, 1),     # Sky blue
            (0.8, 0.6, 1),     # Lavender
            (0.6, 0.9, 1)      # Cyan-blue
        ])
        self.phase_offset = random.uniform(0, 2 * math.pi)
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
        Window.bind(mouse_pos=self.on_mouse_pos)
        
    def on_mouse_pos(self, window, pos):
        self.mouse_x = pos[0]
        self.mouse_y = pos[1]
        self.mouse_time = 0
    
    def create_particles(self):
        self.particles = []
        for _ in range(80):
            x = random.uniform(0, Window.width)
            y = random.uniform(0, Window.height)
            size = random.uniform(2, 7)
            self.particles.append(Particle(x, y, size))
    
    def create_glow_points(self):
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


class CurvedButton(Button):
    hover = BooleanProperty(False)
    
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
            Color(100/255, 180/255, 240/255, 1 if not self.hover else 120/255, 190/255, 250/255, 1)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[30, 30, 30, 30])
    
    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            anim = Animation(size=(220, 55), duration=0.1)
            anim.start(self)
        return super(CurvedButton, self).on_touch_down(touch)
    
    def on_touch_up(self, touch):
        if self.collide_point(*touch.pos):
            anim = Animation(size=(220, 60), duration=0.2, t='out_back')
            anim.start(self)
        return super(CurvedButton, self).on_touch_up(touch)

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
            Color(50/255, 130/255, 240/255, 0.7)
            Line(rounded_rectangle=[self.pos[0], self.pos[1], self.size[0], self.size[1], 20], width=1.5)

class AdminLoginScreen(Screen):
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

        # Form Container with dark blue styling
        form_container = DarkBlueLayout(
            orientation="vertical",
            padding=20,
            spacing=15,
            size_hint=(None, None),
            size=(350, 450),
            pos_hint={"center_x": 0.5, "center_y": 0.5}
        )

        # Admin Login Label
        login_label = Label(
            text="ADMIN LOGIN", 
            font_size=24, 
            bold=True, 
            size_hint_y=None, 
            height=60, 
            color=(1, 1, 1, 1)  # White text
        )
        form_container.add_widget(login_label)

        # Form Fields
        self.email_input = TextInput(
            hint_text='Admin Email', 
            size_hint_y=None, 
            height=40,
            background_color=(1, 1, 1, 0.8),
            foreground_color=(15/255, 30/255, 100/255, 1)
        )
        self.password_input = TextInput(
            hint_text='Password', 
            password=True, 
            size_hint_y=None, 
            height=40,
            background_color=(1, 1, 1, 0.8),
            foreground_color=(15/255, 30/255, 100/255, 1)
        )
        self.token_input = TextInput(
            hint_text='Admin Token', 
            size_hint_y=None, 
            height=40,
            background_color=(1, 1, 1, 0.8),
            foreground_color=(15/255, 30/255, 100/255, 1)
        )

        # Feedback Label
        self.feedback_label = Label(
            text="", 
            font_size=16, 
            color=(1, 0, 0, 1),  # Red color for errors
            size_hint_y=None, 
            height=40
        )

        # Login Button
        login_button = CurvedButton(
            text='ADMIN LOGIN', 
            font_size=18, 
            size_hint=(None, None), 
            pos_hint={"center_x": 0.5}
        )
        login_button.bind(on_press=self.verify_admin)

        # Back Button
        back_button = CurvedButton(
            text='BACK TO INDEX', 
            font_size=18, 
            size_hint=(None, None), 
            pos_hint={"center_x": 0.5}
        )
        back_button.bind(on_press=self.go_back)

        # Add widgets to form container
        form_container.add_widget(self.email_input)
        form_container.add_widget(self.password_input)
        form_container.add_widget(self.token_input)
        form_container.add_widget(login_button)
        form_container.add_widget(back_button)
        form_container.add_widget(self.feedback_label)

        layout.add_widget(form_container)
        self.add_widget(layout)

        # Apply entry animations
        Clock.schedule_once(self.apply_entrance_animations, 0.1)
        Window.bind(mouse_pos=self.on_mouse_pos)

    def apply_entrance_animations(self, dt):
        for child in self.children:
            if isinstance(child, FloatLayout):
                for widget in child.children:
                    if isinstance(widget, DarkBlueLayout):
                        widget.opacity = 0
                        anim = Animation(opacity=1, duration=0.8, t='out_back')
                        anim.start(widget)

    def on_mouse_pos(self, window, pos):
        for widget in self.walk():
            if isinstance(widget, (CurvedButton,)) and hasattr(widget, 'on_mouse_pos'):
                if not widget.hover and widget.collide_point(*widget.to_widget(*pos)):
                    widget.hover = True
                    widget.update_canvas()
                elif widget.hover and not widget.collide_point(*widget.to_widget(*pos)):
                    widget.hover = False
                    widget.update_canvas()

    def update_rect(self, *args):
        """Update background size when window resizes."""
        self.bg.pos = self.pos
        self.bg.size = self.size

    def verify_admin(self, instance):
        email = self.email_input.text.strip()
        password = self.password_input.text.strip()
        token = self.token_input.text.strip()

        # Check admin credentials
        admin = admins_collection.find_one({
            "email": email,
            "password": password,
            "role": "admin",  # ensure role = admin
            "token": token
        })

        if admin:
            self.feedback_label.text = "✅ Admin Login Successful!"
            self.manager.current = "admin_dashboard"  # Navigate to admin dashboard
        else:
            self.feedback_label.text = "❌ Invalid Admin Credentials!"

    def go_back(self, instance):
        self.manager.current = "index"  # Navigate to index page