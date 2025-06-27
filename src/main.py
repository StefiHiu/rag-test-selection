# src/main.py

from src.retriever import TestCaseRetriever
from data.test_cases import test_cases
from src.generator import generate_response


retriever = TestCaseRetriever()

retriever.add_test_cases(test_cases)

# Simulate a query based on a code change description
query = "Changed logic in login validation"

# Get ranked test cases from Chroma
ranked_chroma = retriever.retrieve_and_rank_from_chroma(query)

recommendation = generate_response(query, ranked_chroma)
print("\n💡 LLM Recommendation:\n")
print(recommendation)

#print("🔎 Top matches:")
#for id, doc, score in ranked_chroma:
#    print(f"- {id}: {doc} (similarity: {score:.2f})")
