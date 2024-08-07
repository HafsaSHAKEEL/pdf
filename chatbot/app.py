import os
from datetime import datetime
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from advancedsearch.advanced_search import AdvancedSearch
from autosearch.indexer import Indexer
from chatbot.pdf_viewer import extract_text_from_pdf

app = FastAPI()

# Initialize Indexer and AdvancedSearch with the directory where PDFs are stored
indexer = Indexer(pdf_directory="pdf")
advancedsearch = AdvancedSearch(pdf_directory="pdf")


@app.get("/")
def read_root():
    """
    Root endpoint to check if the API is running.

    :return: Welcome message as a JSON response.
    """
    return {"message": "Welcome to the OwlEyes Backend API"}


@app.get("/list_pdfs")
def get_pdfs():
    """
    Endpoint to list all PDF files in the specified directory.

    :return: JSON response containing a list of PDF filenames.
    :raises HTTPException: If there's an error listing PDFs.
    """
    try:
        pdf_list = os.listdir("pdf")
        return JSONResponse(content=pdf_list)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/pdfs/{file_name}")
def get_pdf(file_name: str):
    """
    Endpoint to retrieve the text content of a specific PDF file.

    :param file_name: Name of the PDF file to retrieve.
    :return: JSON response containing the file name and its text content.
    :raises HTTPException: If the PDF file is not found or there's an error retrieving the PDF.
    """
    try:
        pdf_path = os.path.join("pdf", file_name)
        if not os.path.exists(pdf_path):
            raise HTTPException(status_code=404, detail="PDF not found")

        text = extract_text_from_pdf(pdf_path)
        return {"file_name": file_name, "content": text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/search")
def search_documents(query: str = Query(..., min_length=1), file_name: Optional[str] = None):
    """
    Endpoint to search for a query string within the PDFs. Optionally search within a specific file.

    :param query: Search query string.
    :param file_name: Optional filename to restrict the search to a specific PDF.
    :return: JSON response containing the search query and results.
    :raises HTTPException: If the file is not found or there's an error during the search.
    """
    try:
        results = indexer.search(query, file_name)
        return {"query": query, "results": results}
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/autocomplete")
def autocomplete(query: str = Query(..., min_length=1)):
    """
    Endpoint to provide autocomplete suggestions for a given query string.

    :param query: Autocomplete query string.
    :return: JSON response containing the query and autocomplete suggestions.
    :raises HTTPException: If there's an error providing autocomplete suggestions.
    """
    try:
        suggestions = indexer.autocomplete(query)
        return {"query": query, "suggestions": suggestions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/alternative_search")
def alternative_search(query: str = Query(..., min_length=1)):
    """
    Endpoint to provide alternative search results based on the query.

    :param query: The search query string.
    :return: JSON response containing the alternative search results.
    :raises HTTPException: If there's an error providing alternative search results.
    """
    try:
        alternative_results = indexer.alternative_search_results(query)
        return {
            "query": query,
            "alternative_results": alternative_results
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
    Endpoint to perform an advanced search with various filters.

    :param beforeDate: End date for the effective date range (format: YYYY-MM-DD).
    :param afterDate: Start date for the effective date range (format: YYYY-MM-DD).
    :param parties: List of parties to search for.
    :param clauses: List of clauses to search for.
    :param terms: List of terms to search for.
    :param companies: List of companies to search for.
    :param divisions: List of divisions to search for.
    :param mentionedNames: List of mentioned names to search for.
    :param mentionedSignatures: List of mentioned signatures to search for.
    :param mentionedWitnesses: List of mentioned witnesses to search for.
    :param dealTypes: List of deal types to search for.
    :param page: Page number for pagination (default is 1).
    :param page_size: Number of results per page (default is 10).
    :return: JSON response containing paginated advanced search results.
    :raises HTTPException: If there's an error performing the advanced search.
    """
    try:

        before_date = datetime.strptime(beforeDate, "%Y-%m-%d").date() if beforeDate else None
        after_date = datetime.strptime(afterDate, "%Y-%m-%d").date() if afterDate else None

        # Combine all search terms and remove empty strings
        all_terms = set(parties + clauses + terms + companies + divisions +
                        mentionedNames + mentionedSignatures + mentionedWitnesses + dealTypes)
        all_terms.discard("")

        # Perform search
        results = advancedsearch.search(search_terms=list(all_terms))

        start_index = (page - 1) * page_size  # pagination
        end_index = start_index + page_size
        paginated_results = results[start_index:end_index]

        return {"page": page, "page_size": page_size, "results": paginated_results, "total_results": len(results)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
