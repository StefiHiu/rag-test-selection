# src/retriever.py

import chromadb
from sentence_transformers import SentenceTransformer


class PersistentTestCaseRetriever:
    def __init__(self, project_name="default"):
        """
        Initialize a persistent ChromaDB collection for a given project.
        Args:
            project_name (str): The name of the project for which to create or load the collection.
        This allows for project-specific storage of test cases.
        """
        
        self.project_name = project_name
        self.client = chromadb.PersistentClient(path=f"./embeddings/{project_name}")
        existing_collections = self.client.list_collections()
        collection_names = [col.name for col in existing_collections]
        # Create or load project-specific collection
        self.collection = self.client.get_or_create_collection(name=project_name, metadata={"hnsw:space": "cosine"})


        if project_name in collection_names:
            print(f"✅ Loaded existing collection: '{project_name}'")
        else:
            print(f"🆕 Created new collection: '{project_name}'")
        
        self.embedding_model = SentenceTransformer("paraphrase-mpnet-base-v2")

    def add_test_cases(self, test_cases):
        """
        Add test cases to the ChromaDB collection, ensuring:
        - New test cases are embedded and added
        - Modified ones are re-embedded
        - Deleted ones are removed
        Args:
            test_cases (list): List of dictionaries with 'id' and 'content' keys.
        """

        print(f"🔄 Syncing test cases with persistent ChromaDB collection '{self.collection.name}'")

        # Get current test case IDs and contents
        current_test_cases = {tc["id"]: tc["content"] for tc in test_cases}
        current_ids = set(current_test_cases.keys())

        # Get existing entries from ChromaDB
        existing_data = self.collection.get(include=["documents", "metadatas"])
        existing_ids = existing_data["ids"]
        existing_docs = existing_data["documents"]

        # Create lookup of current vs existing
        existing_lookup = {id_: doc for id_, doc in zip(existing_ids, existing_docs)}
        existing_ids_set = set(existing_ids)

        # Identify and remove deleted test cases
        to_delete = list(existing_ids_set - current_ids)
        if to_delete:
            print(f"🗑 Removing {len(to_delete)} stale test cases: {to_delete}")
            self.collection.delete(ids=to_delete)

        # Identify new and modified test cases
        to_add = []
        new_ids = []
        new_embeddings = []
        metadatas = []

        for tc_id, content in current_test_cases.items():
            if tc_id not in existing_lookup:
                # New test case
                to_add.append(content)
                new_ids.append(tc_id)
                metadatas.append({"id": tc_id})
            elif existing_lookup[tc_id] != content:
                # Modified test case
                print(f"🔁 Re-embedding modified test case: {tc_id}")
                to_add.append(content)
                new_ids.append(tc_id)
                metadatas.append({"id": tc_id})
                self.collection.delete(ids=[tc_id])  # Remove outdated version

        # Embed and add
        if to_add:
            print(f"➕ Adding {len(to_add)} new/updated test cases")
            new_embeddings = self.embedding_model.encode(to_add, convert_to_numpy=True).tolist()
            self.collection.add(
                ids=new_ids,
                documents=to_add,
                embeddings=new_embeddings,
                metadatas=metadatas
            )
        else:
            print("✅ No new or changed test cases to add.")

    def retrieve_test_cases(self, query, similarity_threshold=0.55, max_results=10):
        query_vec = self.embedding_model.encode([query], convert_to_numpy=True).tolist()[0]
        results = self.collection.query(
            query_embeddings=[query_vec],
            n_results=max_results,
            include=["documents", "distances", "metadatas"]
        )
        
        matches = []
        for doc, dist, metadata in zip(results["documents"][0], results["distances"][0], results["metadatas"][0]):
            similarity = 1 - dist
            if similarity > similarity_threshold:
                matches.append((metadata["id"], doc, similarity))
        return sorted(matches, key=lambda x: x[2], reverse=True)
