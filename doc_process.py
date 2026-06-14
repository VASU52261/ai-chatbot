import fitz  # PyMuPDF
from bs4 import BeautifulSoup
import docx
import os

def extract_text_from_document(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    
    try:
        if ext == '.txt':
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
                
        elif ext == '.pdf':
            doc = fitz.open(file_path)
            text = ""
            for page in doc:
                text += page.get_text()
            return text
            
        elif ext in ['.htm', '.html']:
            with open(file_path, 'r', encoding='utf-8') as f:
                soup = BeautifulSoup(f, 'html.parser')
                return soup.get_text(separator='\n')
                
        elif ext == '.docx':
            doc = docx.Document(file_path)
            return "\n".join([paragraph.text for paragraph in doc.paragraphs])
            
        else:
            return f"Unsupported file type: {ext}"
    except Exception as e:
        return f"Error extracting text: {e}"
