# analysis/gemini_summarizer.py

import google.generativeai as genai
import json, re
from analysis.change_detector import get_environment_config


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

def summarize_diff_gemini(diff_text: str) -> str:
    """
    Summarize a git diff using an LLM.

    Args:
        diff_text (str): The git diff text to summarize.

    Returns:
        str: A developer summary which is a detailed explanation of the changes,
              and a retrieval query which is a concise description of the change.
              The retreival query is suitable for retrieval systems.
    """
    prompt = (
        "You are an expert software engineer who wants to use RAG to determine which test cases to re-run based on git diffs.\n\n"
        "Given this git diff:\n\n"
        "```\n"
        f"{diff_text}\n"
        "```\n\n"
        "Please produce a JSON object with **two fields**:\n\n"
        "- \"DEVELOPER SUMMARY\": A clear, detailed summary suitable for a developer.\n"
        "- \"RETRIEVAL QUERY\": A short, focused description of the change and its effects (1-2 sentences), suitable for retrieval.\n\n"
    )

    # Call the model
    completion = model.generate_content(prompt)
    raw_output = completion.text.strip() # Get the raw output text

    # Strip code fences if present
    if raw_output.startswith("```"):
        raw_output = re.sub(r"^```[a-zA-Z]*\n?", "", raw_output)
        raw_output = re.sub(r"\n?```$", "", raw_output).strip()

    # Try to parse the output as JSON first to separate the summaries
    try:
        parsed = json.loads(raw_output)
        dev_summary = parsed.get("DEVELOPER SUMMARY", "").strip()
        retrieval_query = parsed.get("RETRIEVAL QUERY", "").strip()
        
    # If JSON parsing fails, fallback to regex parsing
    except Exception:
        dev_match = re.search(r"DEVELOPER SUMMARY:(.*?)(RETRIEVAL QUERY:|$)", raw_output, re.DOTALL | re.IGNORECASE)
        ret_match = re.search(r"RETRIEVAL QUERY:(.*)", raw_output, re.DOTALL | re.IGNORECASE)

        if not dev_match or not ret_match:
            raise ValueError(f"Could not parse model output:\n{raw_output}")
    
        dev_summary = dev_match.group(1).strip()
        retrieval_query = ret_match.group(1).strip()

    return {
        "developer_summary": dev_summary,
        "retrieval_query": retrieval_query
    }
