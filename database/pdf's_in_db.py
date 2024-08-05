import os
import sqlite3


# Step 2: Create SQLite Database and Table
def create_database():
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


# Step 3: Function to Insert PDF into Database
def insert_pdf(file_path):
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


# Step 4: Insert All PDFs from the Directory
def insert_pdfs_from_directory(pdf_directory):
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
