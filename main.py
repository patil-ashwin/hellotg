import json
from config_loader import load_query_config
from azure_helper import (
    extract_intent,
    explain_result,
    store_json_and_embed,
    answer_question_with_context
)
from tg_client import call_describe_ring

# Load query config (mapped by intent)
QUERY_CONFIG = load_query_config()

def main():
    while True:
        prompt = input("\nEnter your prompt (e.g. 'Ask anything') or type 'exit' to quit: ")
        if prompt.lower() == "exit":
            print("Goodbye!")
            break

        intent_data = extract_intent(prompt)
        print("Intent Extracted:", intent_data)

        intent = intent_data.get("intent")
        if not intent or intent not in QUERY_CONFIG:
            print(f"Unknown or unsupported intent: {intent}")
            continue

        config = QUERY_CONFIG[intent]
        query_name = config.get("query_name")
        input_params = config.get("input_params", [])

        # Prepare parameters for TigerGraph query
        tg_args = {param: intent_data.get(param) for param in input_params}
        if not all(tg_args.values()):
            print(f"Missing required input params for query: {input_params}")
            continue

        # Execute TigerGraph query
        tg_result = call_describe_ring(**tg_args)
        print("TG Raw Result:", tg_result)

        # Explain result if required
        explanation = explain_result(tg_result, config)
        print("\nFinal Explanation:\n", explanation)

        # Store for in-memory RAG (follow-up Q&A)
        #store_json_and_embed(tg_result, intent)

        # Q&A loop for follow-ups
        #while True:
            #question = input("\nAsk a follow-up question about this result (or type 'exit' to go back to main prompt): ")
            #if question.lower() == "exit":
                #break
            #answer = answer_question_with_context(question, intent)
            #print("Answer:", answer)

if __name__ == "__main__":
    main()
