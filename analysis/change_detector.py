from git import Repo
import os

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
    
    head_commit = repo.head.commit
    parent_commit = head_commit.parents[0]

    if not parent_commit:
        print("No parent commit found. This might be the initial commit.")
        return
    
    diffs =parent_commit.diff(head_commit, create_patch=True)

    if not diffs:
        print("No changes detected.")
        return 

    # Collect the diff text from all changes
    print(f"Detected {len(diffs)} changes in the repository:")
    for diff in diffs:
        change_type = []
        if diff.new_file:
            change_type.append("NEW file")
        if diff.deleted_file:
            change_type.append("DELETED file")
        if diff.renamed_file:    
            change_type.append(f"RENAMED file from {diff.rename_from} to {diff.rename_to}")
        change_desription = ", ".join(change_type) if change_type else "MODIFIED file"
    
    print(f"File: {diff.b_path or diff.a_path} - {change_desription}\n")
    if isinstance(diff.diff, bytes):
        diff_text = diff.diff.decode('utf-8', errors='ignore')
    else:
        diff_text = diff.diff
    return diff_text

if __name__ == "__main__":
    differences = detect_changes()
    print(differences)