# src/write_report.py

def write_report(file_list, ranked_cases, developer_summary, diffs):
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

    # Indent and reformat the developer summary
    # Split into paragraphs (double line breaks) and indent each line
    paragraphs = developer_summary.strip().split("\n\n")
    indented_paragraphs = []
    for para in paragraphs:
        lines = para.strip().splitlines()
        indented_lines = ["  " + line.strip() for line in lines if line.strip()]
        indented_paragraphs.append("\n".join(indented_lines))
    nicely_indented_summary = "\n\n".join(indented_paragraphs)

    # Compose the Markdown report
    report = f"""📄 Automated Change Analysis Report

Detected {len(diffs)} change(s) in the repository:

{formatted_files}

---

Detailed Developer Summary:

{nicely_indented_summary}

---

Suggested Test Cases to Re-run:

{formatted_tests}
"""

    # Save report to file
    report_path = "report.md"
    with open(report_path, "w") as f:
        f.write(report)

    print(f"\nReport saved to {report_path}")
