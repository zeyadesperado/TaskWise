import pytesseract as tess
import os
import fitz  # PyMuPDF
from PIL import Image

# Set the path to Tesseract executable
tess.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"  # Modify this path as needed

def check_file_type(extension):
    """Return the file type based on the extension."""
    if extension.lower() in (".jpg", ".jpeg", ".png", ".gif", ".bmp"):
        return "Image"
    elif extension.lower() in (".pdf", ".txt"):
        return "Document"
    return None

def convert_pdf_to_text(pdf_path):
    """Convert all pages of a PDF to text."""
    text = ""
    doc = fitz.open(pdf_path)
    for i in range(len(doc)):
        page = doc.load_page(i)
        pix = page.get_pixmap(matrix=fitz.Matrix(300/72, 300/72))
        image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        text += tess.image_to_string(image)
    return text

def convert_image_to_text(image_path):
    """Convert an image file to text."""
    img = Image.open(image_path)
    return tess.image_to_string(img)

def store_text_in_file(text, output_path):
    """Store the extracted text in a file."""
    with open(output_path, 'w', encoding='utf-8') as file:
        file.write(text.lower())

def convert_file_to_text(file_path):
    file_path=file_path
    """Determine the file type and process accordingly."""
    filename, extension = os.path.splitext(file_path)
    file_type = check_file_type(extension)
    
    if file_type == "Image":
        print('Processing image file...')
        text = convert_image_to_text(file_path)
    elif file_type == "Document":
        print('Processing document file...')
        text = convert_pdf_to_text(file_path)
    else:
        print('Unsupported file type.')
        return
    return text