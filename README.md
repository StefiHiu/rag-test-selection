# 🔍 RAG-Based Test Case Selection

This project explores **intelligent test case selection** based on recent code changes, using a **Retrieval-Augmented Generation (RAG)** approach.

Instead of manually linking test cases to changed code, this system uses embeddings and a language model to **retrieve and recommend relevant tests** automatically — aiming to reduce unnecessary test runs and accelerate feedback cycles.

---

## 🚀 Project Goals

- Analyze recent code changes (e.g. Git diffs)
- Retrieve relevant test cases using vector search
- Generate smart test selection recommendations with LLM
- Build a modular and extensible proof-of-concept

---

## 📁 Project Structure

```bash
rag-test-selection/
├── data/              # Test cases, code snippets, code diffs
├── embeddings/        # Embedding storage/indexes
├── src/               # Core logic: retriever, generator, pipeline
  ├── retriever.py
  ├── generator.py
  └── main.py
├── README.md          # This file
└── requirements.txt   # Python dependencies
