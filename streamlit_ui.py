import streamlit as st
from config_loader import load_query_config
from azure_helper import extract_intent, explain_result
from tg_client import call_describe_ring

QUERY_CONFIG = load_query_config()

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

def process_prompt():
    prompt = st.session_state.input_value
    if not prompt.strip():
        return

    intent_data = extract_intent(prompt)
    st.session_state.chat_history.append({"user": prompt})

    intent = intent_data.get("intent")
    if not intent or intent not in QUERY_CONFIG:
        st.session_state.chat_history.append({"bot": f"Unknown or unsupported intent: {intent}"})
    else:
        config = QUERY_CONFIG[intent]
        input_params = config.get("input_params", [])
        tg_args = {param: intent_data.get(param) for param in input_params}

        if not all(tg_args.values()):
            st.session_state.chat_history.append({"bot": f"Missing required input params for query: {input_params}"})
        else:
            tg_result = call_describe_ring(**tg_args)
            explanation = explain_result(tg_result, config)
            #st.session_state.chat_history.append({"bot": f"TG Raw Result:\n{tg_result}"})
            st.session_state.chat_history.append({"bot": f"\n{explanation}"})

    # Clear input after processing
    st.session_state.input_value = ""

st.title("Bart OpenAI Assistant")

# Text input with callback to process and clear input safely
st.text_input(
    "Enter your prompt (e.g. 'Ask anything')",
    key="input_value",
    on_change=process_prompt
)

# Display chat history
for chat in st.session_state.chat_history:
    if "user" in chat:
        st.markdown(f"**You:** {chat['user']}")
    if "bot" in chat:
        st.markdown(f"**Assistant:** {chat['bot']}")
