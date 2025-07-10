from openai import OpenAI
from analysis.change_detector import get_environment_config
import google.generativeai as genai

# Get the API key from environment variables or GitHub Actions
loaded_api_key, _ = get_environment_config()
# Configure the Google Generative AI client
genai.configure(
    api_key=loaded_api_key
)
# Initialize the model
model = genai.GenerativeModel(
    model_name="gemini-2.5-pro"
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
        f"Please recommend which test cases should be re-executed and explain why each test case was selected."
        f"If there are no relevant test cases, simply state that.\n\n"
    )

    # Call the model
    completion = model.generate_content(prompt)
    raw_output = completion.text.strip() # Get the raw output text

    return raw_output
