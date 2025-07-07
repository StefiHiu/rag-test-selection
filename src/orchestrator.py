from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parent.parent))  # Ensure parent folder is in sys.path
from analysis.change_detector import detect_changes
from analysis.summarizer import summarize_diff
from src.retriever import TestCaseRetriever
from data.test_cases import test_cases
from src.generator import generate_response
from analysis.gemini_summarizer import summarize_diff_gemini
from src.write_report import write_report


def main():
    print("Detecting changes...")
    diff_text, report_list, diffs = detect_changes()

    if not diff_text.strip():
        print("No changes detected. Exiting.")
        return

    print("\nSummarizing the detected changes...")
    summaries = summarize_diff_gemini(diff_text)
    developer_summary = summaries["developer_summary"]
    retrieval_query = summaries["retrieval_query"]

    print("\nDeveloper Summary:")
    print(developer_summary)

    print("\nRetrieval Query for test case selection:")
    print(retrieval_query)

    print("\nInitializing retriever...")
    retriever = TestCaseRetriever()

    print("\nAdding test cases to embedding store...")
    retriever.add_test_cases(test_cases)

    print("\nRetrieving relevant test cases from ChromaDB...")
    ranked_tests = retriever.retrieve_and_rank_test_cases(
        query=retrieval_query,
        similarity_threshold=0.5,
        max_results=10
    )

    if not ranked_tests:
        print("\nNo relevant test cases found to re-run for these changes.")
    else:
        print("\nRecommended test cases to re-run based on the changes:")
        for i, (test_id, doc, score) in enumerate(ranked_tests, start=1):
            print(f"{i}. [{test_id}] {doc} (similarity: {score:.2f})")


    print("\nWriting report...")
    write_report(report_list, ranked_tests, developer_summary, diffs)


if __name__ == "__main__":
    main()
