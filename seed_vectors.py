import os
import time
from pinecone import Pinecone, ServerlessSpec
from google import genai
from dotenv import load_dotenv

load_dotenv()

# Expanded golden standards — covers all major commercial contract clause types
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
    },
    {
        "id": "std_ip_01",
        "text": "Intellectual Property Ownership: All pre-existing intellectual property of each party remains the sole property of that party. Work product created specifically for and fully funded by Customer under this Agreement shall be considered work-for-hire and assigned to Customer upon full payment. Vendor retains the right to use general knowledge, skills, and experience acquired during performance.",
        "type": "intellectual_property"
    },
    {
        "id": "std_confidentiality_01",
        "text": "Confidentiality: Each party agrees to hold the other party's Confidential Information in strict confidence using at least the same degree of care it uses for its own confidential information, but no less than reasonable care. Confidential Information shall not be disclosed to third parties without prior written consent. This obligation survives termination for a period of three (3) years.",
        "type": "confidentiality"
    },
    {
        "id": "std_governing_law_01",
        "text": "Governing Law and Dispute Resolution: This Agreement shall be governed by and construed in accordance with the laws of the State of Delaware, without regard to conflict of law principles. Any disputes arising under this Agreement shall first be subject to good-faith negotiation for thirty (30) days, followed by binding arbitration under JAMS rules if unresolved.",
        "type": "governing_law"
    },
    {
        "id": "std_data_privacy_01",
        "text": "Data Protection: Each party shall comply with all applicable data protection laws and regulations, including GDPR and CCPA where applicable. Vendor shall implement and maintain appropriate technical and organizational security measures to protect Customer personal data. Data shall not be used for any purpose beyond fulfilling contractual obligations without explicit written consent.",
        "type": "data_privacy"
    },
    {
        "id": "std_noncompete_01",
        "text": "Non-Solicitation: During the term of this Agreement and for a period of twelve (12) months thereafter, neither party shall directly solicit or hire any employee of the other party who was involved in the performance of this Agreement, without prior written consent. This clause does not restrict general public recruitment campaigns.",
        "type": "non_solicitation"
    },
    {
        "id": "std_payment_01",
        "text": "Payment Terms: Customer shall pay all undisputed invoices within thirty (30) days of receipt. Late payments shall accrue interest at the lesser of 1.5% per month or the maximum rate permitted by law. Vendor may suspend services after providing fifteen (15) days written notice of non-payment, without liability.",
        "type": "payment"
    },
    {
        "id": "std_warranty_01",
        "text": "Warranty: Vendor warrants that the services will be performed in a professional and workmanlike manner consistent with industry standards. In the event of a breach of this warranty, Vendor shall, at its option, re-perform the deficient services at no additional charge or refund the fees paid for the deficient services.",
        "type": "warranty"
    },
    {
        "id": "std_force_majeure_01",
        "text": "Force Majeure: Neither party shall be liable for delays or failures in performance resulting from causes beyond their reasonable control, including natural disasters, government actions, war, terrorism, or pandemic events. The affected party shall provide prompt written notice and use commercially reasonable efforts to resume performance as soon as practicable.",
        "type": "force_majeure"
    },
    {
        "id": "std_auto_renewal_01",
        "text": "Term and Renewal: This Agreement shall commence on the Effective Date and continue for an initial term of one (1) year. Thereafter, this Agreement shall automatically renew for successive one-year periods unless either party provides written notice of non-renewal at least sixty (60) days prior to the end of the then-current term.",
        "type": "auto_renewal"
    },
]

def seed_database():
    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    ai_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    index_name = os.getenv("PINECONE_INDEX_NAME", "lexwarden-safe-clauses")
    dimension = 768  # text-embedding-004 output width

    if index_name not in pc.list_indexes().names():
        print(f"Creating Pinecone index: {index_name}...")
        pc.create_index(
            name=index_name,
            dimension=dimension,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1")
        )
        time.sleep(5)

    index = pc.Index(index_name)
    print(f"Seeding {len(GOLDEN_STANDARDS)} golden standard clauses...")

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
        print(f"  ✓ {item['id']} ({item['type']})")

    index.upsert(vectors=vectors_payload)
    print(f"\nSeeding complete. {len(GOLDEN_STANDARDS)} vectors loaded into '{index_name}'.")

if __name__ == "__main__":
    seed_database()
