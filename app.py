import streamlit as st
import json
import uuid
from services import bedrock_agent_runtime 

# Set up Streamlit page configuration
st.title('VALORANT eSports Manager Chatbot')
st.write('Enter a prompt to receive a response from the Bedrock Agent.')

# Function to handle invoking the Bedrock Agent
def get_bedrock_agent_response(prompt):
    # Retrieve Agent ID and Alias ID from Streamlit secrets
    agent_id = st.secrets["AWS_AGENT_ID"]  # Use your Bedrock Agent ID
    agent_alias_id = st.secrets["AWS_ALIAS_ID"]  # Use your Bedrock Agent Alias
    session_id = str(uuid.uuid4())  # Generate a unique session ID

    try:
        # Invoke the Bedrock Agent using the defined logic
        response = bedrock_agent_runtime.invoke_agent(
            agent_id,
            agent_alias_id,
            session_id,
            prompt
        )
        return response
    except Exception as e:
        st.error(f"An error occurred: {e}")
        return None

# User input for the prompt
prompt = st.text_area('Your Prompt', height=200)

# When the user submits the prompt
if st.button('Submit'):
    if prompt.strip():
        with st.spinner('Processing...'):
            response = get_bedrock_agent_response(prompt)
            if response:
                # Display the response text
                st.subheader('Model Response:')
                st.write(response["output_text"])

                # Display any citations found
                if response["citations"]:
                    st.subheader("Citations:")
                    for citation in response["citations"]:
                        st.write(f"- {citation}")

                # Optional: Show traces (for debugging or insights)
                if response["trace"]:
                    st.subheader("Trace Information:")
                    trace_str = json.dumps(response["trace"], indent=2)
                    st.code(trace_str, language="json")
    else:
        st.warning('Please enter a prompt before submitting.')
