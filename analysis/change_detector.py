
from datetime import datetime
from utils.configuration import get_repo

def detect_changes(repo_path=".", event=None):
    """
    Detect changes in the git repository compared to HEAD.
    
    Args:
        repo_path (str): Path to the git repository. Defaults to current directory.
        event (GitHub event or None): GitHub event payload if running in GitHub Actions. Defaults to None.
    Returns:
        Tuple of (diff_text, change_description, diffs, commit_metadata)
        - diff_text (str): Combined text of all diffs.
        - change_description (list): List of file changes with their status.
        - diffs (list): List of diff objects.
        - commit_metadata (dict): Metadata of the commit including author, timestamp, and message.
    """
    # Get the repository
    repo = get_repo(repo_path)
    if not repo:
        return

    if event:
        # Running in GitHub Actions
        # Extract the before and after SHA (unique identifier) from the event
        before_sha = event["before"]
        after_sha = event["after"]
        print(f"GitHub Actions detected: comparing {before_sha}..{after_sha}")
    else:
        # Running locally for testing purposes
        print("Local run: defaulting to HEAD~1..HEAD")
        before_sha = repo.commit("HEAD~1").hexsha
        after_sha = repo.head.commit.hexsha
    
    # Determine the commits to compare
    before_commit = repo.commit(before_sha) if before_sha else None
    after_commit = repo.commit(after_sha) if after_sha else None

    # Collect the metadata from the after commit
    if after_commit is not None:
        commit_metadata = {
            "author": after_commit.author.name,
            "timestamp": datetime.fromtimestamp(after_commit.committed_date).strftime("%Y-%m-%d %H:%M:%S"),
            "message": after_commit.message.strip(),
        }

    # Get the diffs between the two commits
    diffs = before_commit.diff(after_commit, create_patch=True)

    # If there are no diffs, it means no changes have been made
    if not diffs:
        print("No changes detected.")
        return 

    # Collect the diff text from all changes
    print(f"Detected {len(diffs)} changes in the repository:")
    all_diff_texts = [] # Initialize a list to hold all diff texts
    change_description = []  # Initialize a list to hold file change descriptions
    for diff in diffs:
        file_path = diff.b_path or diff.a_path
        status = "MODIFIED"  # Default status for modified files
        if diff.new_file:
            status = "NEW"
        elif diff.deleted_file:
            status = "DELETED"
        elif diff.renamed_file:    
            status = "RENAMED from {diff.rename_from} to {diff.rename_to}"
        change_description.append(f"- {file_path} ({status})")

        print(f"File: {diff.b_path or diff.a_path} - {status}\n")
        # Combine all diffs into a single text
        if isinstance(diff.diff, bytes): # Check if diff is in bytes
            # Decode bytes to string
            diff_text = diff.diff.decode('utf-8', errors='ignore')
        else:
            diff_text = diff.diff
        # Append the diff text to the list
        all_diff_texts.append(diff_text)
    return "\n".join(all_diff_texts), change_description, diffs, commit_metadata