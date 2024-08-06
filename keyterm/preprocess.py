import os
import logging
import yake
import fitz
from transformers import AutoTokenizer, TFAutoModelForTokenClassification, pipeline
from nltk.corpus import stopwords
from nltk import word_tokenize, pos_tag

import nltk

nltk.download('stopwords')
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class TermExtractionHandler:
    """
    Handles the extraction and ranking of key terms from text using YAKE and NER models.
    """

    def __init__(self):
        """
        Initializes the TermExtractionHandler with necessary models and stopwords.
        """
        self.ner_model = None
        self.tokenizer = None
        self.stop_words = set(stopwords.words('english'))
        self.additional_stopwords = {'date', 'time', 'place', 'address', 'period', 'full', 'terms', 'service',
                                     'parties', 'conditions', 'written', 'notice', 'agreement', 'document', 'will',
                                     'shall', 'in', 'the', 'is', 'to', 'of', 'equal', 'prior', 'condition', 'amounts',
                                     'number', 'days', 'area', 'costs', 'damage', 'company', 'event', 'payment',
                                     'respect', 'tenants', 'whatsoever', 'reason', 'obligations', 'annexure', 'party',
                                     'email', 'charges', 'commencement'}

        self.load_ner_model()

    def load_ner_model(self):
        """
        Loads the NER model and tokenizer.
        """
        self.tokenizer = AutoTokenizer.from_pretrained("dbmdz/bert-large-cased-finetuned-conll03-english")
        self.ner_model = TFAutoModelForTokenClassification.from_pretrained(
            "dbmdz/bert-large-cased-finetuned-conll03-english")

    def extract_key_terms(self, text, max_terms=150):
        """
        Extracts key terms from the provided text using YAKE and NER models.

        :param text: The input text from which to extract key terms.
        :param max_terms: The maximum number of terms to extract.
        :return: A set of filtered key terms.
        """
        logging.info("Extracting keywords using YAKE and NER...")

        # Extract using YAKE
        yake_extractor = yake.KeywordExtractor(lan="en", n=3, dedupLim=0.9, top=max_terms)
        yake_keywords = yake_extractor.extract_keywords(text)
        yake_terms = set(kw.lower() for kw, _ in yake_keywords)
        logging.info(f"YAKE keywords: {yake_terms}")

        # Extract using NER
        ner_pipeline = pipeline("ner", model=self.ner_model, tokenizer=self.tokenizer, aggregation_strategy="simple")
        ner_results = ner_pipeline(text)
        ner_terms = set(result['word'].lower() for result in ner_results if len(result['word'].split()) > 1)
        logging.info(f"NER keywords: {ner_terms}")

        all_terms = yake_terms.union(ner_terms)

        # Further filtering
        filtered_terms = self.filter_terms(all_terms, text)
        logging.info(f"Filtered keywords: {filtered_terms}")
        return filtered_terms

    def filter_terms(self, terms, text):
        """
        Filters the extracted terms to remove stopwords and non-informative terms.

        :param terms: A set of extracted terms.
        :param text: The input text for context.
        :return: A set of filtered and informative key terms.
        """
        logging.info("Filtering terms...")

        # Remove stopwords and short terms
        filtered_terms = {term for term in terms if term not in self.stop_words and len(term) > 2}
        logging.info(f"After stopwords removal: {filtered_terms}")

        # Tokenize and POS tagging
        tokens = word_tokenize(text)
        pos_tags = pos_tag(tokens)
        nouns = {word.lower() for word, pos in pos_tags if pos.startswith('NN')}  # Nouns and proper nouns
        logging.info(f"Nouns: {nouns}")

        # Only keep terms that are nouns or proper nouns
        final_terms = {term for term in filtered_terms if any(word in nouns for word in term.split())}
        logging.info(f"Final terms after noun filtering: {final_terms}")

        # Additional filtering to remove common yet non-informative terms
        final_terms = {term for term in final_terms if
                       not any(stopword in term for stopword in self.additional_stopwords)}
        logging.info(f"Final terms after additional stopwords: {final_terms}")

        # Remove terms with too many common words
        def is_informative(term):
            words = term.split()
            return len(words) > 1 and sum(word in self.additional_stopwords for word in words) <= 1

        informative_terms = {term for term in final_terms if is_informative(term) or len(term.split()) == 1}
        logging.info(f"Informative terms: {informative_terms}")

        # Remove redundant terms and fix repetitions
        unique_terms = set()
        for term in informative_terms:
            if not any(term in other_term and term != other_term for other_term in informative_terms):
                unique_terms.add(term)

        logging.info(f"Unique terms: {unique_terms}")
        return unique_terms

    def extract_and_rank_key_terms(self, text):
        """
        Extracts and ranks key terms from the provided text using YAKE and NER models.

        :param text: The input text from which to extract key terms.
        :return: A list of ranked key terms.
        """
        logging.info("Extracting and ranking key terms...")

        # Extract using YAKE for n-grams
        yake_extractor = yake.KeywordExtractor(lan="en", n=3, dedupLim=0.9, top=150)
        yake_keywords = yake_extractor.extract_keywords(text)
        yake_terms = {kw.lower(): score for kw, score in yake_keywords}

        # Extract using NER
        ner_pipeline = pipeline("ner", model=self.ner_model, tokenizer=self.tokenizer, aggregation_strategy="simple")
        ner_results = ner_pipeline(text)
        ner_terms = {result['word'].lower() for result in ner_results if len(result['word'].split()) > 1}

        # Combine and filter terms
        combined_terms = yake_terms.keys() | ner_terms
        filtered_terms = self.filter_terms(combined_terms, text)

        # Rank terms by their combined relevance score (YAKE score for n-grams and frequency for NER terms)
        term_scores = {term: yake_terms.get(term, 0) for term in filtered_terms}
        ranked_terms = sorted(term_scores, key=term_scores.get, reverse=True)

        logging.info(f"Ranked terms: {ranked_terms}")
        return ranked_terms

    def process_pdfs(self, pdf_directory):
        """
        Processes all PDF files in the specified directory, extracts text, and ranks key terms.

        :param pdf_directory: Path to the directory containing PDF files.
        """
        self.load_ner_model()
        if not os.path.exists(pdf_directory):
            logging.error(f"PDF directory not found: {pdf_directory}")
            return

        for filename in os.listdir(pdf_directory):
            if filename.endswith(".pdf"):
                pdf_path = os.path.join(pdf_directory, filename)
                logging.info(f"Extracting text from {pdf_path}")
                doc = fitz.open(pdf_path)
                text = ""
                for page in doc:
                    text += page.get_text() + "\n"
                doc.close()

                key_terms = self.extract_and_rank_key_terms(text)
                logging.info(f"Extracted terms for {filename}: {key_terms}")
                print(f"Extracted terms for {filename}:")
                for term in key_terms:
                    print(term)


if __name__ == "__main__":
    pdf_directory = "../pdf"  # Adjust this path as needed
    handler = TermExtractionHandler()
    handler.process_pdfs(pdf_directory)
