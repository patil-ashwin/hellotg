# config_loader.py
import json

def load_query_config(path="query_config.json"):
    with open(path, "r") as f:
        config = json.load(f)
    return {entry["intent"]: entry for entry in config}
