import os
from datetime import datetime
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
from transformers import pipeline, TFGPT2LMHeadModel, AutoTokenizer
from advancedsearch.advanced_search import AdvancedSearch
from autosearch.indexer import Indexer
from chatbot.pdf_viewer import extract_text_from_pdf
from keyterm.preprocess import TermExtractionHandler

app = FastAPI()


indexer = Indexer(pdf_directory="pdf")
advancedsearch = AdvancedSearch(pdf_directory="pdf")
term_extraction_handler = TermExtractionHandler()

# Initialize the Hugging Face transformers pipeline with TensorFlow model
tokenizer = AutoTokenizer.from_pretrained("gpt2")
model = TFGPT2LMHeadModel.from_pretrained("gpt2")
nlp = pipeline("text-generation", model=model, tokenizer=tokenizer)


class Annotation(BaseModel):
    page_number: int
    text: str
    coordinates: Dict[str, Any]


class Feedback(BaseModel):
    query: str
    response: str
    rating: int
    comments: Optional[str] = None


# In-memory database for annotations and feedback
annotations_db = {}
feedback_db = []


@app.get("/")
def read_root():
    """
    Root endpoint that returns a welcome message.

    Returns:
        dict: A welcome message.
    """
    return {"message": "Welcome to the OwlEyes Backend API"}


@app.get("/list_pdfs")
def get_pdfs():
    """
    List all PDF files in the specified directory.

    Returns:
        JSONResponse: A list of PDF file names.
    """
    try:
        pdf_list = os.listdir("pdf")
        return JSONResponse(content=pdf_list)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/pdfs/{file_name}")
def get_pdf(file_name: str):
    """
    Retrieve a PDF file.

    Args:
        file_name (str): The name of the PDF file to retrieve.

    Returns:
        FileResponse: The requested PDF file.
    """
    try:
        pdf_path = os.path.join("pdf", file_name)
        if not os.path.exists(pdf_path):
            raise HTTPException(status_code=404, detail="PDF not found")

        return FileResponse(pdf_path, media_type='application/pdf', filename=file_name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/search")
def search_documents(query: str = Query(..., min_length=1), file_name: Optional[str] = None):
    """
    Search for documents that match the query.

    Args:
        query (str): The search query.
        file_name (Optional[str]): The name of the file to search within (if specified).

    Returns:
        dict: The search query and results.
    """
    try:
        results = indexer.search(query, file_name)
        if not results:
            raise HTTPException(status_code=404, detail="No documents found matching the query.")
        return {"query": query, "results": results}
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/autocomplete")
def autocomplete(query: str = Query(..., min_length=1)):
    """
    Provide autocomplete suggestions for the given query.

    Args:
        query (str): The search query.

    Returns:
        dict: The search query and suggestions.
    """
    try:
        suggestions = indexer.autocomplete(query)
        return {"query": query, "suggestions": suggestions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/alternative_search")
def alternative_search(query: str = Query(..., min_length=1), page: int = Query(1, ge=1),
                       page_size: int = Query(10, ge=1)):
    """
    Perform an alternative search with pagination.

    Args:
        query (str): The search query.
        page (int): The page number for pagination.
        page_size (int): The number of results per page.

    Returns:
        dict: The search query, paginated results, and total results.
    """
    try:
        alternative_results = indexer.alternative_search_results(query)

        # Pagination
        start_index = (page - 1) * page_size
        end_index = start_index + page_size
        paginated_results = alternative_results[start_index:end_index]

        return {
            "query": query,
            "alternative_results": paginated_results,
            "total_results": len(alternative_results),
            "page": page,
            "page_size": page_size
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/advanced_search")
def advanced_search_documents(
        beforeDate: Optional[str] = Query(None,
                                          description="End date for the effective date range (format: YYYY-MM-DD)"),
        afterDate: Optional[str] = Query(None,
                                         description="Start date for the effective date range (format: YYYY-MM-DD)"),
        parties: Optional[List[str]] = Query([], description="Parties to search for"),
        clauses: Optional[List[str]] = Query([], description="Clauses to search for"),
        terms: Optional[List[str]] = Query([], description="Terms to search for"),
        companies: Optional[List[str]] = Query([], description="Companies to search for"),
        divisions: Optional[List[str]] = Query([], description="Divisions to search for"),
        mentionedNames: Optional[List[str]] = Query([], description="Mentioned names to search for"),
        mentionedSignatures: Optional[List[str]] = Query([], description="Mentioned signatures to search for"),
        mentionedWitnesses: Optional[List[str]] = Query([], description="Mentioned witnesses to search for"),
        dealTypes: Optional[List[str]] = Query([], description="Deal types to search for"),
        page: int = Query(1, description="Page number for pagination", ge=1),
        page_size: int = Query(10, description="Number of results per page", ge=1)
):
    """
    Perform an advanced search with various filters and pagination.

    Args:
        beforeDate (Optional[str]): End date for the effective date range.
        afterDate (Optional[str]): Start date for the effective date range.
        parties (Optional[List[str]]): Parties to search for.
        clauses (Optional[List[str]]): Clauses to search for.
        terms (Optional[List[str]]): Terms to search for.
        companies (Optional[List[str]]): Companies to search for.
        divisions (Optional[List[str]]): Divisions to search for.
        mentionedNames (Optional[List[str]]): Mentioned names to search for.
        mentionedSignatures (Optional[List[str]]): Mentioned signatures to search for.
        mentionedWitnesses (Optional[List[str]]): Mentioned witnesses to search for.
        dealTypes (Optional[List[str]]): Deal types to search for.
        page (int): Page number for pagination.
        page_size (int): Number of results per page.

    Returns:
        dict: The paginated search results and total results.
    """
    try:
        before_date = datetime.strptime(beforeDate, "%Y-%m-%d").date() if beforeDate else None
        after_date = datetime.strptime(afterDate, "%Y-%m-%d").date() if afterDate else None

        all_terms = set(parties + clauses + terms + companies + divisions +
                        mentionedNames + mentionedSignatures + mentionedWitnesses + dealTypes)
        all_terms.discard("")

        results = advancedsearch.search(search_terms=list(all_terms))

        start_index = (page - 1) * page_size
        end_index = start_index + page_size
        paginated_results = results[start_index:end_index]

        return {"page": page, "page_size": page_size, "results": paginated_results, "total_results": len(results)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/key_terms/{file_name}")
def get_key_terms(file_name: str):
    """
    Extract and rank key terms from a PDF file.

    Args:
        file_name (str): The name of the PDF file.

    Returns:
        dict: The file name and extracted key terms.
    """
    try:
        pdf_path = os.path.join("pdf", file_name)
        if not os.path.exists(pdf_path):
            raise HTTPException(status_code=404, detail="PDF not found")

        text = extract_text_from_pdf(pdf_path)
        key_terms = term_extraction_handler.extract_and_rank_key_terms(text)
        return {"file_name": file_name, "key_terms": key_terms}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/annotations/{file_name}")
def save_annotation(file_name: str, annotation: Annotation):
    """
    Save an annotation for a PDF file.

    Args:
        file_name (str): The name of the PDF file.
        annotation (Annotation): The annotation to save.

    Returns:
        dict: A success message.
    """
    if file_name not in annotations_db:
        annotations_db[file_name] = []
    annotations_db[file_name].append(annotation.dict())
    return {"message": "Annotation saved successfully"}


@app.get("/annotations/{file_name}")
def get_annotations(file_name: str):
    """
    Retrieve annotations for a PDF file.

    Args:
        file_name (str): The name of the PDF file.

    Returns:
        dict: The file name and its annotations.
    """
    if file_name not in annotations_db:
        raise HTTPException(status_code=404, detail="No annotations found for this file")
    return {"file_name": file_name, "annotations": annotations_db[file_name]}


@app.post("/feedback")
def save_feedback(feedback: Feedback):
    """
    Save user feedback.

    Args:
        feedback (Feedback): The feedback to save.

    Returns:
        dict: A success message.
    """
    feedback_db.append(feedback.dict())
    return {"message": "Feedback saved successfully"}


if __name__ == "__app__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
