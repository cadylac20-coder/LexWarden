import os
import time
from pinecone import Pinecone, ServerlessSpec
from google import genai
from dotenv import load_dotenv

load_dotenv()

def seed_database():
    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    ai_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    index_name = os.getenv("PINECONE_INDEX_NAME", "lexwarden-safe-clauses")

    # text-embedding-004 outputs 768-dimension vectors
    dimension = 768 

    if index_name not in pc.list_indexes().names():
        print(f"Creating Pinecone index mapping array infrastructure: {index_name}...")
        pc.create_index(
            name=index_name,
            dimension=dimension,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1")
        )
        # Give cluster standard boot propagation time buffer
        time.sleep(5)

    index = pc.Index(index_name)

    GOLDEN_STANDARDS = [
        {
            "id": "std_liability_01",
            "text": "Limitation of Liability: Neither party shall be liable for any indirect, incidental, special, exemplary, or consequential damages. Each party's maximum aggregate liability under this agreement shall be strictly capped at the total amount actually paid by customer to vendor in the twelve (12) month period immediately preceding the event giving rise to liability.",
            "type": "liability"
        },
        {
            "id": "std_indemnity_01",
            "text": "Indemnification Mutual: Each party shall defend, indemnify, and hold harmless the other party against third-party claims arising entirely out of gross negligence, willful misconduct, or strict material breach of contract obligations executed by the indemnifying party.",
            "type": "indemnification"
        },
        {
            "id": "std_termination_01",
            "text": "Termination for Cause: Either party may terminate this Agreement immediately upon written notice if the other party materially breaches any provision of this Agreement and fails to cure such breach within thirty (30) days after receipt of specific written tracking notices describing the failure.",
            "type": "termination"
        }
    ]

    print(f"Processing and vectorizing {len(GOLDEN_STANDARDS)} corporate boilerplate standards...")
    
    vectors_payload = []
    for item in GOLDEN_STANDARDS:
        res = ai_client.models.embed_content(
            model="text-embedding-004",
            contents=item["text"]
        )
        vector_values = res.embeddings[0].values
        
        vectors_payload.append({
            "id": item["id"],
            "values": vector_values,
            "metadata": {
                "clause_text": item["text"],
                "clause_type": item["type"]
            }
        })

    index.upsert(vectors=vectors_payload)
    print("Database seeding completed successfully.")

if __name__ == "__main__":
    seed_database()
