import os
import logging
import fitz

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def extract_text_from_pdf(pdf_directory, text_directory):
    """
    Extract text from PDF files in the specified directory and save the extracted text to text files.

    This function processes all PDaF files in the provided directory, extracts the text content from each page,
    and saves the extracted text to a corresponding text file in the specified text directory.

    :param pdf_directory: Path to the directory containing PDF files.
    :param text_directory: Path to the directory where extracted text files will be saved.
    """
    if not os.path.exists(pdf_directory):
        logging.error(f"Error processing {pdf_directory}: no such file or directory.")
        return

    if not os.path.exists(text_directory):
        os.makedirs(text_directory)

    for filename in os.listdir(pdf_directory):
        if filename.endswith(".pdf"):
            pdf_path = os.path.join(pdf_directory, filename)
            text_path = os.path.join(
                text_directory, filename.replace(".pdf", "_text.txt")
            )

            try:
                logging.info(f"Extracting text from {pdf_path}")
                doc = fitz.open(pdf_path)
                text = ""
                for page in doc:
                    text += page.get_text() + "\n"
                doc.close()

                with open(text_path, "w", encoding="utf-8") as text_file:
                    text_file.write(text)
                logging.info(f"Saved extracted text to {text_path}")
            except Exception as e:
                logging.error(f"Error extracting text from {pdf_path}: {e}")
