from src.retriever_google import GoogleEmbeddingRetriever
from data.test_cases import test_cases
from src.retriever import TestCaseRetriever

# Initialize
google_retriever = GoogleEmbeddingRetriever()
other_retriever = TestCaseRetriever()

# Add test cases
google_retriever.add_test_cases(test_cases)
other_retriever.add_test_cases(test_cases)

# Retrieve
query = "updated checkout process"
results = google_retriever.retrieve_test_cases(query)
resutls2 = other_retriever.retrieve_and_rank_test_cases(query)

print("\n🔍 Top matches with Google Embeddings:")
for tid, doc, sim in results:
    print(f"- {tid}: {doc} (similarity: {sim:.2f})")

print("\n🔍 Top matches with Other Embeddings:")
for test_id, doc, score in resutls2:
    print(f"- {test_id}: {doc} (similarity: {score:.2f})")
