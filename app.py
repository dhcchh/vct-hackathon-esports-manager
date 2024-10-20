import streamlit as st
import json
import uuid
from services import bedrock_agent_runtime 
import re

# Set up Streamlit page configuration
st.title('Welcome to VALORANT eSports ScoutBot! 🎯')
st.write(
    """
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
                           + "List all 5 players and their roles. Include category of agents."
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

# Display conversation history in a chat-like interface
st.write("### Conversation History")
for chat in st.session_state.conversation_history:
    st.write(f"**User:** {chat['user']}")
    st.write(f"**ScoutBot:** {chat['agent']}")
    st.write("---")  # Separator line for readability

# User input for the prompt
prompt = st.text_area('Your Prompt', height=100)

# When the user submits the prompt
if st.button('Submit'):
    if prompt.strip():
        with st.spinner('Processing...'):
            response = get_bedrock_agent_response(prompt)
            if response:
                # Display any citations found (optional)
                if response.get("citations"):
                    st.subheader("Citations:")
                    for citation in response["citations"]:
                        st.write(f"- {citation}")
    else:
        st.warning('Please enter a prompt before submitting.')
