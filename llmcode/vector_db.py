from typing import List

import chromadb
from chromadb.config import Settings


class VectorDB:
    def __init__(self, persist_dir: str = ".chromadb"):
        self.client = chromadb.Client(Settings(persist_directory=persist_dir))
        self.collection = self.client.get_or_create_collection("code")

    def add_code_chunk(self, chunk_id: str, code: str, metadata: dict = None):
        self.collection.add(
            documents=[code], ids=[chunk_id], metadatas=[metadata or {}]
        )

    def search(self, query: str, n_results: int = 5) -> List[dict]:
        results = self.collection.query(query_texts=[query], n_results=n_results)
        return results


# Example usage:
# db = VectorDB()
# db.add_code_chunk("file1.py:1-10", "def foo(): ...", {"file": "file1.py"})
# matches = db.search("function to parse arguments")
