from dotenv import load_dotenv
load_dotenv()
from RAG import rag_setup, rag_pipeline

run_rag_setup = input("Run RAG Setup (Y/n)\n > ").lower()

overwrite = False

if run_rag_setup == "y":
    overwrite = input("Overwrite ALL Data (Y/n)\n > ").lower()
    overwrite = overwrite == "y"

    rag_setup.setup(overwrite)

rag_pipeline.qa()