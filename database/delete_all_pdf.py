import sqlite3


def delete_all_pdfs_and_reset():
    # Connect to the SQLite database
    conn = sqlite3.connect('pdf_files.db')
    cursor = conn.cursor()

    # Execute the DELETE statement to remove all records from the pdfs table
    cursor.execute('DELETE FROM pdfs')

    # Reset the AUTOINCREMENT counter for the id column
    cursor.execute('DELETE FROM sqlite_sequence WHERE name="pdfs"')

    # Commit the changes and close the connection
    conn.commit()
    conn.close()
    print("All PDF records have been deleted and ID counter has been reset in the database.")


if __name__ == "__main__":
    delete_all_pdfs_and_reset()
