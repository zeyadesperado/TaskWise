import os
import fitz  # PyMuPDF

def convert_pdf_to_text(pdf_path):
    """Convert all pages of a text-based PDF to text."""
    text = ""
    doc = fitz.open(pdf_path)
    
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text += page.get_text()
    
    return text

def store_text_in_file(text, output_path):
    """Store the extracted text in a file."""
    with open(output_path, 'w', encoding='utf-8') as file:
        file.write(text.lower())

def convert_file_to_text(file_path):
    """Process the file if it is a PDF and save the extracted text to a file."""
    #print("I AM HERE")
    filename, extension = os.path.splitext(file_path)
    
    if extension.lower() == ".pdf":
        print('Processing document file...')
        text = convert_pdf_to_text(file_path)
        return text
        #output_path = filename + ".txt"
        #store_text_in_file(text, output_path)
        #print(f"Text saved to {output_path}")
    else:
        print('Unsupported file type.')
