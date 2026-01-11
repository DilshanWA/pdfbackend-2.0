import os
import subprocess

class Compressor:
    gs_quality_map = {
        'low': '/screen',
        'medium': '/ebook',
        'high': '/prepress'
    }

    def __init__(self, file_manager):
        self.file_manager = file_manager

    def compress_pdf(self, input_path, output_path, quality, file_size_bytes):
        if quality not in self.gs_quality_map:
            quality = 'medium'

        gs_quality = self.gs_quality_map[quality]
        if quality == 'high' and file_size_bytes > 1 * 1024 * 1024:
            gs_quality = '/screen'

        subprocess.run([
            "gs",
            "-sDEVICE=pdfwrite",
            "-dCompatibilityLevel=1.4",
            f"-dPDFSETTINGS={gs_quality}",
            "-dNOPAUSE",
            "-dQUIET",
            "-dBATCH",
            f"-sOutputFile={output_path}",
            input_path
        ], check=True)

    def compress(self, file, quality):
        filename = file.filename
        name, ext = os.path.splitext(filename)
        input_path = self.file_manager.save_file(file)
        output_filename = f"{name}_compressed.pdf"
        output_path = os.path.join(self.file_manager.upload_folder, output_filename)

        file_size_bytes = os.path.getsize(input_path)

        self.compress_pdf(input_path, output_path, quality, file_size_bytes)
        self.file_manager.remove_file(input_path)

        return output_filename
