import os
import fitz
from typing import List


class AdvancedSearch:
    def __init__(self, pdf_directory: str):
        """
        Initialize the AdvancedSearch object with a directory containing PDF files.

        :param pdf_directory: Directory where the PDF files are stored.
        """
        self.pdf_directory = pdf_directory
        self.index = {}

    def build_index(self):
        """
        Build an index of PDF files in the specified directory.
        The index maps filenames to their extracted text content.
        """
        self.index = {}
        for filename in os.listdir(self.pdf_directory):
            if filename.endswith(".pdf"):
                filepath = os.path.join(self.pdf_directory, filename)
                text = self.extract_text_from_pdf(filepath)
                self.index[filename] = text

    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        Extract text content from a PDF file.

        :param pdf_path: Path to the PDF file.
        :return: Extracted text content of the PDF file.
        """
        text = ""
        try:
            with fitz.open(pdf_path) as doc:
                for page in doc:
                    text += page.get_text()
        except Exception as e:
            print(f"Error reading {pdf_path}: {e}")
        return text

    def search(self, search_terms: List[str]) -> List[str]:
        """
        Search for files containing any of the specified search terms.

        :param search_terms: List of terms to search for within the PDF files.
        :return: List of filenames that contain any of the search terms.
        """
        self.build_index()
        results = []

        search_terms_lower = [term.lower() for term in search_terms]  # to handle case sensitive issues

        for filename, text in self.index.items():
            text_lower = text.lower()
            if any(term in text_lower for term in search_terms_lower):
                results.append(filename)

        return results
