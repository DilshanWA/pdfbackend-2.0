import os
import uuid
from PyPDF2 import PdfReader, PdfWriter


class PdfSpliter:
    def __init__(self, file_manager):
        self.file_manager = file_manager

    def split_pdf(self, file):
        input_pdf_path = self.file_manager.save_file(file)
        output_files = []

        try:
            reader = PdfReader(input_pdf_path)
            num_pages = len(reader.pages)

            if num_pages == 0:
                raise ValueError("PDF has no pages")

            for page_num in range(num_pages):
                writer = PdfWriter()
                writer.add_page(reader.pages[page_num])

                unique_id = uuid.uuid4().hex
                output_filename = (
                    f"{os.path.splitext(file.filename)[0]}_"
                    f"{unique_id}_page_{page_num + 1}.pdf"
                )

                output_path = os.path.join(
                    self.file_manager.upload_folder,
                    output_filename
                )

                with open(output_path, "wb") as output_pdf:
                    writer.write(output_pdf)

                output_files.append(output_filename)

            return output_files

        except Exception:
            raise

        finally:
            self.file_manager.remove_file(input_pdf_path)

    def split_pdf_custom_range(self, file, page_range):
        input_pdf_path = self.file_manager.save_file(file)
        output_files = []

        try:
            reader = PdfReader(input_pdf_path)
            num_pages = len(reader.pages)

            if num_pages == 0:
                raise ValueError("PDF has no pages")

            ranges = page_range.split(',')
            pages_to_extract = set()

            for r in ranges:
                if '-' in r:
                    start, end = map(int, r.split('-'))
                    pages_to_extract.update(range(start - 1, min(end, num_pages)))
                else:
                    page_num = int(r) - 1
                    if 0 <= page_num < num_pages:
                        pages_to_extract.add(page_num)

            for page_num in sorted(pages_to_extract):
                writer = PdfWriter()
                writer.add_page(reader.pages[page_num])

                unique_id = uuid.uuid4().hex
                output_filename = (
                    f"{os.path.splitext(file.filename)[0]}_"
                    f"{unique_id}_page_{page_num + 1}.pdf"
                )

                output_path = os.path.join(
                    self.file_manager.upload_folder,
                    output_filename
                )

                with open(output_path, "wb") as output_pdf:
                    writer.write(output_pdf)

                output_files.append(output_filename)

            return output_files

        except Exception:
            raise
                