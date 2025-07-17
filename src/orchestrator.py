from pathlib import Path
import sys
# Ensure parent folder is in sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))  

from analysis.change_detector import detect_changes
from data.test_cases import test_cases
from src.generator import generate_response
from analysis.gemini_summarizer import summarize_diff_gemini
from src.write_report import write_report
from utils.configuration import get_environment_config, load_llm, get_retriever



def main():
    # Set the project name
    project_name = "rag-test-selection"

    # Get the API key and GitHub event payload
    api_key, event = get_environment_config()

    # Load the LLM model
    model = load_llm(api_key)
    
    # Detect changes in the repository, along with the type of changes and commit metadata
    print("Detecting changes...")
    diff_text, change_description, diffs, commit_metadata = detect_changes(event=event)

    if not diff_text.strip():
        print("No changes detected. Exiting.")
        return

    print("\nSummarizing the detected changes...")
    summaries = summarize_diff_gemini(
        diff_text, 
        commit_message=commit_metadata["message"], 
        model=model
        )
    # Extract the developer summary and retrieval query from the summaries
    developer_summary = summaries["developer_summary"]
    retrieval_query = summaries["retrieval_query"]

    # Print the summaries to the console
    print("\nDeveloper Summary:")
    print(developer_summary)
    print("\nRetrieval Query for test case selection:")
    print(retrieval_query)

    # Initialize the retriever
    # use "persistent" for the persistent retriever, "google" for the Google embedding retriever,
    # or leave it as None for the default retriever
    print("\nInitializing retriever...")
    retriever = get_retriever(project_name=project_name, type="persistent")

    print("\nAdding test cases to embedding store...")
    retriever.add_test_cases(test_cases)

    print("\nRetrieving relevant test cases from ChromaDB...")
    ranked_tests = retriever.retrieve_test_cases(
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
    response = generate_response(
        query=retrieval_query, 
        retrieved_test_cases=ranked_tests, 
        model=model
        )
    print("\nGenerated Response:")
    print(response)

    print("\nWriting report...")
    write_report(project_name, change_description, ranked_tests, developer_summary, diffs, commit_metadata, response)


if __name__ == "__main__":
    main()
    
