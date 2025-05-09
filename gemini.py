import google.generativeai as genai
from google.api_core import exceptions
import streamlit as st
from config import Config

class GeminiAssistant:
    def __init__(self):
        self.config = Config()
        self.model = self._initialize_model()
        
    def _initialize_model(self):
        """Initialize the first available model from the updated list"""
        genai.configure(api_key=self.config.API_KEY)
        
        for model_name in self.config.MODEL_NAMES:
            try:
                model = genai.GenerativeModel(model_name)
                # Test the model with a simple prompt
                model.generate_content("Test connection")
                st.session_state.current_model = model_name
                st.success(f"Connected to: {model_name}")
                return model
            except Exception as e:
                st.warning(f"Model {model_name} unavailable: {str(e)}")
                continue
                
        st.error("No working model found. Please check your API access.")
        st.stop()
    
    def generate_response(self, prompt):
        """Generate response from Gemini"""
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=self.config.GENERATION_CONFIG,
                safety_settings=self.config.SAFETY_SETTINGS
            )
            return response.text
        except Exception as e:
            raise RuntimeError(f"Generation failed: {str(e)}")