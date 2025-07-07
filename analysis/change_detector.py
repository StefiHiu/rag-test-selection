from git import Repo
import os
import json

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
    

    event_path = os.getenv("GITHUB_EVENT_PATH")

    if event_path:
        # Running in GitHub Actions
        with open(event_path, "r") as f:
            event = json.load(f)
        before_sha = event["before"]
        after_sha = event["after"]
        print(f"GitHub Actions detected: comparing {before_sha}..{after_sha}")
    else:
        # Running locally
        print("Local run: defaulting to HEAD~1..HEAD")
        repo = Repo(".")
        before_sha = repo.commit("HEAD~1").hexsha
        after_sha = repo.head.commit.hexsha


    before_commit = repo.commit(before_sha) if before_sha else None
    after_commit = repo.commit(after_sha) if after_sha else None

    diffs = before_commit.diff(after_commit, create_patch=True)
    # Define the head commit and its parent
    head_commit = repo.head.commit
    parent_commit = head_commit.parents[0]

    print("Fetching remote refs...")
    # Fetch the latest changes from the remote repository
    repo.remotes.origin.fetch()

    # Compare origin/main with the current HEAD
    base_commit = repo.commit('origin/main')

    # If there are no parents, it means this is the initial commit
    if not parent_commit:
        print("No parent commit found. This might be the initial commit.")
        return
    
    # Get the diffs between the parent commit and the head commit
    #diffs =parent_commit.diff(head_commit, create_patch=True)
    #diffs = base_commit.diff(head_commit, create_patch=True)

    # If there are no diffs, it means no changes have been made
    if not diffs:
        print("No changes detected.")
        return 

    # Collect the diff text from all changes
    print(f"Detected {len(diffs)} changes in the repository:")
    all_diff_texts = []
    for diff in diffs:
        change_type = [] # Initialize a list to hold change types
        if diff.new_file:
            change_type.append("NEW FILE")
        if diff.deleted_file:
            change_type.append("DELETED FILE")
        if diff.renamed_file:    
            change_type.append(f"RENAMED FILE FROM {diff.rename_from} TO {diff.rename_to}")
        change_desription = ", ".join(change_type) if change_type else "MODIFIED FILE"
    
        print(f"File: {diff.b_path or diff.a_path} - {change_desription}\n")
        # Combine all diffs into a single text
        if isinstance(diff.diff, bytes): # Check if diff is in bytes
            # Decode bytes to string
            diff_text = diff.diff.decode('utf-8', errors='ignore')
        else:
            diff_text = diff.diff
        # Append the diff text to the list
        all_diff_texts.append(diff_text)
    return "\n".join(all_diff_texts)

if __name__ == "__main__":
    differences = detect_changes()
    print(differences)