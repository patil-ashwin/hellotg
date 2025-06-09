import json
import numpy as np
from langchain.chat_models import AzureChatOpenAI
from langchain.embeddings import OpenAIEmbeddings
from langchain.schema import HumanMessage, SystemMessage
from config import (
    AZURE_ENDPOINT,
    AZURE_DEPLOYMENT,
    AZURE_API_KEY,
    AZURE_API_VERSION,
    AZURE_EMBEDDING_API_KEY,
    AZURE_EMBEDDING_API_VERSION,
    AZURE_EMBEDDING_DEPLOYMENT,
)

# Map of intent → [snippets, vectors]
_context_store = {}

# LangChain LLM and Embedding setup
llm = AzureChatOpenAI(
    openai_api_base=AZURE_ENDPOINT,
    openai_api_version=AZURE_API_VERSION,
    deployment_name=AZURE_DEPLOYMENT,
    openai_api_key=AZURE_API_KEY,
    openai_api_type="azure",
    temperature=0.3
)

embedder = OpenAIEmbeddings(
    deployment=AZURE_EMBEDDING_DEPLOYMENT,  # exact embedding deployment name, e.g. "text-embedding-ada-002"
    openai_api_base=AZURE_ENDPOINT,        # just the base resource endpoint
    openai_api_key=AZURE_EMBEDDING_API_KEY,
    openai_api_version=AZURE_EMBEDDING_API_VERSION,  # e.g. "2023-05-15"
    openai_api_type="azure"
)


# 1. INTENT EXTRACTION
def extract_intent(prompt):
    system_prompt = '''You are an intent extractor. Given a prompt, return ONLY a compact JSON like:
{"intent": "ring_explanation", "ring_id": "12345"}'''
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=prompt)
    ]
    response = llm(messages).content
    print("[Azure] Intent raw response:", response)
    try:
        return json.loads(response)
    except Exception as e:
        print("Intent extraction failed:", e)
        return {"intent": None}

# 2. EXPLANATION GENERATOR (based on config)
def explain_result(tg_json, config):
    explanation_type = config.get("explanation_type", "custom")
    if explanation_type == "custom":
        return _custom_explanation(tg_json, config)
    elif explanation_type == "free":
        return "No specific explanation prompt configured. You can ask your own questions based on the context."
    else:
        return f"Unsupported explanation type: {explanation_type}"

def _custom_explanation(tg_json, config):
    sys_prompt = "\n".join(config.get("custom_prompt", [])).strip()
    if not sys_prompt:
        return "Missing custom prompt in config."

    messages = [
        SystemMessage(content=sys_prompt),
        HumanMessage(content=f"Explain this fraud ring detection result:\n{json.dumps(tg_json)}")
    ]
    return llm(messages).content

# 3. CONTEXT FLATTENER
def flatten_json_to_snippets(data: dict, intent: str = "") -> list[str]:
    snippets = []

    # TigerGraph responses often wrap data in a top-level "results" list
    if "results" in data and isinstance(data["results"], list):
        data = _merge_results(data["results"])

    for key, entities in data.items():
        if not isinstance(entities, list):
            continue
        for idx, item in enumerate(entities):
            parts = []
            # Use "v_type" and "v_id" if available
            if "v_type" in item:
                parts.append(f"{item['v_type']} (id: {item.get('v_id')})")
            elif "v_id" in item:
                parts.append(f"Entity ID: {item['v_id']}")
            else:
                parts.append(f"{key} [{idx}]")

            # Include attributes
            attributes = item.get("attributes", {})
            for attr_key, attr_val in attributes.items():
                if isinstance(attr_val, list):
                    parts.append(f"{attr_key}: {', '.join(map(str, attr_val))}")
                else:
                    parts.append(f"{attr_key}: {attr_val}")

            snippets.append(" | ".join(parts))

    return snippets

def _merge_results(results_list: list[dict]) -> dict:
    merged = {}
    for entry in results_list:
        for k, v in entry.items():
            if isinstance(v, list):
                merged.setdefault(k, []).extend(v)
            else:
                merged[k] = v
    return merged

# 4. STORE JSON + EMBEDDINGS
def store_json_and_embed(tg_result, intent):
    global _context_store
    print(f"\n[RAG] Flattening and embedding context for intent: {intent}")

    snippets = flatten_json_to_snippets(tg_result, intent)
    print(f"[RAG] Generated {len(snippets)} text snippets from TigerGraph result.")

    if len(snippets) == 0:
        print("[RAG][Warning] No context snippets generated — check tg_result content.")
        return

    try:
        print("[RAG] Sending first snippet to embedder for test:")
        print("Sample snippet:", snippets[0][:300] + "..." if len(snippets[0]) > 300 else snippets[0])

        vectors = embedder.embed_documents(snippets)
        print("[RAG] Embedding generation succeeded.")
    except Exception as e:
        print(f"[Embedding Error] Failed to generate embeddings:\n{str(e)}")
        print(f"[Embedding Error] Deployment: {embedder.deployment}")
        print(f"[Embedding Error] API Base: {embedder.openai_api_base}")
        print(f"[Embedding Error] API Version: {embedder.openai_api_version}")
        return

    _context_store[intent] = {
        "snippets": snippets,
        "vectors": [np.array(v) for v in vectors]
    }
    print(f"[RAG] Successfully stored {len(snippets)} embedded context snippets.")



# 5. SIMILARITY RETRIEVAL
def cosine_similarity(v1, v2):
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

def retrieve_top_k_snippets(question, intent, k=3):
    context = _context_store.get(intent)
    if not context:
        return []

    q_emb = np.array(embedder.embed_query(question))
    sims = [cosine_similarity(q_emb, s_emb) for s_emb in context["vectors"]]
    top_indices = np.argsort(sims)[-k:][::-1]
    return [context["snippets"][i] for i in top_indices]

# 6. FOLLOW-UP Q&A
def answer_question_with_context(question, intent):
    if intent not in _context_store:
        return "No context loaded for this intent. Please run a main query first."

    top_snippets = retrieve_top_k_snippets(question, intent)
    if not top_snippets:
        return "No relevant information found."

    context = "\n".join(top_snippets)
    messages = [
        SystemMessage(content="You are a helpful fraud assistant. Use the context to answer the user's question."),
        HumanMessage(content=f"Context:\n{context}\n\nQuestion: {question}")
    ]
    return llm(messages).content
