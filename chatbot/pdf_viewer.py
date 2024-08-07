import os
import fitz
from fastapi import HTTPException
from fastapi.responses import Response


def list_all_pdfs():
    """
    List all PDF files in the specified directory.

    :return: A list of PDF file names.
    :raises HTTPException: If the PDF directory is not found.
    """
    pdf_dir = "pdf"
    if not os.path.exists(pdf_dir):
        raise HTTPException(status_code=404, detail="PDF directory not found")

    pdf_files = [f for f in os.listdir(pdf_dir) if f.endswith(".pdf")]
    return pdf_files


def serve_pdf(file_name: str, as_text: bool = False):
    """
    Serve the specified PDF file. Optionally return its text content.

    :param file_name: The name of the PDF file to serve.
    :param as_text: Whether to return the text content of the PDF.
    :return: If as_text is True, return a dictionary with the file name and text content.
             Otherwise, return the raw PDF content as a Response.
    :raises HTTPException: If the PDF file is not found.
    """
    pdf_path = os.path.join("pdf", file_name)
    if not os.path.exists(pdf_path):
        raise HTTPException(status_code=404, detail="PDF not found")

    if as_text:
        text = extract_text_from_pdf(pdf_path)
        return {"file_name": file_name, "content": text}

    with open(pdf_path, "rb") as f:
        content = f.read()
    return Response(content, media_type="application/pdf")


def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extract text content from a PDF file.

    :param pdf_path: The path to the PDF file.
    :return: The extracted text content.
    :raises HTTPException: If an error occurs while extracting text from the PDF.
    """
    try:
        doc = fitz.open(pdf_path)
        text = ""
        for page in doc:
            text += page.get_text("text") + "\n"
        doc.close()
        return text
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
