# LexWarden
A software capable of analyzing through any legal documents (eg:- NDA, TOS, Vendor Agreements) and aptly assess any and all predatory clauses, unusual liabilities, or non-standard compliance terms found within the concerned documents.
Mainly Utilizes 3 components:
1) OCR - Reads physical, signed legal documents and converts them to clean markdown text chunks.
2) AI - Vector Database and Retrieval-Augmented Generation (RAG). A standard, safe legal templates is embedded into the vector database. When a new contract is scanned, the AI compares the new clauses against the "safe" standard embeddings and uses an LLM to explain why a specific scanned clause is high-risk.
3) Database - 
