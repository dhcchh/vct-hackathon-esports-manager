import json
import os
from services import bedrock_agent_runtime
import streamlit as st
import uuid

# Get config from environment variables
agent_id = os.environ.get("BEDROCK_AGENT_ID")
agent_alias_id = os.environ.get("BEDROCK_AGENT_ALIAS_ID", "TSTALIASID")  # Default alias ID for testing
ui_title = os.environ.get("BEDROCK_AGENT_TEST_UI_TITLE", "Agents for Amazon Bedrock Test UI")
ui_icon = os.environ.get("BEDROCK_AGENT_TEST_UI_ICON")

def init_state():
    st.session_state.session_id = str(uuid.uuid4())
    st.session_state.messages = []
    st.session_state.citations = []
    st.session_state.trace = {}

# General page configuration and initialization
st.set_page_config(page_title=ui_title, page_icon=ui_icon, layout="wide")
st.title(ui_title)
if len(st.session_state.items()) == 0:
    init_state()

# Sidebar button to reset session state
with st.sidebar:
    if st.button("Reset Session"):
        init_state()

# Display chat history from session state
for message in st.session_state.messages:
    if message["role"] == "user":
        with st.chat_message("user"):
            st.markdown(f"🗨️ **User:** {message['content']}", unsafe_allow_html=True)
    elif message["role"] == "assistant":
        with st.chat_message("assistant"):
            st.markdown(f"🤖 **ScoutBot:** {message['content']}", unsafe_allow_html=True)

# Chat input that invokes the agent
if prompt := st.chat_input("Type your message here..."):
    # Append the user's input to the message history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(f"🗨️ **User:** {prompt}")

    # Create a placeholder for ScoutBot's response
    with st.chat_message("assistant"):
        placeholder = st.empty()
        placeholder.markdown("🤖 ScoutBot is thinking...")

        # Call Bedrock agent to get a response
        response = bedrock_agent_runtime.invoke_agent(
            agent_id,
            agent_alias_id,
            st.session_state.session_id,
            prompt
        )

        output_text = response["output_text"]

        # Add citations if any are present
        if len(response["citations"]) > 0:
            citation_num = 1
            num_citation_chars = 0
            citation_locs = ""
            for citation in response["citations"]:
                end_span = citation["generatedResponsePart"]["textResponsePart"]["span"]["end"] + 1
                for retrieved_ref in citation["retrievedReferences"]:
                    citation_marker = f"[{citation_num}]"
                    output_text = output_text[:end_span + num_citation_chars] + citation_marker + output_text[end_span + num_citation_chars:]
                    citation_locs = citation_locs + "\n<br>" + citation_marker + " " + retrieved_ref["location"]["s3Location"]["uri"]
                    citation_num += 1
                    num_citation_chars += len(citation_marker)
                output_text = output_text[:end_span + num_citation_chars] + "\n" + output_text[end_span + num_citation_chars:]
                num_citation_chars += 1
            output_text = output_text + "\n" + citation_locs

        # Display the assistant's response
        placeholder.markdown(f"🤖 **ScoutBot:** {output_text}", unsafe_allow_html=True)

        # Save response in session state to maintain chat history
        st.session_state.messages.append({"role": "assistant", "content": output_text})
        st.session_state.citations = response["citations"]
        st.session_state.trace = response["trace"]

# Additional sidebar feature for citations
with st.sidebar:
    st.subheader("Citations")
    if len(st.session_state.citations) > 0:
        citation_num = 1
        for citation in st.session_state.citations:
            for retrieved_ref_num, retrieved_ref in enumerate(citation["retrievedReferences"]):
                with st.expander("Citation [" + str(citation_num) + "]", expanded=False):
                    citation_str = json.dumps({
                        "generatedResponsePart": citation["generatedResponsePart"],
                        "retrievedReference": citation["retrievedReferences"][retrieved_ref_num]
                    }, indent=2)
                    st.code(citation_str, language="json")
                citation_num += 1
    else:
        st.text("None")
