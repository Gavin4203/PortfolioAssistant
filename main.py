from dotenv import load_dotenv
load_dotenv()
from RAG import rag_setup, rag_pipeline
from LLM import llm_agent

agent = llm_agent.agent()

run_rag_setup = input("Run RAG Setup (Y/n)\n > ").lower()

overwrite = False

if run_rag_setup == "y":
    overwrite = input("Overwrite ALL Data (Y/n)\n > ").lower()
    overwrite = overwrite == "y"

    rag_setup.setup(overwrite)

#rag_pipeline.qa()

def main():
    while True:
        print("--- Your Question Below (Enter '/end' to process input OR '/bye' to exit) ---")

        lines = []
        showSource = False

        while True:
            line = input()

            if line.lower() == '/bye':
                return

            if line.lower() == '/end':
                break

            if line.lower() =='/end-t':
                showSource = True
                break

            lines.append(line)

        q = " ".join(lines)

        #send to langgraph
        agent.speak_to_it(q)

main()