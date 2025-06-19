from sentence_transformers import SentenceTransformer
import chromadb

class TestCaseRetriever:
    def __init__(self):
        # Load the embedding model
        self.embedding_model = SentenceTransformer('paraphrase-mpnet-base-v2')
        # Initialize ChromaDB client
        self.client = chromadb.Client()

        # Get or create the collection to store test case embeddings
        self.collection = self.client.get_or_create_collection(name="test_cases")

    def _prepare_test_data(self, test_cases, return_tensor=False):
        """
        Extract IDs, contents, and embeddings from test cases.

        Args:
            test_cases (list): List of dicts with 'id' and 'content'.
            return_tensor (bool): If True, return tensor embeddings instead of list.

        Returns:
            Tuple of (ids, contents, embeddings)
        """
        ids = [case['id'] for case in test_cases]
        contents = [case['content'] for case in test_cases]
        embeddings = self.embedding_model.encode(
            contents, 
            convert_to_tensor=return_tensor, 
            convert_to_numpy=not return_tensor
        )

        if not return_tensor:
            embeddings = embeddings.tolist()

        return ids, contents, embeddings

    def add_test_cases(self, test_cases):
        """
        Add test cases to the ChromaDB collection.

        Args:
            test_cases (list): List of dictionaries with 'id' and 'content' keys.
        """
        ids, contents, embeddings = self._prepare_test_data(test_cases)

        # Add the test cases to the collection
        self.collection.add(
            ids=ids,
            documents=contents,
            embeddings=embeddings
        )

    def retrieve_and_rank_test_cases(self, query, test_cases, similarity_threshold=0.55):
        """
        Compute similarity between the query and test cases, returning the most relevant ones.
        
        Args:
            query (str): Natural language query describing code changes.
            test_cases (list): List of dictionaries with 'id' and 'content' keys.
            similarity_threshold (float): Minimum similarity score to consider a match.
            
        Returns:
            list of (id, content, similarity) tuples for relevant test cases.
        """
        ids, contents, embeddings = self._prepare_test_data(test_cases)
        query_embedding = self.embedding_model.encode([query], convert_to_numpy=True).tolist()[0]

        # Compute cosine similarity
        similarities = self.embedding_model.similarity(query_embedding, embeddings)
        relevant_cases = [
            (ids[i], contents[i], score.item()) for i, score in enumerate(similarities[0]) if score.item() > 0.55
        ]
        ranked_cases = sorted(relevant_cases, key=lambda x: x[2], reverse=True)
        return ranked_cases
        