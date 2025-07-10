from git import Repo
import os
import json
from dotenv import load_dotenv

def get_environment_config():
    """
    Determine the current environment (GitHub Actions or local) and load the API key and event payload if available.
    Returns:
        Tuple[str, dict or None]: (api_key, github_event)
            - api_key: The API key from .env file or GitHub Secrets.
            - github_event: Parsed GitHub event JSON if running in GitHub Actions, otherwise None.
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

def detect_changes(repo_path="."):
    """
    Detect changes in the git repository compared to HEAD.
    
    Args:
        repo_path (str): Path to the git repository. Defaults to current directory.
    """
    # Initialize the repository
    repo = Repo(repo_path)
    # Check if the repository is bare
    if repo.bare:
        print("No git repository found.")
        return
    
    # Get the event path from environment variables
    _, event = get_environment_config()

    if event:
        # Running in GitHub Actions
        # Extract the before and after SHA from the event
        before_sha = event["before"]
        after_sha = event["after"]
        print(f"GitHub Actions detected: comparing {before_sha}..{after_sha}")
    else:
        # Running locally for testing purposes
        print("Local run: defaulting to HEAD~1..HEAD")
        repo = Repo(".")
        before_sha = repo.commit("HEAD~1").hexsha
        after_sha = repo.head.commit.hexsha
    
    # Determine the commits to compare
    before_commit = repo.commit(before_sha) if before_sha else None
    after_commit = repo.commit(after_sha) if after_sha else None

    # Get the diffs between the two commits
    diffs = before_commit.diff(after_commit, create_patch=True)

    # If there are no diffs, it means no changes have been made
    if not diffs:
        print("No changes detected.")
        return 

    # Collect the diff text from all changes
    print(f"Detected {len(diffs)} changes in the repository:")
    all_diff_texts = []
    report_list = []  # Initialize a list to hold file change descriptions
    for diff in diffs:
        file_path = diff.b_path or diff.a_path
        status = "MODIFIED"  # Default status for modified files
        if diff.new_file:
            status = "NEW"
        if diff.deleted_file:
            status = "DELETED"
        if diff.renamed_file:    
            status = "RENAMED from {diff.rename_from} to {diff.rename_to}"
        report_list.append(f"- {file_path} ({status})")

        print(f"File: {diff.b_path or diff.a_path} - {status}\n")
        # Combine all diffs into a single text
        if isinstance(diff.diff, bytes): # Check if diff is in bytes
            # Decode bytes to string
            diff_text = diff.diff.decode('utf-8', errors='ignore')
        else:
            diff_text = diff.diff
        # Append the diff text to the list
        all_diff_texts.append(diff_text)
    return "\n".join(all_diff_texts), report_list, diffs

if __name__ == "__main__":
    differences = detect_changes()
    print(differences)