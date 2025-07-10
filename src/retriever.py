from sentence_transformers import SentenceTransformer
import chromadb

class TestCaseRetriever:
    def __init__(self):
        # Load the embedding model
        self.embedding_model = SentenceTransformer('paraphrase-mpnet-base-v2')
        # Initialize ChromaDB client
        self.client = chromadb.Client()

        # Get or create the collection to store test case embeddings with cosine similarity
        self.collection = self.client.get_or_create_collection(name="test_cases", metadata={"hnsw:space": "cosine"})

    def prepare_test_data(self, test_cases, return_tensor=False):
        """
        Extract IDs, contents, and embeddings from test cases.

        Args:
            test_cases (list): List of dicts with 'id' and 'content'.
            return_tensor (bool): If True, return tensor embeddings instead of list.

        Returns:
            Tuple of (ids, contents, embeddings)
        """
        # Extract IDs and contents from the test cases
        ids = [case['id'] for case in test_cases]
        contents = [case['content'] for case in test_cases]
        # If no contents are provided, return empty lists
        if not contents:
            print("No test cases provided.")
            return [], [], []
        # Generate embeddings for the contents using the embedding model
        embeddings = self.embedding_model.encode(
            contents, 
            convert_to_tensor=return_tensor, 
            convert_to_numpy=not return_tensor
        )
        # If return_tensor is True, embeddings will be a tensor, otherwise a numpy array
        if not return_tensor:
            embeddings = embeddings.tolist()

        return ids, contents, embeddings

    def add_test_cases(self, test_cases):
        """
        Add test cases to the ChromaDB collection.

        Args:
            test_cases (list): List of dictionaries with 'id' and 'content' keys.
        """
        # Clear the collection before adding new test cases
        if self.collection.count() > 0:
            print(f"Collection '{self.collection.name}' already contains {self.collection.count()} test cases.")
            print("Clearing existing test cases from the collection.")
            # Clear the collection to avoid duplicates
            existing_ids = self.collection.get()['ids']
            if existing_ids:
                self.collection.delete(ids=existing_ids)

        # Prepare the test data
        ids, contents, embeddings = self.prepare_test_data(test_cases)

        # Add the test cases to the collection
        self.collection.add(
            ids=ids,
            documents=contents,
            embeddings=embeddings,
            metadatas=[{"id": id_} for id_ in ids]  # Store IDs as metadata
        )

    def retrieve_and_rank_test_cases(self, query, similarity_threshold=0.5, max_results=20):
        """
        Retrieve and rank test cases directly from ChromaDB using the stored embeddings.

        Args:
            query (str): The natural language query.
            similarity_threshold (float): Minimum similarity to include in results.
            max_results (int): Number of top results to retrieve.

        Returns:
            List of (document, similarity_score) tuples.
        """
        # Embed the query
        query_embedding = self.embedding_model.encode([query], convert_to_numpy=True).tolist()[0]

        # Query ChromaDB
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=max_results,
            include=["documents", "distances", "metadatas"]
        )
        
        # Process results
        documents = results.get("documents", [[]])[0]
        distances = results.get("distances", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]

        matches = []
        for doc, dist, metadata in zip(documents, distances, metadatas):
            similarity = 1 - dist
            if similarity > similarity_threshold:
                matches.append((metadata["id"], doc, similarity))

        # Sort descending by similarity
        return sorted(matches, key=lambda x: x[2], reverse=True)
    
    def get_captcha(self):
        """
        Generate a simple CAPTCHA to verify human interaction for safety.
        
        Returns:
            str: A simple CAPTCHA string.
        """
        import random
        import string
        
        # Generate a random 6-character alphanumeric CAPTCHA
        captcha = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
        return captcha