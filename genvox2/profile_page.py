import kivy
from kivy.app import App
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.image import Image
from kivy.graphics import Color, Rectangle, Ellipse, RoundedRectangle, Line
from kivy.animation import Animation
from kivy.properties import NumericProperty, BooleanProperty, ObjectProperty
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.lang import Builder
from pymongo import MongoClient

# Update KV styling for buttons
kv_string = '''
#:kivy 2.0.0

<CurvedButton>:
    size_hint: None, None
    size: 220, 60
    background_color: 0, 0, 0, 0  # Transparent background
    color: 15/255, 30/255, 100/255, 1  # Dark blue text
    bold: True
    hover: False
    canvas.before:
        # Light white color for the buttons
        Color:
            rgba: 1, 1, 1, 1
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [30, 30, 30, 30]
'''
Builder.load_string(kv_string)

# MongoDB Connection
MONGO_URI = "mongodb://localhost:27017/"
client = MongoClient(MONGO_URI)
db = client["genvox"]
users_collection = db["genvox"]

class DarkBlueLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Set default parameters if not provided
        kwargs.setdefault('orientation', 'vertical')
        
        # Custom drawing for dark blue layout with light blue border
        with self.canvas.before:
            # Dark blue background
            Color(8/255, 20/255, 45/255, 0.9)
            self.rounded_rect = RoundedRectangle(
                pos=self.pos, 
                size=self.size, 
                radius=[20, 20, 20, 20]
            )
            
            # Light blue border
            Color(50/255, 130/255, 240/255, 0.7)
            self.border_line = Line(
                rounded_rectangle=[
                    self.pos[0], 
                    self.pos[1], 
                    self.size[0], 
                    self.size[1], 
                    20
                ],
                width=1.5
            )
        
        # Bind position and size updates
        self.bind(pos=self.update_canvas, size=self.update_canvas)
    
    def update_canvas(self, *args):
        # Update canvas drawings when position or size changes
        self.canvas.before.clear()
        with self.canvas.before:
            # Dark blue background
            Color(8/255, 20/255, 45/255, 0.9)
            self.rounded_rect = RoundedRectangle(
                pos=self.pos, 
                size=self.size, 
                radius=[20, 20, 20, 20]
            )
            
            # Light blue border
            Color(50/255, 130/255, 240/255, 0.7)
            self.border_line = Line(
                rounded_rectangle=[
                    self.pos[0], 
                    self.pos[1], 
                    self.size[0], 
                    self.size[1], 
                    20
                ],
                width=1.5
            )

class CurvedButton(Button):
    hover = BooleanProperty(False)
    ripple_alpha = NumericProperty(0)
    ripple_size = NumericProperty(0)
    
    def __init__(self, **kwargs):
        super(CurvedButton, self).__init__(**kwargs)
        self.bind(pos=self.update_canvas, size=self.update_canvas)
        Clock.schedule_once(self.update_canvas, 0)
        
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

class RoundedButton(Button):
    hover = BooleanProperty(False)
    
    def __init__(self, **kwargs):
        super(RoundedButton, self).__init__(**kwargs)
        self.size_hint = (None, None)
        self.size = (50, 50)
        self.background_normal = ''
        self.background_color = (0, 0, 0, 0)  # Transparent background
        self.color = (1, 1, 1, 1)  # White text
        self.bold = True
        self.bind(pos=self.update_canvas, size=self.update_canvas)
    
    def update_canvas(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            # Light blue circle background
            Color(100/255, 180/255, 240/255, 1 if not self.hover else 0.7)
            Ellipse(pos=self.pos, size=self.size)
    
    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            anim = Animation(size=(45, 45), duration=0.1)
            anim.start(self)
        return super(RoundedButton, self).on_touch_down(touch)
    
    def on_touch_up(self, touch):
        if self.collide_point(*touch.pos):
            anim = Animation(size=(50, 50), duration=0.2, t='out_back')
            anim.start(self)
        return super(RoundedButton, self).on_touch_up(touch)
    
    def on_mouse_pos(self, *args):
        if not self.get_root_window():
            return
        pos = args[1]
        if self.collide_point(*self.to_widget(*pos)):
            if not self.hover:
                self.hover = True
                self.update_canvas()
        else:
            if self.hover:
                self.hover = False
                self.update_canvas()

class ProfileScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Base layout with animation support
        layout = FloatLayout()
        
        # Set background color
        with self.canvas.before:
            Color(30/255, 40/255, 80/255, 1)  # Dark blue background
            self.bg = Rectangle(pos=self.pos, size=self.size)
        
        # Update rect method to fix previous error
        def update_rect(instance, *args):
            instance.bg.pos = instance.pos
            instance.bg.size = instance.size
        
        self.bind(pos=update_rect, size=update_rect)

        # Title Label - Moved to top of the page
        title_label = Label(
            text='Profile', 
            font_size=35, 
            bold=True, 
            color=(1, 1, 1, 1),  # White title
            pos_hint={'center_x': 0.5, 'top': 1.4}  # Positioned at the very top
        )
        layout.add_widget(title_label)

        # Back Button with your custom image in top left corner
        back_button = Button(
            background_normal='back.png',  # Use your custom back button image
            background_color=(1, 1, 1, 1),  # Ensure full color
            size_hint=(None, None),
            size=(50, 50),
            pos_hint={'x': 0.05, 'top': 0.95}  # Adjusted positioning
        )
        back_button.bind(on_press=self.go_back)
        layout.add_widget(back_button)
        
        # Main Profile Container
        profile_container = DarkBlueLayout(
            orientation="vertical",
            padding=20,
            spacing=15,
            size_hint=(None, None),
            size=(320, 480),
            pos_hint={"center_x": 0.5, "center_y": 0.45}  # Slightly adjusted vertical position
        )

        # Profile Image
       # Profile Image
        profile_image = Image(
            source="user_image.png",  # Verify this is the correct filename
            size_hint=(None, None), 
            size=(120, 120),
            pos_hint={"center_x": 0.5},
            allow_stretch=True,  # Allow image to be stretched
            keep_ratio=True,     # Maintain image aspect ratio
)
        profile_container.add_widget(profile_image)

        # User Info Layout
        info_layout = BoxLayout(
            orientation="vertical", 
            spacing=15, 
            size_hint_y=None, 
            height=180
        )

        # Dynamically create input rows
        self.input_fields = {
            "NAME:": TextInput(text="", multiline=False, disabled=True),
            "EMAIL:": TextInput(text="", multiline=False, disabled=True),
            "PASSWORD:": TextInput(text="", password=True, multiline=False, disabled=True)
        }

        for label_text, input_field in self.input_fields.items():
            row_layout = BoxLayout(orientation="horizontal", size_hint_y=None, height=50)
            
            # Label
            label = Label(
                text=label_text, 
                font_size=18, 
                color=(1, 1, 1, 1), 
                size_hint_x=0.4, 
                halign="left"
            )
            label.bind(size=lambda instance, value: setattr(instance, 'text_size', value))
            
            # Input Field (with matching style)
            input_field.background_color = (1, 1, 1, 0.1)
            input_field.foreground_color = (1, 1, 1, 1)
            input_field.selection_color = (100/255, 180/255, 240/255, 0.5)
            input_field.size_hint_x = 0.6
            
            row_layout.add_widget(label)
            row_layout.add_widget(input_field)
            info_layout.add_widget(row_layout)

        profile_container.add_widget(info_layout)

        # Button Layout for Edit and Save
        edit_save_layout = BoxLayout(
            orientation='horizontal',
            spacing=10,
            size_hint=(None, None),  # Changed from size_hint_y to size_hint
            size=(320, 60),  # Specify a fixed size
            pos_hint={"center_x": 0.5}
        )

        # Edit Button
        self.edit_button = CurvedButton(
            text="EDIT", 
            size_hint=(None, None),
            size=(150, 60),
            color=(15/255, 30/255, 100/255, 1)  # Dark blue text
        )
        self.edit_button.bind(on_press=self.enable_edit)
        
        # Save Button
        self.save_button = CurvedButton(
            text="SAVE", 
            disabled=True,
            size_hint=(None, None),
            size=(150, 60),
            color=(15/255, 30/255, 100/255, 1)  # Dark blue text
        )
        self.save_button.bind(on_press=self.save_profile)
        
        edit_save_layout.add_widget(self.edit_button)
        edit_save_layout.add_widget(self.save_button)
        profile_container.add_widget(edit_save_layout)

        # Logout Button
        logout_button = CurvedButton(
            text="Logout", 
            size_hint_y=None, 
            height=60, 
            pos_hint={"center_x": 0.5},
            color=(15/255, 30/255, 100/255, 1)  # Dark blue text
        )
        logout_button.bind(on_press=self.logout)
        profile_container.add_widget(logout_button)

        layout.add_widget(profile_container)
        self.add_widget(layout)


    def go_back(self, instance):
        # Transition to home.py screen
        self.manager.current = 'home'  # Ensure this matches the name in your ScreenManager

    def enable_edit(self, instance):
        for field in self.input_fields.values():
            field.disabled = False
        self.save_button.disabled = False
        self.edit_button.disabled = True

    def save_profile(self, instance):
        new_data = {
            "name": self.input_fields["NAME:"].text,
            "email": self.input_fields["EMAIL:"].text,
            "password": self.input_fields["PASSWORD:"].text
        }
        users_collection.update_one({"email": self.input_fields["EMAIL:"].text}, {"$set": new_data})
        for field in self.input_fields.values():
            field.disabled = True
        self.save_button.disabled = True
        self.edit_button.disabled = False

    def logout(self, instance):
        # Add fade-out animation before transitioning
        fade_out = Animation(opacity=0, duration=0.3)
        fade_out.bind(on_complete=lambda *args: self.transition_to_login())
        fade_out.start(self)
    
    def transition_to_login(self):
        self.manager.current = "index"
        self.opacity = 1  # Reset opacity for next time

    def on_pre_enter(self):
        email = App.get_running_app().user_email
        print(f"📩 on_pre_enter triggered with email: {email}")  # Debugging log
        if email:
            self.load_user_data(email)
        else:
            print("⚠️ No email found in App context")

    def load_user_data(self, email):
        print(f"🔍 Fetching data for email: {email}")  # Debugging log
        user_data = users_collection.find_one({"email": email})

        if user_data:
            print("✅ User data found:", user_data)  # Debugging log
            self.input_fields["NAME:"].text = user_data.get("name", "Not Found")
            self.input_fields["EMAIL:"].text = user_data.get("email", "Not Found")
            self.input_fields["PASSWORD:"].text = user_data.get("password", "Not Found")
        else:
            print("⚠️ User data not found!")

class ProfileApp(App):
    user_email = "test@example.com"  # Default email for testing

    def build(self):
        sm = ScreenManager()
        sm.add_widget(ProfileScreen(name="profile"))
        sm.add_widget(Screen(name="index"))
        sm.add_widget(Screen(name="home"))
        return sm

if __name__ == "__main__":
    Window.size = (400, 700)
    ProfileApp().run()