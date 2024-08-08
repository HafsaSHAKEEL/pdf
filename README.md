
# OwlEyes Backend 

## Overview
The OwlEyes Backend  is a service designed to provide robust PDF management and document search capabilities. It includes features for listing, retrieving, and serving PDFs, performing both basic and advanced searches, extracting key terms, saving and retrieving annotations, and collecting user feedback.

## Features
- **List Available PDFs:** Retrieve a list of all PDF files in the specified directory.
- **Retrieve and Serve PDFs:** Download and view individual PDF files.
- **Search Documents:** Perform basic and advanced searches on PDF content.
- **Autocomplete Suggestions:** Provide search query autocomplete suggestions.
- **Extract Key Terms:** Identify and rank key terms from PDF documents.
- **Annotations:** Save and retrieve annotations for specific PDF files.
- **Feedback Collection:** Collect user feedback on search results and document content.

## Setup

### Prerequisites
- Python 3.7+
- Pipenv (recommended for dependency management)

### Installation

1. **Clone the repository:**
    ```sh
    git clone https://github.com/yourusername/owleyes-backend.git
    cd owleyes-backend
    ```

2. **Install dependencies using Pipenv:**
    ```sh
    pipenv install
    ```

3. **Activate the Pipenv shell:**
    ```sh
    pipenv shell
    ```

4. **Run the application:**
    ```sh
    uvicorn chatbot.app:app --reload
    ```

5. **Access the API documentation:**
    Open your browser and navigate to `http://127.0.0.1:8000/docs` to explore the available endpoints and test the API.

## Endpoints

### Root
- `GET /`
  - **Description:** Returns a welcome message.
  - **Response:**
    ```json
    {
      "message": "Welcome to the OwlEyes Backend API"
    }
    ```

### PDF Management
- `GET /list_pdfs`
  - **Description:** List all available PDFs in the specified directory.
  - **Response:**
    ```json
    ["file1.pdf", "file2.pdf", "file3.pdf"]
    ```

- `GET /pdfs/{file_name}`
  - **Description:** Retrieve a specific PDF file.
  - **Parameters:**
    - `file_name` (str): The name of the PDF file to retrieve.
  - **Response:** Serves the requested PDF file.

### Search
- `GET /search`
  - **Description:** Perform a basic search for documents that match the query.
  - **Parameters:**
    - `query` (str): The search query.
    - `file_name` (Optional[str]): The name of the file to search within (if specified).
  - **Response:**
    ```json
    {
      "query": "search term",
      "results": ["result1", "result2", "result3"]
    }
    ```

- `GET /autocomplete`
  - **Description:** Provide autocomplete suggestions for the given query.
  - **Parameters:**
    - `query` (str): The search query.
  - **Response:**
    ```json
    {
      "query": "search term",
      "suggestions": ["suggestion1", "suggestion2", "suggestion3"]
    }
    ```

- `GET /alternative_search`
  - **Description:** Perform an alternative search with pagination.
  - **Parameters:**
    - `query` (str): The search query.
    - `page` (int): The page number for pagination.
    - `page_size` (int): The number of results per page.
  - **Response:**
    ```json
    {
      "query": "search term",
      "alternative_results": ["result1", "result2"],
      "total_results": 20,
      "page": 1,
      "page_size": 10
    }
    ```

- `GET /advanced_search`
  - **Description:** Perform an advanced search with various filters and pagination.
  - **Parameters:** Multiple query parameters for filtering search results.
  - **Response:**
    ```json
    {
      "page": 1,
      "page_size": 10,
      "results": ["result1", "result2"],
      "total_results": 50
    }
    ```

### Key Terms
- `GET /key_terms/{file_name}`
  - **Description:** Extract and rank key terms from a PDF file.
  - **Parameters:**
    - `file_name` (str): The name of the PDF file.
  - **Response:**
    ```json
    {
      "file_name": "example.pdf",
      "key_terms": ["term1", "term2", "term3"]
    }
    ```

### Annotations
- `POST /annotations/{file_name}`
  - **Description:** Save an annotation for a PDF.
  - **Parameters:**
    - `file_name` (str): The name of the PDF file.
    - **Request Body:**
      ```json
      {
        "page_number": 1,
        "text": "Annotation text",
        "coordinates": {"x": 100, "y": 200, "width": 150, "height": 50}
      }
      ```
  - **Response:**
    ```json
    {
      "message": "Annotation saved successfully"
    }
    ```

- `GET /annotations/{file_name}`
  - **Description:** Retrieve annotations for a PDF file.
  - **Parameters:**
    - `file_name` (str): The name of the PDF file.
  - **Response:**
    ```json
    {
      "file_name": "example.pdf",
      "annotations": [{"page_number": 1, "text": "Annotation text", "coordinates": {"x": 100, "y": 200, "width": 150, "height": 50}}]
    }
    ```

### Feedback
- `POST /feedback`
  - **Description:** Save user feedback.
  - **Request Body:**
    ```json
    {
      "query": "search term",
      "response": "search result",
      "rating": 5,
      "comments": "Great search results!"
    }
    ```
  - **Response:**
    ```json
    {
      "message": "Feedback saved successfully"
    }
    ```

## Project Structure

```plaintext
.
├── advancedsearch/
│   └── advanced_search.py
├── autosearch/
│   └── indexer.py
├── chatbot/
│   ├── __init__.py
│   ├── app.py
│   └── pdf_viewer.py
├── database/
│   ├── __init__.py
│   ├── delete_all_pdf.py
│   ├── pdf's_in_db.py
│   └── pdf_files.db
├── keyterm/
│   ├── __init__.py
│   ├── pdf2text.py
│   └── preprocess.py
├── main.py
├── pdf/
│   ├── commercial-lease-agreement-template-2.pdf
│   ├── employment-contract-revised.pdf
│   └── Residential Purchase Agreement.pdf
├── README.md
└── .gitignore
