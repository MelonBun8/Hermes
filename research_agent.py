import os
from langchain.tools import DuckDuckGoSearchRun
from langchain.agents import initialize_agent, AgentType
from langchain.memory import ConversationBufferMemory
from langchain.prompts import MessagesPlaceholder
from langchain_core.messages import SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from config import Config

class ResearchAgent:
    def __init__(self):
        self.config = Config()
        self.search_tool = DuckDuckGoSearchRun()
        self.llm = self._initialize_llm()
        self.memory = ConversationBufferMemory(return_messages=True, memory_key="chat_history")
        self.agent = self._initialize_agent()
       
    def _initialize_llm(self):
        """Initialize the Gemini model for LangChain usage"""
        os.environ["GOOGLE_API_KEY"] = self.config.API_KEY
        return ChatGoogleGenerativeAI(
            model=self.config.MODEL_NAMES[0],
            temperature=self.config.GENERATION_CONFIG["temperature"],
            convert_system_message_to_human=True
        )
   
    def _initialize_agent(self):
        """Initialize the LangChain agent with tools"""
        tools = [self.search_tool]
        
        # Define the system message
        system_message = """You are a research assistant that helps people find accurate information. 
Always cite your sources with proper URLs. 
Format your responses with markdown and structure them well."""
       
        # Create agent with updated format
        return initialize_agent(
            tools=tools,
            llm=self.llm,
            agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
            memory=self.memory,
            verbose=True,
            agent_kwargs={
                "system_message": system_message,
                "extra_prompt_messages": [MessagesPlaceholder(variable_name="chat_history")]
            }
        )
   
    def research(self, query):
        """Perform research on a topic with citations"""
        structured_query = f"""Research the following topic and provide detailed information with proper citations:
        {query}
       
        Structure your response with:
        1. Key Findings (bullet points)
        2. Relevant Studies (with citations to specific sources)
        3. Current Challenges
        4. Future Directions
       
        For each fact or claim, include a citation to a specific source URL in [Source: URL] format.
        """
       
        try:
            return self.agent.run(structured_query)
        except Exception as e:
            return f"Error performing research: {str(e)}"