import streamlit as st
import atexit
from gemini import GeminiAssistant
from database import DatabaseManager

def initialize_session():
    """Initialize session state variables"""
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'gemini' not in st.session_state:
        st.session_state.gemini = GeminiAssistant()
    if 'db' not in st.session_state:
        st.session_state.db = DatabaseManager()

def render_sidebar():
    """Render sidebar components"""
    with st.sidebar:
        st.title("Settings")
        if st.button("🔄 Clear Conversation"):
            st.session_state.messages = []
            st.rerun()
        
        st.divider()
        st.markdown(f"**Current Model:**\n`{getattr(st.session_state, 'current_model', 'N/A')}`")
        
        st.markdown("**Conversation History**")
        for conv in st.session_state.db.get_recent_conversations():
            if st.button(f"🗨️ {conv[1][:30]}...", key=f"hist_{conv[0]}"):
                load_conversation(conv[0])

def load_conversation(conv_id):
    """Load specific conversation"""
    conv = st.session_state.db.get_recent_conversations(1)
    if conv:
        st.session_state.messages = [
            {"role": "user", "content": conv[0][1]},
            {"role": "assistant", "content": conv[0][2], "id": conv[0][0]}
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
    render_sidebar()
    render_chat_interface()

if __name__ == "__main__":
    main()