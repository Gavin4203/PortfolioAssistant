import sys

import ollama
from llama_index.core import Settings, SimpleDirectoryReader, VectorStoreIndex, StorageContext
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.vector_stores.qdrant import QdrantVectorStore
from qdrant_client import QdrantClient, models
import os

COLLECTION_NAME = os.environ['COLLECTION_NAME']
QDRANT_DATA = os.environ['QDRANT_DATA']
USER_DATA = os.environ['USER_DATA']

def qa():
    # set the models
    Settings.llm = Ollama(model="llama3.1:8b", request_timeout=120.0)
    Settings.embed_model = OllamaEmbedding(model_name="nomic-embed-text")
    Settings.chunk_size = 512

    # load the qdrant client
    client = QdrantClient(path=QDRANT_DATA)
    vector_store = QdrantVectorStore(client=client, collection_name=COLLECTION_NAME)

    # get qdrant index
    index = VectorStoreIndex.from_vector_store(vector_store=vector_store)

    # turn the index into a Q&A engine
    query_engine = index.as_query_engine()

    while True:
        print("--- Your Question Below (Enter '/end' to process input OR '/bye' to exit) ---")

        lines = []
        while True:
            line = input()

            if line.lower() == '/bye':
                return

            if line.lower() == '/end':
                break

            lines.append(line)

        q = " ".join(lines)

        # LlamaIndex will embed, search, and generate a response here
        print("\nstarting response generation...\n")
        response = query_engine.query(q)

        print(f"\n--- AI Response ---\n{response}")

        print("\n\n---- AI Sources ----")
        for node in response.source_nodes:
            print(f"- {node.text} \n(Relevance Score: {node.score:.4f})")

        print("\n")