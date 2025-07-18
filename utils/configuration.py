import os
import json
from dotenv import load_dotenv
import google.generativeai as genai
from git import Repo, InvalidGitRepositoryError
from src.persistent_retriever import PersistentTestCaseRetriever
from src.retriever_google import GoogleEmbeddingRetriever
from src.retriever import TestCaseRetriever

def get_environment_config():
    """
    Determine the current environment (GitHub Actions or local) and load the API key and event payload if available.
    Returns:
        api_key (str): The API key from .env file or GitHub Secrets.
        github_event: Parsed GitHub event JSON if running in GitHub Actions, otherwise None.
    """
    github_event_path = os.getenv("GITHUB_EVENT_PATH")
    # Check if running in GitHub Actions
    if github_event_path:
        # Load the API key from environment variable
        api_key = os.getenv("API_KEY")
        # Load the GitHub event payload
        if os.path.isfile(github_event_path):
            # If the file exists, read it
            with open(github_event_path, "r") as f:
                github_event = json.load(f)
        else:
            # If the file does not exist, return an empty dict
            github_event = None
    else:
        # Running locally, load from .env file
        load_dotenv()  # Load environment variables from .env file
        api_key = os.getenv("GEMINI_API_KEY")
        github_event = None  # No GitHub event in local environment
    return api_key, github_event

def get_retriever(project_name: str, type: str = None):
    """
    Get the appropriate retriever based on the type specified.
    Args:
        project_name (str): The name of the project for the persistent retriever.
        type (str or None): The type of retriever to use. Options are "persistent", "google", or None for in-memory retriever as default.
    Returns:
        retriever: An instance of the appropriate retriever class.
    """
    if type == "persistent":
        retriever = PersistentTestCaseRetriever(project_name=project_name)
    elif type == "google":
        retriever = GoogleEmbeddingRetriever()
    else: # Default to in-memory retriever
        retriever = TestCaseRetriever()
    return retriever

def load_llm(api_key: str) -> genai.GenerativeModel: 
    """
    Load the LLM model with the provided API key.
    Args:
        api_key (str): The API key for the Google Generative AI service.
    Returns:
        model (genai.GenerativeModel): An instance of the GenerativeModel configured with the API key.
    """
    # Configure the Google Generative AI client
    genai.configure(
        api_key=api_key
    )
    # Initialize the model
    model = genai.GenerativeModel(
        model_name="gemini-2.5-pro"
    )
    return model

def get_repo(repo_path=".") -> Repo:
    """
    Get the Git repository at the specified path.

    Args:
        repo_path (str): Path to the git repository. Defaults to current directory.
        github_event (dict or None): GitHub event payload if running in GitHub Actions. Defaults to None.
    Raises:
        InvalidGitRepositoryError: If the specified path is not a valid git repository.
    Returns:
        repo (Repo): An instance of the Git repository.
    """
    try:
        # Initialize the repository
        repo = Repo(repo_path)
        # Check if there are commits in the repository
        if repo.bare:
            print("No git repository found.")
            return None
        return repo
    except InvalidGitRepositoryError:
        print(f"No valid git repository found at {repo_path}.")
        return None
