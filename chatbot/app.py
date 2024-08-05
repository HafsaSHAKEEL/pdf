
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import sys
import os
import fitz

from chatbot.pdf_viewer import serve_pdf, list_all_pdfs

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from keyterm.preprocess import TermExtractionHandler

from keyterm.pdf2text import extract_text_from_pdf

app = FastAPI()

term_handler = TermExtractionHandler("keyterm/term_extraction_results")

@app.get("/")
def read_root():
    return {"message": "Welcome to the OwlEyes Backend API"}

@app.get("/list_pdfs")
def get_pdfs():
    try:
        pdf_list = list_all_pdfs()
        return JSONResponse(content=pdf_list)
    except HTTPException as e:
        raise e

@app.get("/pdfs/{file_name}")
def get_pdf(file_name: str, as_text: bool = False):
    try:
        return serve_pdf(file_name, as_text=as_text)
    except HTTPException as e:
        raise e

@app.get("/extract_keywords/{file_name}")
def extract_keywords(file_name: str):
    try:
        # Load PDF and extract text
        pdf_path = os.path.join("pdf", file_name)
        doc = fitz.open(pdf_path)
        text = ""
        for page in doc:
            text += page.get_text() + "\n"
        doc.close()

        # Extract keywords
        keywords = term_handler.extract_key_terms(text)

        return {"file_name": file_name, "keywords": list(keywords)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
