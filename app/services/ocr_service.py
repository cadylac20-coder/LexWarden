import io
import re
from pypdf import PdfReader

class OCRService:
    @staticmethod
    async def extract_text(file_bytes: bytes) -> str:
        """
        Parses incoming payload streams. 
        Extracts native digital streams using PyPDF.
        """
        try:
            pdf_file = io.BytesIO(file_bytes)
            reader = PdfReader(pdf_file)
            extracted_pages = []
            
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    extracted_pages.append(text)
            
            full_text = "\n".join(extracted_pages)
            
            if not full_text.strip():
                raise ValueError("Document appears empty or contains unreadable scanned image layers.")
                
            return full_text
        except Exception as e:
            raise RuntimeError(f"OCR Extraction pipeline failure: {str(e)}")

    @staticmethod
    def chunk_text(text: str) -> list[str]:
        """
        Splits clean contract streams cleanly based on structural line spaces 
        and normalizes overlapping fragments.
        """
        # Split by typical legal paragraph boundaries
        paragraphs = re.split(r'\n\s*\n', text)
        cleaned_chunks = []
        
        for para in paragraphs:
            para_clean = para.strip()
            if not para_clean:
                continue
            # Minimize redundant white spacings inside clauses
            para_clean = re.sub(r'\s+', ' ', para_clean)
            if len(para_clean) > 40:  # Avoid single titles or numbers
                cleaned_chunks.append(para_clean)
                
        return cleaned_chunks
