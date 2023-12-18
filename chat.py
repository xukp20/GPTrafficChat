"""
    Built with the basic demo of streamlit chat app
"""
import streamlit as st
from gpt import gpt_call, TOKEN_LOG_ENABLE, money_calculator
if TOKEN_LOG_ENABLE:
    from gpt import num_tokens_from_messages, single_text_tokens

import json, time

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
# add scroll bars for temperature, top_p, frequency_penalty, presence_penalty and max_tokens
st.sidebar.subheader("Parameters")
temperature = st.sidebar.slider("Temperature", 0.0, 2.0, 0.0)
top_p = st.sidebar.slider("Top P", 0.0, 1.0, 1.0)
frequency_penalty = st.sidebar.slider("Frequency Penalty", 0.0, 1.0, 0.0)
presence_penalty = st.sidebar.slider("Presence Penalty", 0.0, 1.0, 0.0)
max_tokens = st.sidebar.slider("Max Tokens", 1, 2048, 512)

# three columns
col1, col2, col3 = st.columns(3)
with col1:
    if st.sidebar.button("Clear Chat"):
        st.session_state.messages = []
with col2:
    if st.sidebar.button("Remove last round"):
        if len(st.session_state.messages) >= 2:
            st.session_state.messages = st.session_state.messages[:-2]
with col3:
    if st.sidebar.button("Regenerate"):
        st.session_state.messages = st.session_state.messages[:-1]
        with st.spinner("Thinking..."):
            all_messages = [{
                "role": "system",
                "content": system_prompt
            }] + st.session_state.messages
            print(all_messages)
            with open("last_messages.json", "w") as f:
                f.write(json.dumps(all_messages, indent=4))
            print("Using model: ", st.session_state.openai_model)
            print("Parameters: ", temperature, top_p, frequency_penalty, presence_penalty, max_tokens)
            response = gpt_call(all_messages, model=st.session_state.openai_model,
                max_tokens=max_tokens, temperature=temperature, top_p=top_p,
                frequency_penalty=frequency_penalty, presence_penalty=presence_penalty)
        st.session_state.messages.append({"role": "assistant", "content": response})

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
                f.write(json.dumps(all_messages, indent=4))
            print("Using model: ", st.session_state.openai_model)
            print("Parameters: ", temperature, top_p, frequency_penalty, presence_penalty, max_tokens)
            response = gpt_call(all_messages, model=st.session_state.openai_model,
                max_tokens=max_tokens, temperature=temperature, top_p=top_p,
                frequency_penalty=frequency_penalty, presence_penalty=presence_penalty)

            print(response)
            time_taken = time.time() - start_time
        st.markdown(response)

    status_bar(all_messages, response, time_taken)
    st.session_state.messages.append({"role": "assistant", "content": response})
