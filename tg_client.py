# tg_client.py
import json
# from pyTigerGraph import TigerGraphConnection  # Keep commented out for now
from config import TG_HOST, TG_PORT, TG_TOKEN, USE_TG_AUTH, TG_GRAPH_NAME

def call_describe_ring(ring_id):
    # ===== MOCKED RESPONSE START =====
    with open("mock_response.json", "r") as f:
        #print(f"[MOCK TG] Returning local mock data for ring_id: {ring_id}")
        return json.load(f)
    # ===== MOCKED RESPONSE END =====

    # Uncomment below if switching back to live TG
    # host_url = f"http://{TG_HOST}"
    # conn = TigerGraphConnection(
    #     host=host_url,
    #     graphname=TG_GRAPH_NAME,
    #     restppPort=int(TG_PORT),
    #     useCert=False
    # )
    # if USE_TG_AUTH:
    #     conn.apiToken = TG_TOKEN

    # body = {"ring_id": ring_id}
    # print(f"[TG] Sending request to describe Ring {ring_id}")
    # response = conn.runInstalledQuery("get_full_data", params=body)
    # return response 