import pandas
import io
import PyPDF2

def process_pdf(content: bytes):
    pdf_reader = PyPDF2.PdfReader(io.BytesIO(content))
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

def process_xml(content: bytes):
    return content.decode('UTF-8')

def process_csv(content: bytes):
    csv_string = content.decode('UTF-8')
    csv_io = io.StringIO(csv_string)
    result = pandas.read_csv(csv_io)
    return result.to_string(index=False)

def process_txt(content: bytes):
    return content.decode('UTF-8')