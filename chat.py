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

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("What is up?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = gpt_call(st.session_state.messages, MAX_TOKENS, model=st.session_state.openai_model)
        st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})