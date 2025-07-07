# analysis/summarizer.py

from openai import OpenAI

# Initialize LM Studio client
client = OpenAI(
    base_url="http://localhost:1234/v1",
    api_key="lm-studio"
)

def summarize_diff(diff_text: str) -> str:
    """
    Summarize a git diff using an LLM.

    Args:
        diff_text (str): The git diff text to summarize.

    Returns:
        str: A short summary describing the changes.
    """
    prompt = (
        "You are an expert software engineer.\n"
        "Given this Git diff, do two things:\n"
        "1. **Developer Summary (Detailed):** Write a clear, detailed explanation of what was changed and why. Use complete sentences and mention affected files and classes.\n\n"
        "2. **Retrieval Query (Concise):** Write a short, information-dense description in one sentence suitable for a retrieval system. This description should be as brief as possible while capturing what changed.\n\n"
        f"Diff:\n{diff_text}\n\n"
        "Return your response exactly in this format, replacing the placeholders with your text:\n\n"
        "DEVELOPER SUMMARY:\n(your detailed description here)\n\n"
        "RETRIEVAL QUERY:\n(your concise description here)\n\n"
    )

    # Call the model
    completion = client.chat.completions.create(
        model="local-model",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        max_tokens=500
    )
    raw_output = completion.choices[0].message.content.strip()
    developer_summary, retrieval_query = parse_summaries(raw_output) 
    
    return {
    "developer_summary": developer_summary,
    "retrieval_query": retrieval_query
    }
    
def parse_summaries(raw_output: str):
    """
    Parse the raw output from the LLM into structured summaries.

    Args:
        raw_output (str): The raw output text from the LLM.

    Returns:
        Tuple[str, str]: (developer_summary, retrieval_query) 
        A tuple containing the detailed developer summary and the concise retrieval query.
    """
    # Split the output into detailed summary and retrieval query
    developer_summary = ""
    retrieval_query = ""

    # Split the output by the marker lines
    parts = raw_output.split("RETRIEVAL QUERY:")

    if len(parts) == 2:
        # First part is everything after "DEVELOPER SUMMARY:" and before "RETRIEVAL QUERY:"
        dev_part = parts[0]
        if "DEVELOPER SUMMARY:" in dev_part:
            developer_summary = dev_part.split("DEVELOPER SUMMARY:")[1].strip()
        else:
            developer_summary = dev_part.strip()
        # Second part is everything after "RETRIEVAL QUERY:"
        retrieval_query = parts[1].strip()
    else:
        # If the format is not as expected, just take the whole output as developer summary
        developer_summary = raw_output.strip()
        retrieval_query = ""

    return developer_summary, retrieval_query
