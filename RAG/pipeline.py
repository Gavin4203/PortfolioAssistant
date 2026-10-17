import sys

import ollama

from langchain_core.tools import tool

from llama_index.core import Settings, SimpleDirectoryReader, VectorStoreIndex, StorageContext
from llama_index.core.base.embeddings.base import similarity
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.vector_stores.qdrant import QdrantVectorStore
from qdrant_client import QdrantClient, models
import os

COLLECTION_NAME = os.environ['COLLECTION_NAME']
QDRANT_DATA = os.environ['QDRANT_DATA']
USER_DATA = os.environ['USER_DATA']

class pipeline:
    def __init__(self):
        # set the models
        #Settings.llm = Ollama(model="llama3.1:8b", request_timeout=120.0)
        Settings.embed_model = OllamaEmbedding(model_name="nomic-embed-text")
        Settings.chunk_size = 512

        # load the qdrant client
        self.client = QdrantClient(path=QDRANT_DATA)
        self.vector_store = QdrantVectorStore(client=self.client, collection_name=COLLECTION_NAME)

        # get qdrant index
        self.index = VectorStoreIndex.from_vector_store(vector_store=self.vector_store)

        # turn the index into a Q&A engine
        self.retriever = self.index.as_retriever(similarity_top_k = 5)

    def search_portfolio(self, query):
        # LlamaIndex will embed, search, and generate a response here
        #returns a Python list of NodeWithScore objects, ordered from highest similarity score to lowest
        response = self.retriever.retrieve(query)
        chunks = "\n\n---\n\n".join([res.get_content() for res in response])

        return (
            f"{chunks}\n\n"
            "--- END OF PORTFOLIO DATA ---\n"
            "Highlight the candidate's real projects above and connect them to the user's request."
        )

    def data_pop(self, overwrite: bool):
        if overwrite:
            if self.client.collection_exists(COLLECTION_NAME):
                self.client.delete_collection(collection_name=COLLECTION_NAME)

        if not self.client.collection_exists(COLLECTION_NAME):
            self.client.create_collection(
                collection_name=os.environ['COLLECTION_NAME'],
                vectors_config=models.VectorParams(size=768, distance=models.Distance.COSINE),
            )

        vector_store = QdrantVectorStore(client=self.client, collection_name=COLLECTION_NAME)

        # define which storage to use
        storage_context = StorageContext.from_defaults(vector_store=vector_store)

        # set dataset
        data_files = SimpleDirectoryReader(USER_DATA).load_data()

        for file in data_files:
            file.id_ = file.metadata["file_path"]

        # load the existing index from Qdrant
        index = VectorStoreIndex.from_vector_store(
            vector_store=vector_store,
            storage_context=storage_context,
        )

        # Compare incoming IDs against the db
        # it will only embed and add files whose paths are not in Qdrant
        # and it will overwrite/update files whose paths are in Qdrant, if said file is re-added
        refresh = index.refresh(data_files)

        print("Files are now stored in Qdrant")

        count_result = self.client.count(collection_name=COLLECTION_NAME, exact=True)

        print(f"Number of elements in Qdrant DB: {count_result.count}")

        self.vector_store = vector_store
        self.index = index
        self.retriever = index.as_retriever(similarity_top_k = 5)


#global instance of pipeline
user_db = pipeline()