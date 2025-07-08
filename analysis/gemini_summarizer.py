# analysis/gemini_summarizer.py

import google.generativeai as genai
import json, re

# Initialize LM Studio client
model = genai.GenerativeModel(
    model_name="gemini-2.5-pro"
    )
genai.configure(
    api_key=""
    ) 

def summarize_diff_gemini(diff_text: str) -> str:
    """
    Summarize a git diff using an LLM.

    Args:
        diff_text (str): The git diff text to summarize.

    Returns:
        str: A short summary describing the changes.
    """
    prompt = (
        "You are an expert software engineer.\n\n"
        "Given this git diff:\n\n"
        "```\n"
        f"{diff_text}\n"
        "```\n\n"
        "Please produce a JSON object with **two fields**:\n\n"
        "- \"DEVELOPER SUMMARY\": A clear, detailed summary suitable for a developer.\n"
        "- \"RETRIEVAL QUERY\": A short, focused description of the change (1-2 sentences), suitable for retrieval.\n\n"
    )

    # Call the model
    completion = model.generate_content(prompt)
    raw_output = completion.text.strip()

    # Strip code fences if present
    if raw_output.startswith("```"):
        raw_output = re.sub(r"^```[a-zA-Z]*\n?", "", raw_output)
        raw_output = re.sub(r"\n?```$", "", raw_output).strip()

    
    try:
        parsed = json.loads(raw_output)
        return {
            "developer_summary": parsed.get("DEVELOPER SUMMARY", "").strip(),
            "retrieval_query": parsed.get("RETRIEVAL QUERY", "").strip()
        }
    
    except Exception:
        # Fallback to regex parsing
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
