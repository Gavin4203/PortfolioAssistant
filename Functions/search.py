from RAG.pipeline import user_db
from langchain_core.tools import tool

@tool
def search_query(query: str):
    """
    Queries the user's portfolio database for factual details on their background, projects, skills, and work history.

    Args:
        query: A short, 3-to-5 word technical search phrase (e.g., "C# ASP.NET projects", "backend development and Python").
    """

    # LlamaIndex will embed, search, and generate a response here
    response = user_db.search_portfolio(query)

    return str(response)