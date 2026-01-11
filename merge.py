import uuid
from PyPDF2 import PdfMerger
import os

class Merger:
    def __init__(self, file_manager):
        self.file_manager = file_manager

    def merge_pdfs(self, files):
        merger = PdfMerger()
        saved_paths = []
        try:
            for file in files:
                path = self.file_manager.save_file(file)
                merger.append(path)
                saved_paths.append(path)

        
            merged_filename = f"Cloudpdf-merged.pdf"
            merged_path = os.path.join(self.file_manager.upload_folder, merged_filename)
            merger.write(merged_path)
            merger.close()

            for path in saved_paths:
                self.file_manager.remove_file(path)

            return merged_filename
        
        except Exception as e:
            for path in saved_paths:
                self.file_manager.remove_file(path)
            raise e
        
    def merge_pdf_paths(self, pdf_paths, output_path):
        merger = PdfMerger()
        try:
            for path in pdf_paths:
                merger.append(path)
            merger.write(output_path)
            merger.close()
            return output_path
        except Exception as e:
            merger.close()
            raise e
