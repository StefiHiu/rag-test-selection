
import os
import json
import json
import re
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
from langchain_chroma import Chroma
from langchain.schema import Document as LangchainDoc
from data.test_cases import test_cases
from utils.configuration import get_environment_config
from analysis.change_detector import detect_changes

# Load environment variables
load_dotenv()

# Setup LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-pro",
    google_api_key=os.getenv("GEMINI_API_KEY")
)

# Setup embedding and vector store
embedding = GoogleGenerativeAIEmbeddings(
    model="models/embedding-001",  # or another valid model
    google_api_key=os.getenv("GEMINI_API_KEY")
)

vectorstore = Chroma(
    collection_name="test_cases",
    embedding_function=embedding,
    persist_directory="./chroma_langchain"
)

docs = [LangchainDoc(page_content=tc["content"], metadata={"id": tc["id"]}) for tc in test_cases]
vectorstore.add_documents(docs)

# Get the API key and GitHub event payload
_, event = get_environment_config()

    
# Detect changes in the repository, along with the type of changes and commit metadata
print("Detecting changes...")
diff_text, change_description, diffs, commit_metadata = detect_changes(event=event)

# Prompt template
prompt = ChatPromptTemplate.from_template("""
You are a QA expert. Given the following git diff and commit message, summarize the code changes and generate a retrieval query for test selection.

Diff:
{diff}

Commit:
{commit}

Return a JSON like:
{{"developer_summary": "...", "retrieval_query": "..."}}
""")

summarizer_chain = LLMChain(llm=llm, prompt=prompt)
response = summarizer_chain.run({"diff": diff_text, "commit": commit_metadata["message"]})



# Try to extract the JSON between ```json ... ```
json_text_match = re.search(r"```json\n(.*?)```", response, re.DOTALL)
if json_text_match:
    json_text = json_text_match.group(1)
else:
    json_text = response  # fallback if no markdown code block

try:
    data = json.loads(json_text)
    print("Parsed JSON:", data)
    query = data.get("retrieval_query", "")
    print("Retrieval Query:", query)
    print("Developer Summary:", data.get("developer_summary", ""))
except json.JSONDecodeError:
    print("Could not parse JSON. Raw output:")
    print(response)

# Retrieve relevant test cases
if query:
    results_with_scores = vectorstore.similarity_search_with_score(query, k=5)

    print("\n🔍 Relevant Test Cases with Similarity Scores:")
    for doc, score in results_with_scores:
        similarity = 1 - score  # since it's cosine distance
        print(f"- {doc.metadata['id']}: {doc.page_content} (similarity: {similarity:.2f})")

