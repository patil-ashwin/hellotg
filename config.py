# config.py
TG_HOST = "localhost"
TG_PORT = "14240"
TG_GRAPH_NAME = "FraudDetection"
TG_TOKEN = "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJ0aWdlcmdyYXBoIiwiaWF0IjoxNzQ5MDU5NDc3LCJleHAiOjE3NDk2NjQyODIsImlzcyI6IlRpZ2VyR3JhcGgifQ.hwcj-7HApByXeZEXB3lfa-F-nUHylYrcw37yVLd3Vao"
USE_TG_AUTH = True

AZURE_ENDPOINT = "https://patil-mbi99o78-eastus2.cognitiveservices.azure.com/"
AZURE_DEPLOYMENT = "gpt-4.1"
AZURE_API_KEY = "9qfNQERyWxRxjIr9uZJlezlPxhqHdEgW4BA25e1JpvqO3uLJ9ATcJQQJ99BFACHYHv6XJ3w3AAAAACOGxT0M"
AZURE_API_VERSION = "2024-12-01-preview"

# Embedding Deployment
AZURE_EMBEDDING_DEPLOYMENT = "text-embedding-ada-002"
AZURE_EMBEDDING_API_VERSION = "2023-05-15"
#AZURE_EMBEDDING_URL = f"{AZURE_ENDPOINT}openai/deployments/{AZURE_EMBEDDING_DEPLOYMENT}/embeddings?api-version={AZURE_EMBEDDING_API_VERSION}"
AZURE_EMBEDDING_API_KEY = "9qfNQERyWxRxjIr9uZJlezlPxhqHdEgW4BA25e1JpvqO3uLJ9ATcJQQJ99BFACHYHv6XJ3w3AAAAACOGxT0M"