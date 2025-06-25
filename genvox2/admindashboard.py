from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from pymongo import MongoClient

# MongoDB Connection
MONGO_URI = "mongodb://localhost:27017/"
client = MongoClient(MONGO_URI)
db = client["genvox"]
user_collection = db["genvox"]


class AdminDashboardScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Header
        header = BoxLayout(size_hint_y=None, height=50)
        header.add_widget(Label(text="Admin Dashboard", font_size=24))
        self.main_layout.add_widget(header)

        # Load Users Button
        load_users_button = Button(text="Load Users", size_hint_y=None, height=50, background_color=(0, 0.6, 1, 1))
        load_users_button.bind(on_press=self.load_users)
        self.main_layout.add_widget(load_users_button)

        # Add New User Button
        add_user_button = Button(text="Add New User", size_hint_y=None, height=50, background_color=(0, 1, 0, 1))
        add_user_button.bind(on_press=self.add_user_popup)
        self.main_layout.add_widget(add_user_button)

        # Scrollable User List
        self.scroll = ScrollView()
        self.user_grid = GridLayout(cols=1, spacing=10, size_hint_y=None)
        self.user_grid.bind(minimum_height=self.user_grid.setter('height'))
        self.scroll.add_widget(self.user_grid)
        self.main_layout.add_widget(self.scroll)

        # Logout Button
        logout_button = Button(text="Logout", size_hint_y=None, height=50, background_color=(1, 0, 0, 1))
        logout_button.bind(on_press=self.logout)
        self.main_layout.add_widget(logout_button)

        self.add_widget(self.main_layout)

    def load_users(self, instance):
        self.user_grid.clear_widgets()
        users = user_collection.find()

        for user in users:
            user_box = BoxLayout(orientation='horizontal', size_hint_y=None, height=50)
            user_box.add_widget(Label(text=f"Name: {user.get('name', '')} | Email: {user.get('email', '')}", size_hint_x=0.6))

            # Edit Button
            edit_btn = Button(text="Edit", size_hint_x=None, width=80)
            edit_btn.bind(on_press=lambda x, u=user: self.edit_user_popup(u))
            user_box.add_widget(edit_btn)

            # Delete Button
            del_btn = Button(text="Delete", size_hint_x=None, width=80)
            del_btn.bind(on_press=lambda x, u=user: self.delete_user(u))
            user_box.add_widget(del_btn)

            self.user_grid.add_widget(user_box)

    def edit_user_popup(self, user):
        popup_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        name_input = TextInput(text=user.get('name', ''), hint_text="Name")
        email_input = TextInput(text=user.get('email', ''), hint_text="Email")
        password_input = TextInput(hint_text="Password (optional)", password=True)

        popup_layout.add_widget(name_input)
        popup_layout.add_widget(email_input)
        popup_layout.add_widget(password_input)

        def save_changes(instance):
            update_data = {
                "name": name_input.text.strip(),
                "email": email_input.text.strip()
            }
            if password_input.text.strip():
                update_data['password'] = password_input.text.strip()

            user_collection.update_one({"_id": user["_id"]}, {"$set": update_data})
            popup.dismiss()
            self.load_users(None)  # Refresh user list

        save_btn = Button(text="Save", on_press=save_changes)
        popup_layout.add_widget(save_btn)

        popup = Popup(title="Edit User", content=popup_layout, size_hint=(0.8, 0.6))
        popup.open()

    def delete_user(self, user):
        user_collection.delete_one({"_id": user["_id"]})
        self.load_users(None)  # Refresh user list

    def add_user_popup(self, instance):
        popup_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        name_input = TextInput(hint_text="Name")
        email_input = TextInput(hint_text="Email")
        password_input = TextInput(hint_text="Password", password=True)

        popup_layout.add_widget(name_input)
        popup_layout.add_widget(email_input)
        popup_layout.add_widget(password_input)

        def create_user(instance):
            user_data = {
                "name": name_input.text.strip(),
                "email": email_input.text.strip(),
                "password": password_input.text.strip()
            }
            user_collection.insert_one(user_data)
            popup.dismiss()
            self.load_users(None)  # Refresh list

        save_btn = Button(text="Add User", on_press=create_user)
        popup_layout.add_widget(save_btn)

        popup = Popup(title="Add New User", content=popup_layout, size_hint=(0.8, 0.6))
        popup.open()

    def logout(self, instance):
        self.manager.current = "admin"  # Redirect to admin login screen
