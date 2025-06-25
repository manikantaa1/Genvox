from kivy.app import App
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.uix.screenmanager import Screen,ScreenManager
from kivy.core.window import Window
from kivy.uix.behaviors import ButtonBehavior

class InteractiveImage(ButtonBehavior, Image):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Add a subtle hover effect
        self.opacity = 0.8
    
    def on_press(self):
        # Slight press animation
        self.opacity = 0.5
    
    def on_release(self):
        # Restore opacity
        self.opacity = 0.8

class HomePage(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Main layout
        main_layout = BoxLayout(orientation='vertical')
        
        # Background color
        with main_layout.canvas.before:
            Color(30/255, 40/255, 80/255, 1)  # Deep blue background
            self.bg = Rectangle(pos=main_layout.pos, size=main_layout.size)
        
        # Update background when layout changes
        main_layout.bind(pos=self.update_bg, size=self.update_bg)
        
        # ScrollView for content
        scroll = ScrollView(do_scroll_x=False)
        
        # Content layout
        content_layout = BoxLayout(
            orientation='vertical', 
            size_hint_y=None, 
            padding=[20, 10, 20, 20], 
            spacing=15
        )
        content_layout.bind(minimum_height=content_layout.setter('height'))
        
        # Back Button as Interactive Image
        back_btn = InteractiveImage(
            source='back.png',  # Replace with your image path
            size_hint=(None, None),
            size=(50, 50),
            pos_hint={'x': 0.02, 'top': 0.98}
        )
        back_btn.bind(on_release=self.go_back)
        
        # Title with interactive hover effect
        title_label = Label(
            text="About GenVox", 
            font_size=35, 
            bold=True, 
            color=(1, 1, 1, 1),  # White text
            size_hint_y=None,
            height=50
        )
        
        # Sections with interactive labels
        def create_section_label(text, font_size=26, bold=True):
            label = Label(
                text=text, 
                font_size=font_size, 
                bold=bold, 
                color=(1, 1, 1, 1),  # White text
                size_hint_y=None, 
                height=50,
                halign='left',
                text_size=(Window.width-40, None)
            )
            return label
        
        def create_content_label(text, font_size=16):
            # Create a BoxLayout to wrap the content with improved alignment
            content_layout = BoxLayout(
                orientation='vertical', 
                size_hint_y=None, 
                padding=[10, 0],
                spacing=10
            )
            
            # Create the label with improved formatting
            content_label = Label(
                text=text, 
                font_size=font_size, 
                color=(220/255, 220/255, 220/255, 1),  # Light gray text
                size_hint_y=None, 
                halign='left',
                valign='top',
                text_size=(Window.width-40, None)
            )
            
            # Dynamically adjust height based on content
            content_label.bind(texture_size=content_label.setter('size'))
            
            # Add the label to the layout
            content_layout.add_widget(content_label)
            
            return content_layout
        
        # About Section
        about_section = create_section_label("About Us")
        about_content = create_content_label(
            "GenVox: A cutting-edge voice-activated multimodal generative AI companion "
            "that revolutionizes human-AI interaction through advanced natural language processing, "
            "intelligent voice commands, and multi-format content generation."
        )
        
        # Core Features Section
        features_section = create_section_label("Core Features")
        features_content = create_content_label(
            "• Voice-Controlled Text Generation: Create stories, content, and summaries\n"
            "• Image Creation via Voice Prompts: Generate art and illustrations\n"
            "• Audio and Music Synthesis: Create unique soundscapes\n"
            "• Video and Animation Generation: Bring spoken concepts to life\n"
            "• Adaptive Interaction: Personalized AI companion experience"
        )
        
        # Developers Section
        developers_section = create_section_label("Developers", font_size=24)
        developers_content = create_content_label(
            "• J. Mahalakshmi\n"
            "• P. Mani Kanta\n"
            "• S.V.V. Prasanna Kumar\n"
            "• L. Ganesh Kumar", 
            font_size=18
        )
        
        # Assemble the layout
        content_layout.add_widget(title_label)
        content_layout.add_widget(about_section)
        content_layout.add_widget(about_content)
        content_layout.add_widget(features_section)
        content_layout.add_widget(features_content)
        content_layout.add_widget(developers_section)
        content_layout.add_widget(developers_content)
        
        # Add back button to main layout
        main_layout.add_widget(back_btn)
        
        # Finalize layout
        scroll.add_widget(content_layout)
        main_layout.add_widget(scroll)
        self.add_widget(main_layout)
    
    def update_bg(self, *args):
        self.bg.pos = self.pos
        self.bg.size = self.size
    
    def go_back(self, instance):
        self.manager.current = "index"

class MyApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(HomePage(name="about"))
        sm.add_widget(Screen(name="index"))
        sm.current = "about"
        return sm

if __name__ == "__main__":
    MyApp().run()