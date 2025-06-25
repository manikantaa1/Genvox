from pymongo import MongoClient

# MongoDB Connection (Local or Cloud)
MONGO_URI = "mongodb://localhost:27017/"  # Use this for local MongoDB
# MONGO_URI = "mongodb+srv://your_user:your_password@your_cluster.mongodb.net/"  # MongoDB Atlas

client = MongoClient(MONGO_URI)
db = client["genvox"]  # Database name
users_collection = db["genvox"]  # Collection for user data

def create_user(name, email, password):
    """Insert new user into the database (Sign-up)"""
    if users_collection.find_one({"email": email}):
        return "User already exists!"
    
    user_data = {
        "name": name,
        "email": email,
        "password": password,  # ⚠️ Hash password in production!
    }
    users_collection.insert_one(user_data)
    return "User created successfully!"

def login_user(self, email, password):
    """Handle login logic"""
    print(f"🛠️ Login Attempt: {email}, {password}")  # Debugging
    user_data = get_user(email)

    if user_data and user_data["password"] == password:
        print("✅ Login Successful!")
        
        # Pass email to ProfileScreen
        profile_screen = self.manager.get_screen("profile")
        profile_screen.load_user_data(email)
        
        self.manager.current = "profile"  # Navigate to profile page
    else:
        print("❌ Invalid Credentials!")

def authenticate_user(email, password):
    """Check if user exists in database (Login)"""
    user = users_collection.find_one({"email": email})
    if user and user["password"] == password:
        return user  # Login successful
    return None  # Login failed

def get_user(email):
    """Fetch user data from MongoDB"""
    print(f"🔍 Fetching data for email: {email}")  # Debugging
    user_data = users_collection.find_one({"email": email})
    
    if user_data:
        print(f"📢 Retrieved User Data: {user_data}")
        return user_data
    else:
        print("⚠️ User data not found!")
        return None

def update_user(email, new_data):
    """Update user details"""
    users_collection.update_one({"email": email}, {"$set": new_data})
    return "User profile updated!"
