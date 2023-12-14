"""
    Built with the basic demo of streamlit chat app
"""
import streamlit as st
from gpt import gpt_call, TOKEN_LOG_ENABLE, money_calculator
if TOKEN_LOG_ENABLE:
    from gpt import num_tokens_from_messages, single_text_tokens

import json, time
MAX_TOKENS=2048

st.title("GPTraffic Chat")

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-4-1106-preview"

if "messages" not in st.session_state:
    st.session_state.messages = []

# put a bar for status below the messages and above the input 
def status_bar(input_messages, output_str, time):
    model = st.session_state["openai_model"]
    if TOKEN_LOG_ENABLE:
        input_tokens = num_tokens_from_messages(input_messages, model=model)
        output_tokens = single_text_tokens(output_str, model=model)
        # keep time to 2 decimal places
        time = round(time, 2)
        # calculate money
        money = money_calculator(input_tokens, output_tokens, model=model)
        # to string, if > 0.1, use $, else use 
        if money > 0.1:
            money = "$" + str(round(money, 2))
        else:
            money = str(round(money * 100, 2)) + "¢"

        # token per second, to 2 decimal places
        tps = round(output_tokens / time, 2)

        st.caption("input: {}, output: {}, time: {}s, tps: {}, cost: {}".format(input_tokens, output_tokens, time, tps, money))
    else:
        st.caption(f"time: {round(time, 2)}s")

# Create sidebar for setting prompt
st.sidebar.title("Settings")
# change model
st.sidebar.subheader("Model")
st.session_state.openai_model = st.sidebar.selectbox(
    "Select a model",
    [
        "gpt-4-1106-preview",
        "gpt-3.5-turbo",
    ],
    index=0,
)

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
            start_time = time.time()
            all_messages = [{
                "role": "system",
                "content": system_prompt
            }] + st.session_state.messages
            print(all_messages)
            with open("last_messages.json", "w") as f:
                f.write(json.dumps(all_messages))
            print("Using model: ", st.session_state.openai_model)
            response = gpt_call(all_messages, MAX_TOKENS, model=st.session_state.openai_model)
            print(response)
            time_taken = time.time() - start_time
        st.markdown(response)

    status_bar(all_messages, response, time_taken)
    st.session_state.messages.append({"role": "assistant", "content": response})
