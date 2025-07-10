# src/write_report.py

def write_report(file_list, ranked_cases, developer_summary, diffs, commit_metadata, response):
    """
    Write a clean Markdown report about detected changes and recommended test cases.
    """

    # Create formatted list of changed files
    formatted_files = "\n".join(
        f"{line.strip()}" for line in file_list if line.strip()
    )

    # Format suggested test cases
    if ranked_cases:
        formatted_tests = "\n".join(
            f"- {test_id}: {desc} (similarity: {score:.2f})"
            for test_id, desc, score in ranked_cases
        )
    else:
        formatted_tests = "No relevant test cases were suggested."

    # Indent the developer summary for better readability
    indented_summary = "\n".join(
        "  " + line for line in developer_summary.strip().splitlines()
    )

  

    # Compose the Markdown report
    report = f"""📄 **Automated Change Analysis Report**

Detected {len(diffs)} change(s) in the repository:

{formatted_files}

---

🔧 Commit Metadata

    - Author: {commit_metadata['author']}
    - Timestamp: {commit_metadata['timestamp']}
    - Message: {commit_metadata['message']}

---


🔍 Detailed Developer Summary:

{indented_summary}

---

⚡️ Suggested Test Cases to Re-run:

{formatted_tests}

---
💬 Generated Response:
{response}
"""

    # Save report to file
    report_path = "report.md"
    with open(report_path, "w") as f:
        f.write(report)

    print(f"\nReport saved to {report_path}")
