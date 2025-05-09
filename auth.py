import streamlit as st
import hashlib
import sqlite3

class AuthManager:
    def __init__(self, db_name='research_chat.db'):
        self.db_name = db_name
        self._initialize_auth_table()
    
    def _initialize_auth_table(self):
        """Initialize users table if it doesn't exist"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        # Check if table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        table_exists = cursor.fetchone()
        
        if not table_exists:
            cursor.execute('''
                CREATE TABLE users (
                    id INTEGER PRIMARY KEY,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()
            
            # Create default admin user
            self.register_user("admin", "admin123")
            
        conn.close()
    
    def _hash_password(self, password):
        """Create a hash of the password"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def register_user(self, username, password):
        """Register a new user"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        try:
            password_hash = self._hash_password(password)
            cursor.execute(
                "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                (username, password_hash)
            )
            conn.commit()
            success = True
        except sqlite3.IntegrityError:
            # Username already exists
            success = False
        
        conn.close()
        return success
    
    def authenticate(self, username, password):
        """Authenticate a user"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        password_hash = self._hash_password(password)
        cursor.execute(
            "SELECT id FROM users WHERE username = ? AND password_hash = ?",
            (username, password_hash)
        )
        user = cursor.fetchone()
        
        conn.close()
        return user is not None

def login_page():
    """Display login page"""
    if 'auth_manager' not in st.session_state:
        st.session_state.auth_manager = AuthManager()
    
    st.title("🔒 Hermes Research Assistant")
    st.subheader("Login")
    
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")
        
        if submitted:
            if st.session_state.auth_manager.authenticate(username, password):
                st.session_state.logged_in = True
                st.session_state.username = username
                st.rerun()
            else:
                st.error("Invalid username or password")
    
    st.divider()
    
    # Registration expander
    with st.expander("Register New User"):
        with st.form("register_form"):
            new_username = st.text_input("New Username")
            new_password = st.text_input("New Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            register_submitted = st.form_submit_button("Register")
            
            if register_submitted:
                if new_password != confirm_password:
                    st.error("Passwords do not match")
                elif len(new_password) < 6:
                    st.error("Password must be at least 6 characters")
                else:
                    if st.session_state.auth_manager.register_user(new_username, new_password):
                        st.success("Registration successful. You can now login.")
                    else:
                        st.error("Username already exists")