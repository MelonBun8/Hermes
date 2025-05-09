import streamlit as st
import atexit
import base64
from gemini import GeminiAssistant
from database import DatabaseManager
from pdf import export_conversation_to_pdf
from auth import login_page, AuthManager

def initialize_session():
    """Initialize session state variables"""
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'gemini' not in st.session_state:
        st.session_state.gemini = GeminiAssistant()
    if 'db' not in st.session_state:
        st.session_state.db = DatabaseManager()
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'auth_manager' not in st.session_state:
        st.session_state.auth_manager = AuthManager()

def render_sidebar():
    """Render sidebar components"""
    with st.sidebar:
        st.title("Settings")
        if st.button("🔄 Clear Conversation"):
            st.session_state.messages = []
            st.rerun()
        
        # Export to PDF button
        if st.session_state.messages and len(st.session_state.messages) > 0:
            if st.button("📄 Export to PDF"):
                pdf_data = export_conversation_to_pdf(st.session_state.messages)
                b64_pdf = base64.b64encode(pdf_data).decode('utf-8')
                href = f'<a href="data:application/pdf;base64,{b64_pdf}" download="research_conversation.pdf">Download PDF</a>'
                st.markdown(href, unsafe_allow_html=True)
        
        # Logout button
        if st.button("🚪 Logout"):
            st.session_state.logged_in = False
            st.rerun()
        
        st.divider()
        st.markdown(f"**Current Model:**\n`{getattr(st.session_state, 'current_model', 'N/A')}`")
        st.markdown(f"**Logged in as:**\n`{getattr(st.session_state, 'username', 'N/A')}`")
        
        st.markdown("**Conversation History**")
        for conv in st.session_state.db.get_recent_conversations():
            if st.button(f"🗨️ {conv[1][:30]}...", key=f"hist_{conv[0]}"):
                load_conversation(conv[0])

def load_conversation(conv_id):
    """Load specific conversation by ID"""
    conv = st.session_state.db.get_conversation_by_id(conv_id)
    
    if conv:
        st.session_state.messages = [
            {"role": "user", "content": conv[1]},
            {"role": "assistant", "content": conv[2], "id": conv[0]}
        ]
        st.rerun()

def render_chat_interface():
    """Render main chat interface"""
    st.title("🔬 Hermes Research Assistant")
    st.caption("Powered by Gemini AI - Get instant research summaries")
    
    # Display messages
    for i, message in enumerate(st.session_state.messages):
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message["role"] == "assistant" and i > 0:
                cols = st.columns([1, 1, 10])
                with cols[0]:
                    if st.button("👍", key=f"like_{i}"):
                        st.session_state.db.update_likes(message["id"])
                with cols[1]:
                    if st.button("🗑️", key=f"delete_{i}"):
                        st.session_state.db.delete_conversation(message["id"])
                        st.rerun()
    
    # User input
    if prompt := st.chat_input("Ask a research question..."):
        handle_user_input(prompt)

def handle_user_input(prompt):
    """Process user input and generate response"""
    with st.chat_message("user"):
        st.markdown(prompt)
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("assistant"):
        with st.spinner("Researching..."):
            try:
                research_prompt = f"""Provide a detailed research response about: {prompt}
                Structure your response with:
                1. Key Findings (bullet points)
                2. Relevant Studies (with citations if possible)
                3. Current Challenges
                4. Future Directions"""
                
                response = st.session_state.gemini.generate_response(research_prompt)
                conv_id = st.session_state.db.save_conversation(
                    prompt, 
                    response, 
                    st.session_state.current_model
                )
                
                st.markdown(response)
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": response,
                    "id": conv_id
                })
                
            except Exception as e:
                st.error(f"Research failed: {str(e)}")

def main():
    st.set_page_config(page_title="Hermes Research AI", layout="wide")
    
    # Initialize database manager
    if 'db' not in st.session_state:
        st.session_state.db = DatabaseManager()
        # Ensure cleanup on exit
        atexit.register(st.session_state.db.close_all)
    
    initialize_session()
    
    # Check if user is logged in
    if not st.session_state.logged_in:
        login_page()
    else:
        render_sidebar()
        render_chat_interface()

if __name__ == "__main__":
    main()