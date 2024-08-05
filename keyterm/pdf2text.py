import os
import logging
import fitz  # PyMuPDF

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

def extract_text_from_pdf(pdf_path):
    """
    Extract text from a PDF file.

    Args:
        pdf_path (str): The path to the PDF file.

    Returns:
        str: The extracted text from the PDF.
    """
    try:
        logging.info(f"Extracting text from {pdf_path}")
        doc = fitz.open(pdf_path)
        text = ""
        for page in doc:
            text += page.get_text() + "\n"
        doc.close()
        return text
    except Exception as e:
        logging.error(f"Error extracting text from {pdf_path}: {e}")
        return ""
