import fitz
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from keyterm.preprocess import TermExtractionHandler
from autosearch.indexer import Indexer

app = FastAPI()

term_handler = TermExtractionHandler()
indexer = Indexer(pdf_directory="pdf")


@app.get("/")
def read_root():
    """
    Root endpoint for the API.

    :return: Welcome message.
    """
    return {"message": "Welcome to the OwlEyes Backend API"}


@app.get("/list_pdfs")
def get_pdfs():
    """
    List all PDF files in the specified directory.

    :return: JSON response containing the list of PDF files.
    """
    try:
        pdf_list = os.listdir("pdf")
        return JSONResponse(content=pdf_list)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/pdfs/{file_name}")
def get_pdf(file_name: str, as_text: bool = False):
    """
    Retrieve the specified PDF file. Optionally return its text content.

    :param file_name: The name of the PDF file.
    :param as_text: Whether to return the text content of the PDF.
    :return: JSON response containing the file name and optionally the text content.
    """
    try:
        pdf_path = os.path.join("pdf", file_name)
        if not os.path.exists(pdf_path):
            raise HTTPException(status_code=404, detail="PDF not found")

        if as_text:
            text = extract_text_from_pdf(pdf_path)
            return {"file_name": file_name, "content": text}
        else:
            return {"file_name": file_name}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/extract_keywords/{file_name}")
def extract_keywords(file_name: str):
    """
    Extract and rank keywords from the specified PDF file.

    :param file_name: The name of the PDF file.
    :return: JSON response containing the file name and the extracted keywords.
    """
    try:
        pdf_path = os.path.join("pdf", file_name)
        if not os.path.exists(pdf_path):
            raise HTTPException(status_code=404, detail="PDF not found")

        text = extract_text_from_pdf(pdf_path)
        keywords = term_handler.extract_and_rank_key_terms(text)
        return {"file_name": file_name, "keywords": list(keywords)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/search")
def search_documents(query: str = Query(..., min_length=1)):
    """
    Search for documents that contain the query terms and return results with match percentage and context.

    :param query: The search query string.
    :return: JSON response containing the search results.
    """
    try:
        results = indexer.search(query)
        return {"query": query, "results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/autocomplete")
def autocomplete(query: str = Query(..., min_length=1)):
    """
    Provide autocomplete suggestions based on the query.

    :param query: The partial query string for which to provide suggestions.
    :return: JSON response containing the autocomplete suggestions.
    """
    try:
        suggestions = indexer.autocomplete(query)
        return {"query": query, "suggestions": suggestions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/alternative_search")
def alternative_search(query: str = Query(..., min_length=1)):
    """
    Provide alternative search results based on the query.

    :param query: The search query string.
    :return: JSON response containing the alternative search results.
    """
    try:
        alternative_results = indexer.alternative_search_results(query)
        return {
            "query": query,
            "alternative_results": alternative_results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def extract_text_from_pdf(pdf_path):
    """
    Extract text content from a PDF file.

    :param pdf_path: The path to the PDF file.
    :return: The extracted text content.
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


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
