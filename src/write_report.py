# src/write_report.py

def write_report(file_list, ranked_cases, developer_summary, diffs):

    if ranked_cases:
        test_case_lines = [
            f"- {tid}: {desc} (similarity: {score:.2f})"
            for tid, desc, score in ranked_cases
        ]
    else:
        test_case_lines = ["No relevant test cases were suggested."]

    # Create Markdown report
    report = f"""
    # 📄 Automated Change Analysis Report

    ✅ **{len(diffs)} change(s) detected in the repository:**

    {chr(10).join(file_list)}

    ---

    ## 📝 Detailed Developer Summary
    {developer_summary if developer_summary else "No detailed summary provided."}

    ---

    ## 🔍 Suggested Test Cases to Re-run
    {chr(10).join(test_case_lines)}
    """

    # Save report to file
    report_path = "report.md"
    with open(report_path, "w") as f:
        f.write(report)
    print(f"\nReport saved to {report_path}")

if __name__ == "__main__":
    write_report()
