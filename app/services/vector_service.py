from pinecone import Pinecone
from google import genai
from app.config import settings
import logging

logger = logging.getLogger(__name__)

class VectorService:
    def __init__(self):
        self.pc = Pinecone(api_key=settings.PINECONE_API_KEY)
        self.index = self.pc.Index(settings.PINECONE_INDEX_NAME)
        self.ai_client = genai.Client(api_key=settings.GEMINI_API_KEY)
        self.embedding_model = "text-embedding-004"  # 768-dim output

    def get_embedding(self, text: str) -> list[float]:
        try:
            result = self.ai_client.models.embed_content(
                model=self.embedding_model,
                contents=text
            )
            return result.embeddings[0].values
        except Exception as e:
            raise RuntimeError(f"Embedding generation failed: {str(e)}")

    def find_similar_safe_clause(self, scanned_clause: str) -> tuple[str, float]:
        """
        Returns (baseline_clause_text, similarity_score).
        Score is 0.0 if no match found above threshold.
        """
        try:
            query_vector = self.get_embedding(scanned_clause)
            # Note: metric is set at index creation time, not at query time
            results = self.index.query(
                vector=query_vector,
                top_k=1,
                include_metadata=True
            )

            if results and results.get('matches') and len(results['matches']) > 0:
                match = results['matches'][0]
                score = match.get('score', 0)
                if score >= 0.65:
                    return match['metadata']['clause_text'], round(score, 4)

        except Exception as e:
            logger.warning(f"Vector query failed (non-fatal): {e}")

        return "No matching safe baseline found in vector store.", 0.0
