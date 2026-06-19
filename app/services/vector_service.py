import os
from pinecone import Pinecone

class VectorService:
    def __init__(self):
        self.pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
        self.index = self.pc.Index(os.getenv("PINECONE_INDEX_NAME"))

    def get_embedding(self, text: str) -> list[float]:
        # Connect to your preferred embedding model (e.g., OpenAI text-embedding-3-small)
        # Returns a vector of floats
        pass

    def find_similar_safe_clause(self, scanned_clause: str) -> str:
        query_vector = self.get_embedding(scanned_clause)
        
        # Query Pinecone for the standard, low-risk version of this clause
        results = self.index.query(vector=query_vector, top_k=1, include_metadata=True)
        
        if results and results['matches']:
            return results['matches'][0]['metadata']['clause_text']
        return "No standard template clause found."
