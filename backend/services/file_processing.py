import pandas
import io
import PyPDF2

class FileProcess:
    def __init__(self, file_extension, content):
        self.file_extension = file_extension
        self.content = content
        self.extensions = {
            'pdf': self.process_pdf,
            'xml': self.process_xml,
            'csv': self.process_csv,
            'txt': self.process_txt
        }
        self.process = self.extensions.get(file_extension)

    def get_extensions(self):
        return self.extensions
    
    def process_pdf(self):
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(self.content))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    
    def process_xml(self):
        return self.content.decode('UTF-8')
    
    def process_csv(self):
        csv_string = self.content.decode('UTF-8')
        csv_io = io.StringIO(csv_string)
        result = pandas.read_csv(csv_io)
        return result.to_string(index=False)
    
    def process_txt(self):
        return self.content.decode('UTF-8')
    
    def process_file(self):
        return self.process()
