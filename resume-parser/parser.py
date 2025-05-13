import io
import pdfminer.converter
import pdfminer.pdfinterp
import pdfminer.pdfpage
import docx
import json
import re

def extract_text_from_pdf(pdf_path):
    """Extracts text from a PDF file."""
    text = ""
    try:
        with open(pdf_path, 'rb') as file:
            rsrcmgr = pdfminer.pdfinterp.PDFResourceManager()
            retstr = io.StringIO()
            codec = 'utf-8'
            laparams = pdfminer.layout.LAParams()
            device = pdfminer.converter.TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
            interpreter = pdfminer.pdfinterp.PDFInterpreter(rsrcmgr, device)
            pagenums = set()
            for page in pdfminer.pdfpage.PDFPage.get_pages(file, pagenums):
                interpreter.process_page(page)
            text = retstr.getvalue()
            device.close()
            retstr.close()
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
    return text

def extract_text_from_docx(docx_path):
    """Extracts text from a DOCX file."""
    text = ""
    try:
        doc = docx.Document(docx_path)
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
    except Exception as e:
         print(f"Error extracting text from DOCX: {e}")
    return text

def extract_information(text):
    """Extracts basic name, email, and phone using regex."""
    name_match = re.search(r"([A-Z][a-z]+(?:\s[A-Z][a-z]+)+)", text)
    name = name_match.group(1) if name_match else None
    email_match = re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}", text)
    email = email_match.group(0) if email_match else None
    phone_match = re.search(r"\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}", text) # Basic US phone format
    phone = phone_match.group(0) if phone_match else None
    skills_match = re.findall(r"#(\w+)", text) # Simple hashtag-based skill extraction

    return {
        "name": name,
        "email": email,
        "phone": phone,
        "skills": skills_match,
        # You'll need to add more regex patterns for experience and education
        "experience": [],
        "education": []
    }

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        if file_path.lower().endswith(".pdf"):
            text = extract_text_from_pdf(file_path)
        elif file_path.lower().endswith(".docx"):
            text = extract_text_from_docx(file_path)
        else:
            print("Unsupported file format. Please provide a PDF or DOCX file.")
            sys.exit(1)

        if text:
            extracted_data = extract_information(text)
            print(json.dumps(extracted_data, indent=2))
        else:
            print("No text extracted from the file.")
    else:
        print("Please provide a file path as a command-line argument.")