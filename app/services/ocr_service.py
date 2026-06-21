import io
import re
import logging
from pypdf import PdfReader

logger = logging.getLogger(__name__)

class OCRService:
    @staticmethod
    async def extract_text(file_bytes: bytes, filename: str = "") -> str:
        """
        Extracts text from PDF files.
        Tries native digital extraction first (pypdf).
        Falls back to OCR (pytesseract) for scanned/image-based PDFs.
        Also supports .docx via python-docx.
        """
        ext = filename.lower().split(".")[-1] if filename else "pdf"

        if ext == "docx":
            return OCRService._extract_from_docx(file_bytes)
        else:
            return OCRService._extract_from_pdf(file_bytes)

    @staticmethod
    def _extract_from_pdf(file_bytes: bytes) -> str:
        try:
            pdf_file = io.BytesIO(file_bytes)
            reader = PdfReader(pdf_file)
            pages_text = []

            for page in reader.pages:
                text = page.extract_text()
                if text:
                    pages_text.append(text)

            full_text = "\n".join(pages_text).strip()

            # If native extraction got nothing, fall back to OCR
            if not full_text:
                logger.info("Native PDF text extraction empty — attempting OCR fallback.")
                full_text = OCRService._ocr_pdf(file_bytes)

            if not full_text.strip():
                raise ValueError("Document appears empty or entirely unreadable.")

            return full_text

        except Exception as e:
            raise RuntimeError(f"PDF extraction failure: {str(e)}")

    @staticmethod
    def _ocr_pdf(file_bytes: bytes) -> str:
        """Rasterize PDF pages and OCR them with pytesseract."""
        try:
            from pdf2image import convert_from_bytes
            import pytesseract

            images = convert_from_bytes(file_bytes, dpi=300)
            ocr_pages = []
            for img in images:
                text = pytesseract.image_to_string(img)
                if text.strip():
                    ocr_pages.append(text)
            return "\n".join(ocr_pages)
        except ImportError:
            raise RuntimeError("OCR dependencies not installed. Run: pip install pytesseract pdf2image")
        except Exception as e:
            raise RuntimeError(f"OCR processing error: {str(e)}")

    @staticmethod
    def _extract_from_docx(file_bytes: bytes) -> str:
        """Extract text from Word (.docx) documents."""
        try:
            from docx import Document
            doc = Document(io.BytesIO(file_bytes))
            paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
            return "\n\n".join(paragraphs)
        except ImportError:
            raise RuntimeError("python-docx not installed. Run: pip install python-docx")
        except Exception as e:
            raise RuntimeError(f"DOCX extraction failure: {str(e)}")

    @staticmethod
    def chunk_text(text: str) -> list[str]:
        """
        Splits contract text into clause-level chunks by paragraph boundaries.
        Filters out noise (headings, page numbers, short fragments).
        """
        paragraphs = re.split(r'\n\s*\n', text)
        cleaned_chunks = []

        for para in paragraphs:
            para_clean = para.strip()
            if not para_clean:
                continue
            para_clean = re.sub(r'\s+', ' ', para_clean)
            if len(para_clean) > 40:
                cleaned_chunks.append(para_clean)

        return cleaned_chunks
