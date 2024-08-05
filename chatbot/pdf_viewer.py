# pdf_viewer.py
import os
from fastapi.responses import FileResponse, PlainTextResponse
from fastapi import HTTPException
import fitz

def list_all_pdfs():
    pdf_directory = "pdf"
    if not os.path.exists(pdf_directory):
        raise HTTPException(status_code=404, detail="PDF directory not found.")
    pdf_files = [f for f in os.listdir(pdf_directory) if f.endswith('.pdf')]
    return {"pdf_files": pdf_files}

def serve_pdf(file_name, as_text=False):
    pdf_directory = "pdf"
    pdf_path = os.path.join(pdf_directory, file_name)
    if not os.path.exists(pdf_path):
        raise HTTPException(status_code=404, detail="PDF file not found.")
    if as_text:
        doc = fitz.open(pdf_path)
        text = ""
        for page in doc:
            text += page.get_text() + "\n"
        doc.close()
        return PlainTextResponse(content=text)
    else:
        return FileResponse(pdf_path)
