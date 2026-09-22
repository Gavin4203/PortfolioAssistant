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

def setup(overwrite: bool):
    # set the models
    Settings.llm = Ollama(model="llama3.1:8b", request_timeout=120.0)
    Settings.embed_model = OllamaEmbedding(model_name="nomic-embed-text")
    Settings.chunk_size = 512

    # initialize the qdrant client
    client = QdrantClient(path=QDRANT_DATA)

    if overwrite:
        if client.collection_exists(COLLECTION_NAME):
            client.delete_collection(collection_name=COLLECTION_NAME)

    if not client.collection_exists(COLLECTION_NAME):
        client.create_collection(
            collection_name=os.environ['COLLECTION_NAME'],
            vectors_config=models.VectorParams(size=768, distance=models.Distance.COSINE),
        )

    vector_store = QdrantVectorStore(client=client, collection_name=COLLECTION_NAME)

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

    count_result = client.count(collection_name=COLLECTION_NAME, exact=True)

    print(f"Number of elements in Qdrant DB: {count_result.count}")






















def del_item():
    # initialize the qdrant client
    client = QdrantClient(path=QDRANT_DATA)

    vector_store = QdrantVectorStore(client=client, collection_name=COLLECTION_NAME)

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
