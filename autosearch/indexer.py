import os
import fitz
import logging
import re
from collections import defaultdict, Counter
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class Indexer:
    def __init__(self, pdf_directory):
        """
        Initialize the Indexer with a directory containing PDF files.

        :param pdf_directory: Directory where the PDF files are stored.
        """
        self.pdf_directory = pdf_directory
        self.index = defaultdict(list)
        self.words = set()
        self.ngrams = Counter()
        self.stopwords = {"the", "on", "with", "for", "and", "of", "or", "as", "at", "in", "by", "to", "its", "from",
                          "such", "this", "any", "date", "a", "is", "all", "that", "an", "above"}
        self.build_index()

    def build_index(self):
        """
        Build an index from PDF files in the specified directory.
        """
        logging.info("Building index from PDFs...")
        for filename in os.listdir(self.pdf_directory):
            if filename.endswith(".pdf"):
                pdf_path = os.path.join(self.pdf_directory, filename)
                try:
                    doc = fitz.open(pdf_path)
                    text = ""
                    for page in doc:
                        text += page.get_text("text") + "\n"
                    doc.close()

                    words = re.findall(r'\b\w+\b', text.lower())
                    self.words.update(words)
                    self.index_document(filename, words)
                    logging.info(
                        f"Indexed terms for {filename}: {words[:100]}")  # Display the first 100 terms for brevity
                    logging.info(
                        f"Indexed n-grams for {filename}: {list(self.ngrams.keys())[:100]}")  # Display the first 100 n-grams for brevity
                except Exception as e:
                    logging.error(f"Error indexing file {filename}: {str(e)}")
        logging.info(f"Index built with {len(self.words)} unique words.")
        logging.info(f"Sample indexed words: {list(self.words)[:50]}")

    def index_document(self, filename, words):
        """
        Index the words from a document.

        :param filename: Name of the file being indexed.
        :param words: List of words extracted from the document.
        """
        logging.info(f"Indexing words from file: {filename}")
        for i in range(len(words)):
            unigram = words[i]
            self.ngrams[(unigram,)] += 1
            self.index[unigram].append(filename)
            if i < len(words) - 1:
                bigram = (words[i], words[i + 1])
                self.ngrams[bigram] += 1
            if i < len(words) - 2:
                trigram = (words[i], words[i + 1], words[i + 2])
                self.ngrams[trigram] += 1
        logging.info(
            f"Indexed unigrams: {[unigram for unigram in self.ngrams.keys() if len(unigram) == 1][:100]}")  # Display the first 100 unigrams
        logging.info(
            f"Indexed bigrams: {[bigram for bigram in self.ngrams.keys() if len(bigram) == 2][:100]}")  # Display the first 100 bigrams
        logging.info(
            f"Indexed trigrams: {[trigram for trigram in self.ngrams.keys() if len(trigram) == 3][:100]}")  # Display the first 100 trigrams

    def search(self, query, filename=None):
        """
        Search for query terms in the indexed documents.

        :param query: Search query string.
        :param filename: Optional filename to restrict the search to a specific PDF.
        :return: List of search results with filenames and match percentages.
        :raises FileNotFoundError: If the specified file is not found.
        """
        query_terms = query.lower().split()
        document_matches = defaultdict(int)

        if filename:
            if not os.path.exists(os.path.join(self.pdf_directory, filename)):
                raise FileNotFoundError(f"File {filename} not found in directory.")
            pdf_files = [filename]
        else:
            pdf_files = os.listdir(self.pdf_directory)

        for pdf_file in pdf_files:
            pdf_path = os.path.join(self.pdf_directory, pdf_file)
            doc = fitz.open(pdf_path)
            text = ""
            for page in doc:
                text += page.get_text("text") + "\n"
            doc.close()

            words = re.findall(r'\b\w+\b', text.lower())
            for term in query_terms:
                if term in words:
                    document_matches[pdf_file] += 1

        results = []
        for pdf_file, count in document_matches.items():
            if count == len(query_terms):
                match_percentage = (count / len(query_terms)) * 100
                results.append({
                    "file_name": pdf_file,
                    "match_percentage": match_percentage,
                    "matches": self.get_context_matches(pdf_file, query_terms)
                })

        return sorted(results, key=lambda x: x["match_percentage"], reverse=True)

    def get_context_matches(self, filename, query_terms):  # highlight terms that are being found,Handle Tap/Click to
        # Jump to Sections:
        """
        Get context matches for query terms in a specific document.

        :param filename: Name of the file to search.
        :param query_terms: List of query terms to search for.
        :return: List of context matches.
        """
        pdf_path = os.path.join(self.pdf_directory, filename)
        doc = fitz.open(pdf_path)
        text = ""
        for page in doc:
            text += page.get_text("text") + "\n"
        doc.close()

        matches = []
        lines = text.splitlines()

        for i, line in enumerate(lines):
            if any(term in line.lower() for term in query_terms):
                start_idx = max(i - 2, 0)
                end_idx = min(i + 3, len(lines))
                snippet = ' '.join(lines[start_idx:end_idx])
                highlighted_snippet = snippet
                for term in query_terms:
                    highlighted_snippet = highlighted_snippet.replace(term, f"<mark>{term}</mark>")
                matches.append({"context": highlighted_snippet})

        return matches

    def autocomplete(self, query):
        """
        Provide autocomplete suggestions based on the query.

        :param query: Autocomplete query string.
        :return: List of autocomplete suggestions.
        """
        query_lower = query.lower()
        suggestions = set()
        logging.info(f"Query: {query_lower}")
        for ngram in self.ngrams.keys():
            if ' '.join(ngram).startswith(query_lower):
                suggestions.add(' '.join(ngram))
                logging.info(f"Matched ngram: {' '.join(ngram)}")

        # Remove stopwords from suggestions
        suggestions = self.remove_stopwords(suggestions)

        logging.info(f"Autocomplete suggestions for '{query}': {suggestions}")
        return list(suggestions)

    def remove_stopwords(self, suggestions):
        """
        Remove stopwords from the list of suggestions.

        :param suggestions: List of autocomplete suggestions.
        :return: List of suggestions without stopwords.
        """
        return [suggestion for suggestion in suggestions if
                not any(stopword in suggestion.split() for stopword in self.stopwords)]

    def alternative_search_results(self, query):
        """
        Provide alternative search results based on the query.

        :param query: Search query string.
        :return: List of alternative search results with filenames and match percentages.
        """
        query_terms = query.lower().split()
        match_counts = defaultdict(int)
        matched_files = set()

        for term in query_terms:
            if term in self.index:
                matched_files.update(self.index[term])

        results = []
        for filename in matched_files:
            match_percentage = sum(
                1 for term in query_terms if term in self.index and filename in self.index[term]) / len(
                query_terms) * 100
            results.append({
                "file_name": filename,
                "match_percentage": match_percentage
            })

        return sorted(results, key=lambda x: x["match_percentage"], reverse=True)


if __name__ == "__app__":
    pdf_directory = "/mnt/data"
    indexer = Indexer(pdf_directory)
    logging.info("Indexing complete.")
