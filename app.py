import streamlit as st
import json
import uuid
from services import bedrock_agent_runtime 
import re

# Set up Streamlit page configuration
st.set_page_config(
    page_title="VALORANT eSports ScoutBot",
    page_icon="🎯",
    layout="centered"
)

# Display the welcome message once, at the start of the session
if "has_started" not in st.session_state:
    st.session_state.has_started = True
    st.write(
        """
        # Welcome to VALORANT eSports ScoutBot! 🎯
        Hi there! 👋 I'm ScoutBot, your friendly digital assistant here to help with scouting and recruiting top VALORANT esports players. 
        Whether you're looking to build a well-rounded team, analyze player performance, or explore potential recruits, I'm here to assist you every step of the way. 

        You can ask me questions like:
        - "Build a team using only players from VCT International."
        - "Build a team that includes at least two players from an underrepresented group, such as the Game Changers program."
        - "Can you give insights on player performance with specific agents?"

        My goal is to make your scouting process easier and help you assemble a winning team! Let’s get started! 🚀
        """
    )

# Initialize session state
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())  # Generate a unique session ID
if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []  # Initialize conversation history

# Function to handle invoking the Bedrock Agent
def get_bedrock_agent_response(prompt):
    # Retrieve Agent ID and Alias ID from Streamlit secrets
    agent_id = st.secrets["AWS_AGENT_ID"]
    agent_alias_id = st.secrets["AWS_ALIAS_ID"]
    session_id = st.session_state.session_id

    # Check Prompt for team building, provide additional context
    if re.search(r"\bbuild a team\b", prompt.lower()):
        modified_prompt = (prompt 
                           + " List all 5 players and their roles. Include category of agents."
                           + " Give player performance."
                           + " 1 of these players must also take on additional role of in-game leader (IGL)." 
                           + " Give team strategy, strengths and weaknesses, language issues.")
    else:
        modified_prompt = prompt

    try:
        # Combine structured conversation history with the current prompt
        structured_history = [
            f"User: {entry['user']}\nAgent: {entry['agent']}" for entry in st.session_state.conversation_history
        ]
        combined_prompt = "\n".join(structured_history + [f"User: {modified_prompt}"])
        
        # Invoke the Bedrock Agent using the combined structured prompt
        response = bedrock_agent_runtime.invoke_agent(  
            agent_id,
            agent_alias_id,
            session_id,
            combined_prompt
        )
        
        # Store the conversation in a structured format
        st.session_state.conversation_history.append({
            "user": prompt,
            "agent": response["output_text"],
            "trace": response.get("trace", None)
        })
        
        return response
    except Exception as e:
        st.error(f"An error occurred: {e}")
        return None

# Create a chat-like interface with the conversation history
st.write("### Chat with ScoutBot")

# Add CSS to make the chat scrollable and more like a traditional chat box
st.markdown("""
    <style>
    .chat-container {
        height: 500px;
        overflow-y: auto;
        border: 1px solid #ccc;
        padding: 10px;
        background-color: #f9f9f9;
        border-radius: 5px;
        display: flex;
        flex-direction: column-reverse; /* Keep the latest messages at the bottom */
    }
    .message {
        padding: 5px;
        margin-bottom: 5px;
    }
    .user-message {
        text-align: left;
        font-weight: bold;
        color: #003399;
    }
    .bot-message {
        text-align: left;
        font-weight: bold;
        color: #228B22;
    }
    </style>
    """, unsafe_allow_html=True)

# Display the chat history inside the styled container
with st.container():
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    for chat in reversed(st.session_state.conversation_history):
        st.markdown(f"<div class='message user-message'>🗨️ User: {chat['user']}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='message bot-message'>🤖 ScoutBot: {chat['agent']}</div>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# User input for the prompt
prompt = st.text_area('Your Prompt', height=100)

# When the user submits the prompt
if st.button('Send'):
    if prompt.strip():
        with st.spinner('Processing...'):
            response = get_bedrock_agent_response(prompt)
            if response:
                # The conversation is automatically displayed on each re-run
                pass
    else:
        st.warning('Please enter a prompt before sending.')
