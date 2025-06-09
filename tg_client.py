# tg_client.py
import requests, json
from config import TG_HOST, TG_PORT, TG_GRAPH_NAME, TG_TOKEN, USE_TG_AUTH

def call_tigergraph_query(query_name, params):
    url = f"http://{TG_HOST}:{TG_PORT}/query/{TG_GRAPH_NAME}/{query_name}"
    headers = {"Accept": "application/json"}
    if USE_TG_AUTH:
        headers["Authorization"] = f"Bearer {TG_TOKEN}"
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json().get("results", [])
