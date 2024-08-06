import os
import sqlite3

def create_database():
    """
    Create an SQLite database and a table for storing PDF files.

    The table is named 'pdfs' and has the following columns:
    - id: An integer primary key that autoincrements.
    - file_name: The name of the PDF file.
    - file_data: The binary data of the PDF file.
    """
    conn = sqlite3.connect('pdf_files.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS pdfs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        file_name TEXT NOT NULL,
        file_data BLOB NOT NULL
    )
    ''')
    conn.commit()
    conn.close()


def insert_pdf(file_path):
    """
    Insert a PDF file into the SQLite database.

    :param file_path: The path to the PDF file.
    """
    with open(file_path, 'rb') as file:
        file_data = file.read()
    conn = sqlite3.connect('pdf_files.db')
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO pdfs (file_name, file_data)
    VALUES (?, ?)
    ''', (os.path.basename(file_path), file_data))
    conn.commit()
    conn.close()


def insert_pdfs_from_directory(pdf_directory):
    """
    Insert all PDF files from the specified directory into the SQLite database.

    :param pdf_directory: The path to the directory containing PDF files.
    """
    if not os.path.exists(pdf_directory):
        print(f"Directory does not exist: {pdf_directory}")
        return

    print(f"Directory exists: {pdf_directory}")

    for file_name in os.listdir(pdf_directory):
        if file_name.endswith('.pdf'):
            file_path = os.path.join(pdf_directory, file_name)
            insert_pdf(file_path)
    print("All PDF files have been inserted into the database.")


if __name__ == "__main__":
    # Use absolute path for the pdf directory
    pdf_directory = '/home/hafsa/PycharmProjects/Air gapped Chatbot /pdf'  # Ensure this path is correct
    create_database()
    insert_pdfs_from_directory(pdf_directory)
