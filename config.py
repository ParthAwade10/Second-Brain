import os
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
if not ANTHROPIC_API_KEY:
    raise ValueError("ANTHROPIC_API_KEY not found in .env file")

client = Anthropic(api_key=ANTHROPIC_API_KEY)

CLAUDE_MODEL = "claude-sonnet-4-20250514"

QDRANT_HOST = "localhost"
QDRANT_PORT = 6333
COLLECTION_NAME = "second_brain"

CHUNK_SIZE = 512
CHUNK_OVERLAP = 50
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

TOP_K_DENSE = 10
TOP_K_SPARSE = 10
TOP_K_RERANK = 5