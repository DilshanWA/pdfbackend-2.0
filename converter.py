import os
import uuid
import subprocess
from PIL import Image


class Converter:
    def __init__(self, file_manager):
        self.file_manager = file_manager

    def convert_file(self, files):
        filename = files.filename
        name, ext = os.path.splitext(filename)
        ext = ext.lower()

        # Save uploaded file
        filepath = self.file_manager.save_file(files)

        # Run LibreOffice conversion
        command = [
            "soffice",
            "--headless",
            "--convert-to", "pdf",
            filepath,
            "--outdir", self.file_manager.upload_folder
        ]
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode != 0:
            self.file_manager.remove_file(filepath)
            raise RuntimeError(f"Conversion failed for {filename}: {result.stderr.decode()}")

        # LibreOffice output PDF path
        original_pdf = os.path.join(self.file_manager.upload_folder, f"{name}.pdf")
        
        # Generate a unique filename
        unique_pdf_name = f"{name}_{uuid.uuid4().hex}.pdf"
        unique_pdf_path = os.path.join(self.file_manager.upload_folder, unique_pdf_name)

        # Rename the PDF to the unique name
        os.rename(original_pdf, unique_pdf_path)

        # Remove original uploaded file
        self.file_manager.remove_file(filepath)

        return unique_pdf_name

