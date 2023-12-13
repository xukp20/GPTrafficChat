"""
    Built with the basic demo of streamlit chat app
"""
import streamlit as st
from gpt import gpt_call
MAX_TOKENS=2048

st.title("GPTraffic Chat")

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-4-1106-preview"

if "messages" not in st.session_state:
    st.session_state.messages = []

# Create sidebar for setting prompt
st.sidebar.title("Settings")
system_prompt = st.sidebar.text_area("System Prompt", value="")
if st.sidebar.button("Clear Chat"):
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("What is up?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            all_messages = [{
                "role": "system",
                "content": system_prompt
            }] + st.session_state.messages
            print(all_messages)
            response = gpt_call(all_messages, MAX_TOKENS, model=st.session_state.openai_model)
        st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})
