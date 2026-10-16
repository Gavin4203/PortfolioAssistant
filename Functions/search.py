from RAG.pipeline import pipeline
from langchain_core.tools import tool

user_db = pipeline()

@tool
def search_query(query):
    """
        Searches the user's personal portfolio, resume, and project history.
        Use this ONLY to look up facts about the user's skills, projects, and work experience.
        NEVER use this tool to draft cover letters or search for external company reviews.

        Args:
            query: A specific search phrase (e.g., "Python and backend experience" or "list all software projects")
    """

    # LlamaIndex will embed, search, and generate a response here
    response = user_db.search_portfolio(search_query)

    return str(response)