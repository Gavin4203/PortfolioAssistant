from RAG import rag_setup
from dotenv import load_dotenv
import os

load_dotenv()

run_rag_setup = input("Run RAG Setup (Y/n)\n > ").lower()

overwrite = False

if run_rag_setup == "y":
    overwrite = input("Overwrite Data (Y/n)\n > ").lower()
    overwrite = overwrite == "y"

rag_setup.setup(overwrite)