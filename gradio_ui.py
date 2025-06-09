import gradio as gr
from config_loader import load_query_config
from azure_helper import extract_intent, explain_result
from tg_client import call_describe_ring

QUERY_CONFIG = load_query_config()

def process_prompt(user_input, history):
    if not user_input.strip():
        return history, history

    intent_data = extract_intent(user_input)
    history.append((user_input, "[Azure] Intent raw response: " + str(intent_data)))

    intent = intent_data.get("intent")
    if not intent or intent not in QUERY_CONFIG:
        bot_reply = f"Unknown or unsupported intent: {intent}"
        history.append((user_input, bot_reply))
        return history, history

    config = QUERY_CONFIG[intent]
    input_params = config.get("input_params", [])
    tg_args = {param: intent_data.get(param) for param in input_params}

    if not all(tg_args.values()):
        bot_reply = f"Missing required input params: {input_params}"
        history.append((user_input, bot_reply))
        return history, history

    tg_result = call_describe_ring(**tg_args)
    explanation = explain_result(tg_result, config)

    bot_reply = f"{explanation}"
    history.append((user_input, bot_reply))
    return history, history


with gr.Blocks() as demo:
    chatbot = gr.Chatbot()
    state = gr.State([])

    with gr.Row():
        user_input = gr.Textbox(
            show_label=False,
            placeholder="Ask about a fraud ring, e.g., 'Explain ring 1234'",
            scale=10
        )
        submit = gr.Button("Submit", scale=2)

    submit.click(fn=process_prompt, inputs=[user_input, state], outputs=[chatbot, state])
    user_input.submit(fn=process_prompt, inputs=[user_input, state], outputs=[chatbot, state])

demo.launch()
