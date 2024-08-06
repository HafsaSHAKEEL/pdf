import os
import fitz  # PyMuPDF
import logging
from collections import defaultdict, Counter
import re

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class Indexer:
    def __init__(self, pdf_directory):
        self.pdf_directory = pdf_directory
        self.index = defaultdict(list)
        self.words = set()
        self.ngrams = Counter()
        self.build_index()

    def build_index(self):
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
                except Exception as e:
                    logging.error(f"Error indexing file {filename}: {str(e)}")
        logging.info(f"Index built with {len(self.words)} unique words.")
        logging.info(f"Sample indexed words: {list(self.words)[:50]}")  # Show a sample of the indexed words

    def index_document(self, filename, words):
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

    def search(self, query):
        query_terms = query.lower().split()
        match_counts = defaultdict(int)

        for term in query_terms:
            if term in self.index:
                for filename in self.index[term]:
                    match_counts[filename] += 1

        results = []
        for filename, count in match_counts.items():
            match_percentage = (count / len(query_terms)) * 100
            if match_percentage > 100:
                match_percentage = 100  # Ensure the match percentage does not exceed 100%
            results.append({
                "file_name": filename,
                "match_percentage": match_percentage,
                "matches": self.get_context_matches(filename, query_terms)
            })

        return sorted(results, key=lambda x: x["match_percentage"], reverse=True)

    def get_context_matches(self, filename, query_terms):
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
                matches.append({"context": snippet})

        return matches

    def autocomplete(self, query):
        query_lower = query.lower()
        suggestions = set()
        for ngram in self.ngrams.keys():
            if ' '.join(ngram).startswith(query_lower):
                suggestions.add(' '.join(ngram))

        logging.info(f"Autocomplete suggestions for '{query}': {suggestions}")
        return list(suggestions)

    def alternative_search_results(self, query):
        query_terms = query.lower().split()
        match_counts = defaultdict(int)
        matched_files = set()

        for term in query_terms:
            if term in self.index:
                matched_files.update(self.index[term])

        results = []
        for filename in matched_files:
            match_percentage = sum(1 for term in query_terms if term in self.index and filename in self.index[term]) / len(query_terms) * 100
            results.append({
                "file_name": filename,
                "match_percentage": match_percentage,
                "matches": self.get_context_matches(filename, query_terms)
            })

        return sorted(results, key=lambda x: x["match_percentage"], reverse=True)

if __name__ == "__main__":
    pdf_directory = "../pdf"
    indexer = Indexer(pdf_directory)
    logging.info("Indexing complete.")
