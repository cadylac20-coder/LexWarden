from pinecone import Pinecone
from google import genai
from google.genai import types
from app.config import settings

class VectorService:
    def __init__(self):
        self.pc = Pinecone(api_key=settings.PINECONE_API_KEY)
        self.index = self.pc.Index(settings.PINECONE_INDEX_NAME)
        self.ai_client = genai.Client(api_key=settings.GEMINI_API_KEY)
        # Production standard embedding model (Output width: 768 dimensions)
        self.embedding_model = "text-embedding-004"

    def get_embedding(self, text: str) -> list[float]:
        try:
            result = self.ai_client.models.embed_content(
                model=self.embedding_model,
                contents=text
            )
            return result.embeddings[0].values
        except Exception as e:
            raise RuntimeError(f"Gemini API calculation vector failure: {str(e)}")

    def find_similar_safe_clause(self, scanned_clause: str) -> str:
        try:
            query_vector = self.get_embedding(scanned_clause)
            results = self.index.query(
                vector=query_vector, 
                top_k=1, 
                include_metadata=True,
                metrics="cosine"
            )
            
            if results and results.get('matches') and len(results['matches']) > 0:
                match = results['matches'][0]
                # Filter out weak contextual matches (Cosine threshold ~0.65)
                if match.get('score', 0) >= 0.65:
                    return match['metadata']['clause_text']
                    
        except Exception as e:
            print(f"Non-fatal Vector indexing read slip: {e}")
            
        return "No explicit matching safe layout baseline found in vector storage."
