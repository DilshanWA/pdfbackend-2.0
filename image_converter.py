
from PIL import Image
import os
import uuid

IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".webp")

class Image_converter():
    A4_WIDTH, A4_HEIGHT = 595, 842

    def __init__(self, file_manager):
        self.file_manager = file_manager

    def image_to_a4_pdf(self, input_path, output_pdf_path):
        image = Image.open(input_path)
        if image.mode in ("RGBA", "LA") or (image.mode == "P" and "transparency" in image.info):
            background = Image.new("RGB", image.size, (255, 255, 255))
            background.paste(image, mask=image.split()[-1])
            image = background
        else:
            image = image.convert("RGB")

        image.thumbnail((self.A4_WIDTH, self.A4_HEIGHT))
        a4_canvas = Image.new("RGB", (self.A4_WIDTH, self.A4_HEIGHT), "white")
        x = (self.A4_WIDTH - image.width) // 2
        y = (self.A4_HEIGHT - image.height) // 2
        a4_canvas.paste(image, (x, y))
        a4_canvas.save(output_pdf_path, "PDF")

    def convert_image_to_pdf(self, file):
        filename = file.filename
        name, ext = os.path.splitext(filename)
        ext = ext.lower()

        if ext not in IMAGE_EXTENSIONS:
            raise ValueError(f"Unsupported image format: {ext}")

        filepath = self.file_manager.save_file(file)

        pdf_filename = f"{name}_{uuid.uuid4().hex}_converted.pdf"
        pdf_path = os.path.join(self.file_manager.upload_folder, pdf_filename)
        self.image_to_a4_pdf(filepath, pdf_path)
        self.file_manager.remove_file(filepath)
        return pdf_filename