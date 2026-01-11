import uuid
from PyPDF2 import PdfReader, PdfWriter
import os


class Protector:
    def __init__(self, file_manager):
        self.file_manager = file_manager
    
    def protect_pdf(self,file_manager, password):
        path = self.file_manager.save_file(file_manager)
        originalFilename = file_manager.filename.split(".pdf")[0]
        protected_filename = f"{originalFilename}_{uuid.uuid4().hex}_protected_.pdf"
        protected_path = os.path.join(self.file_manager.upload_folder, protected_filename)

        try:
            reader = PdfReader(path)
            writer = PdfWriter()

            for page in reader.pages:
                writer.add_page(page)

            writer.encrypt(password)

            with open(protected_path, "wb") as f:
                writer.write(f)

            self.file_manager.remove_file(path)

            return protected_filename
        except Exception as e:
            self.file_manager.remove_file(path)
            raise e
        
        