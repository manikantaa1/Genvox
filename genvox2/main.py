import kivy
from kivy.app import App
from kivy.uix.screenmanager import Screen, ScreenManager
from index_page import IndexScreen
from signin_page import SignInScreen
from login_page import LoginScreen
from home import MainScreen
from chatbot import ChatBotUI
from voice_interface import VoiceAssistantUI
from profile_page import ProfileScreen
from menu_page import MenuScreen
from imagegenereation import ImageGeneratorScreen
from textgeneration import TextGeneratorScreen
from codegeneration import CodeGeneratorScreen
from poetrygeneration import PoetryGeneratorScreen
from problemsolver import ProblemSolverScreen
from Storyteller import StoryGeneratorScreen
from translator import TranslatorScreen
from text_to_speech import SpeechScreen
from textsummarization import SummarizationScreen
from about_page import HomePage 
from admin_page import AdminLoginScreen
from admindashboard import AdminDashboardScreen

# Define the minimum Kivy version required
kivy.require('2.0.0')

# Wrapping ChatBotUI & VoiceAssistantUI inside Screen classes
class ChatBotScreen(Screen):
    def __init__(self, **kwargs):
        super(ChatBotScreen, self).__init__(**kwargs)
        self.add_widget(ChatBotUI())  # ✅ Properly added inside Screen

class VoiceAssistantScreen(Screen):
    def __init__(self, **kwargs):
        super(VoiceAssistantScreen, self).__init__(**kwargs)
        self.add_widget(VoiceAssistantUI())  # ✅ Properly added inside Screen

class MainApp(App):
    user_email = None  # Store logged-in user email
    def build(self):
        sm = ScreenManager()

        # Adding all screens to the screen manager
        sm.add_widget(IndexScreen(name="index"))
        sm.add_widget(SignInScreen(name="signin"))
        sm.add_widget(LoginScreen(name="login"))
        sm.add_widget(MainScreen(name="home"))
        sm.add_widget(ChatBotScreen(name="chatbot"))  # ✅ Fixed
        sm.add_widget(VoiceAssistantScreen(name="voice"))  # ✅ Fixed
        sm.add_widget(ProfileScreen(name="profile"))
        sm.add_widget(MenuScreen(name="menu"))
        sm.add_widget(ImageGeneratorScreen(name="image"))
        sm.add_widget(TextGeneratorScreen(name="textbot"))
        sm.add_widget(CodeGeneratorScreen(name="code"))
        sm.add_widget(PoetryGeneratorScreen(name="poem"))
        sm.add_widget(ProblemSolverScreen(name="solve"))
        sm.add_widget(StoryGeneratorScreen(name="Story"))
        sm.add_widget(TranslatorScreen(name="trans"))
        sm.add_widget(SpeechScreen(name="speech"))
        sm.add_widget(SummarizationScreen(name="Summarize"))
        sm.add_widget(HomePage(name="about"))
        sm.add_widget(AdminLoginScreen(name="admin"))
        sm.add_widget(AdminDashboardScreen(name="admim_dashboard"))
        sm.current = "index"  # Start from the Index Page
        return sm

if __name__ == "__main__":
    MainApp().run()
