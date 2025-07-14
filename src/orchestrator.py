from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parent.parent))  # Ensure parent folder is in sys.path
from analysis.change_detector import detect_changes
from src.retriever import TestCaseRetriever
from src.persistent_retriever import PersistentTestCaseRetriever
from data.test_cases import test_cases
from src.generator import generate_response
from analysis.gemini_summarizer import summarize_diff_gemini
from src.write_report import write_report


def main():
    project_name = "rag-test-selection"
    print("Detecting changes...")
    diff_text, report_list, diffs, commit_metadata = detect_changes()

    if not diff_text.strip():
        print("No changes detected. Exiting.")
        return

    print("\nSummarizing the detected changes...")
    summaries = summarize_diff_gemini(diff_text, commit_message=commit_metadata["message"])
    developer_summary = summaries["developer_summary"]
    retrieval_query = summaries["retrieval_query"]

    print("\nDeveloper Summary:")
    print(developer_summary)

    print("\nRetrieval Query for test case selection:")
    print(retrieval_query)

    print("\nInitializing retriever...")
    retriever = PersistentTestCaseRetriever(project_name=project_name)

    print("\nAdding test cases to embedding store...")
    retriever.add_test_cases(test_cases)

    print("\nRetrieving relevant test cases from ChromaDB...")
    ranked_tests = retriever.retrieve_and_rank_test_cases(
        query=retrieval_query,
        max_results=len(test_cases)  # Limit to the number of test cases available
    )

    if not ranked_tests:
        print("\nNo relevant test cases found to re-run for these changes.")
    else:
        print("\nRecommended test cases to re-run based on the changes:")
        for i, (test_id, doc, score) in enumerate(ranked_tests, start=1):
            print(f"{i}. [{test_id}] {doc} (similarity: {score:.2f})")

    print("\nGenerating response for test case selection...")
    response = generate_response(retrieval_query, ranked_tests)
    print("\nGenerated Response:")
    print(response)

    print("\nWriting report...")
    write_report(project_name, report_list, ranked_tests, developer_summary, diffs, commit_metadata, response)


if __name__ == "__main__":
    main()
    
