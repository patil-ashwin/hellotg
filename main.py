import json
from azure_helper import extract_intent, explain_result
from tg_client import call_tigergraph_query
from rag_helper import build_vectorstore_from_json, query_vectorstore

vectorstore = None

# Load query config
with open("query_config.json") as f:
    all_query_configs = json.load(f)
    QUERY_CONFIG = {conf["intent"]: conf for conf in all_query_configs}

def handle_query(prompt):
    global vectorstore

    # Step 1: Extract intent
    intent_data = extract_intent(prompt)
    intent = intent_data.get("intent")

    if intent not in QUERY_CONFIG:
        print("Unsupported intent or query.")
        return

    # Step 2: Load query metadata
    config = QUERY_CONFIG[intent]
    query_name = config["query_name"]
    input_params = {k: intent_data[k] for k in config.get("input_params", []) if k in intent_data}

    # Step 3: TigerGraph query call
    tg_result_list = call_tigergraph_query(query_name, input_params)

    # Step 4: Use the first result (assumption: single-object return)
    if not tg_result_list:
        print("No results returned from TigerGraph.")
        return
    tg_result = tg_result_list[0]

    # Step 5: Build vectorstore for follow-ups
    vectorstore = build_vectorstore_from_json(tg_result)

    # Step 6: Explanation
    explanation_type = config.get("explanation_type", "freeform")
    system_prompt = "\n".join(config.get("custom_prompt", [])) if explanation_type == "custom" else None
    explanation = explain_result(tg_result, config)

    print("\nResult:\n", explanation)

def follow_up():
    global vectorstore
    question = input("\nFollow-up question: ")
    if vectorstore:
        answer = query_vectorstore(question, vectorstore)
        print("\nAnswer:\n", answer)
    else:
        print("Run a main query first.")

if __name__ == "__main__":
    print("Welcome to BART OpenAI Assistant. Type 'exit' to quit.")
    while True:
        prompt = input("\nEnter your prompt: ")
        if prompt.lower() in ["exit", "quit"]:
            break
        handle_query(prompt)
        while True:
            subq = input("\nDo you have follow-up questions? (yes/no): ")
            if subq.lower() != "yes":
                break
            follow_up()
