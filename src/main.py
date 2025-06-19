# src/main.py

from retriever import TestCaseRetriever

retriever = TestCaseRetriever()

# Add some sample test cases
sample_tests = [
    {"id": "TC_001", "content": "Verify login with valid credentials"},
    {"id": "TC_002", "content": "Verify login with invalid password"},
    {"id": "TC_003", "content": "Check logout functionality"},
    {"id": "TC_004", "content": "Ensure password reset works"},
    {"id": "TC_005", "content": "Test session timeout behavior"},
    {"id": "TC_006", "content": "Validate user registration process"},
    {"id": "TC_007", "content": "Check email verification flow"},
    {"id": "TC_008", "content": "Test profile update functionality"},
    {"id": "TC_009", "content": "Verify account deletion process"},
    {"id": "TC_010", "content": "Ensure two-factor authentication works"}
]
query = "Changed logic in login validation"

retriever.add_test_cases(sample_tests)


# Simulate a query based on a code change description

results = retriever.retrieve_and_rank_test_cases(query, sample_tests)

print("Top matching test cases:")
for id, text, score in results:
    print(f"- {id}: {text} (similarity: {score:.2f})")
