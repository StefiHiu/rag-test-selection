from openai import OpenAI

# Initialize the client to talk to LM Studio running locally
client = OpenAI(
    base_url="http://localhost:1234/v1",
    api_key="lm-studio"  # This can be any string
)

def generate_response(query: str, retrieved_test_cases: list) -> str:
    """
    Generates a natural language recommendation of which test cases to re-run,
    based on the retrieved matches and the code change description.

    Args:
        query (str): The natural language description of the code change.
        retrieved_test_cases (list): List of (id, description, similarity) tuples.

    Returns:
        str: The generated response from the language model.
    """
    # Build the formatted list of test cases
    if not retrieved_test_cases:
        cases_text = "No relevant test cases were found."
    else:
        cases_text = "\n".join(
            [
                f"- ID: {tc_id}, Description: {desc}, Similarity: {sim_score:.2f}"
                for tc_id, desc, sim_score in retrieved_test_cases
            ]
        )

    # Construct the prompt
    prompt = (
        f"You are an expert QA engineer.\n"
        f"Given the following code change description:\n\n"
        f"{query}\n\n"
        f"And these relevant test cases with their similarity scores:\n\n"
        f"{cases_text}\n\n"
        f"Please recommend which test cases should be re-executed and explain why."
    )

    # Call the model
    completion = client.chat.completions.create(
        model="local-model",  # This is what LM Studio expects if you didn't rename your model
        messages=[
            {"role": "user", "content": prompt},
        ],
        temperature=0.3
    )

    # Extract the text
    response_text = completion.choices[0].message.content.strip()
    return response_text
