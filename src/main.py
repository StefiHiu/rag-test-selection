from src.retriever_google import GoogleEmbeddingRetriever
from data.test_cases import test_cases
from src.retriever import TestCaseRetriever
from src.persistent_retriever import PersistentTestCaseRetriever

# Initialize
google_retriever = GoogleEmbeddingRetriever()
other_retriever = TestCaseRetriever()
persistent_retriever = PersistentTestCaseRetriever(project_name="rag-test-selection")

# Add test cases
google_retriever.add_test_cases(test_cases)
other_retriever.add_test_cases(test_cases)
persistent_retriever.add_test_cases(test_cases)

# Retrieve
query = "The test case retriever was refactored to use a persistent, project-specific ChromaDB store that intelligently syncs test cases by adding, updating, and deleting embeddings."
results = google_retriever.retrieve_test_cases(query)
results2 = other_retriever.retrieve_test_cases(query)
results3 = persistent_retriever.retrieve_test_cases(query)

print("\n🔍 Top matches with Google Embeddings:")
for tid, doc, sim in results:
    print(f"- {tid}: {doc} (similarity: {sim:.2f})")

print("\n🔍 Top matches with Other Embeddings:")
for test_id, doc, score in results2:
    print(f"- {test_id}: {doc} (similarity: {score:.2f})")

print("\n🔍 Top matches with Persistent Embeddings:")
for test_id, doc, score in results3:
    print(f"- {test_id}: {doc} (similarity: {score:.2f})")