import json
import os
from services import bedrock_agent_runtime
import streamlit as st
import uuid
import re

# Get config from environment variables
agent_id = st.secrets["AWS_AGENT_ID"]
agent_alias_id = st.secrets["AWS_ALIAS_ID"]
ui_title = "ScoutBot"
ui_icon = ""

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

# Messages in the conversation
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"], unsafe_allow_html=True)

# Chat input that invokes the agent
if prompt := st.chat_input():
    # Check Prompt for team building, provide additional context
    if re.search(r"\bbuild a team\b", prompt.lower()):
        modified_prompt = (
            prompt 
        + " List exactly 5 players with their respective roles. Each player must be a separate entry, even if their roles are the same."
        + " Do not group players under the same role, list them individually."
        + " Format as follows: (IGL + Role)1. PlayerName , (Role)2. PlayerName , (Role)3. PlayerName , (Role)4. PlayerName  , (Role)5. PlayerName"
        + " Ensure that there are only 5 players given, even if there are multiple players for some roles."
        + " Answer questions about player performance with specific agents (in-game playable characters)."
        + " Include category of agent."
        + " Provide insights on team strategy, strengths, and weaknesses."
        )
    else:
        modified_prompt = prompt

    st.session_state.messages.append({"role": "user", "content": modified_prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        placeholder = st.empty()
        placeholder.markdown("Thinking...")
        response = bedrock_agent_runtime.invoke_agent(
            agent_id,
            agent_alias_id,
            st.session_state.session_id,
            prompt
        )
        output_text = response["output_text"] + " If there are more than 5 players provided, you may choose which to include depending on the type of team you would like to build."

        placeholder.markdown(output_text, unsafe_allow_html=True)

        # Add citations
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
                    citation_num = citation_num + 1
                    num_citation_chars = num_citation_chars + len(citation_marker)
                output_text = output_text[:end_span + num_citation_chars] + "\n" + output_text[end_span + num_citation_chars:]
                num_citation_chars = num_citation_chars + 1
            output_text = output_text + "\n" + citation_locs

        placeholder.markdown(output_text, unsafe_allow_html=True)
        st.session_state.messages.append({"role": "assistant", "content": output_text})
        st.session_state.citations = response["citations"]
        st.session_state.trace = response["trace"]
