# src/retriever_google.py

import chromadb
import chromadb.utils.embedding_functions as embedding_functions
import os

class GoogleEmbeddingRetriever:
    def __init__(self):
        """
        Initialize ChromaDB collection with Google Generative AI Embeddings.
        """
        # Create embedding function
        self.google_ef = embedding_functions.GoogleGenerativeAiEmbeddingFunction(
            api_key=os.getenv("API_KEY")
        )

        # Initialize Chroma client
        self.client = chromadb.Client()

        # Create or get collection using Google embedding function
        self.collection = self.client.get_or_create_collection(
            name="test_cases_google",
            embedding_function=self.google_ef
        )

    def add_test_cases(self, test_cases):
        """
        Add test cases to ChromaDB.
        """
        ids = [case["id"] for case in test_cases]
        contents = [case["content"] for case in test_cases]

        # Add documents (embedding is auto-generated)
        self.collection.add(
            ids=ids,
            documents=contents,
            metadatas=[{"id": id_} for id_ in ids]
        )

    def retrieve_test_cases(self, query, similarity_threshold=0.6, max_results=20):
        """
        Retrieve relevant test cases from ChromaDB.
        """
        results = self.collection.query(
            query_texts=[query],
            n_results=max_results,
            include=["documents", "distances", "metadatas"]
        )

        matches = []
        for doc, dist, meta in zip(results["documents"][0], results["distances"][0], results["metadatas"][0]):
            similarity = 1 - dist
            if similarity >= similarity_threshold:
                matches.append((meta["id"], doc, similarity))

        # Sort descending by similarity
        matches.sort(key=lambda x: x[2], reverse=True)
        return matches
