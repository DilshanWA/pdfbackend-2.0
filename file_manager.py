import os
import shutil
import zipfile

class FileManager:
    def __init__(self, upload_folder="/tmp/uploads", zip_folder="/tmp/zips"):
        self.upload_folder = upload_folder
        self.zip_folder = zip_folder
        os.makedirs(self.upload_folder, exist_ok=True)
        os.makedirs(self.zip_folder, exist_ok=True)

    def save_file(self, file):
        filepath = os.path.join(self.upload_folder, file.filename)
        # FastAPI UploadFile
        if hasattr(file, "file"):
            with open(filepath, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

        # Flask FileStorage (backward compatible)
        else:
            file.save(filepath)

        return filepath

    def remove_file(self, filepath):
        if os.path.exists(filepath):
            os.remove(filepath)

    def create_zip(self, files, zip_name):
        zip_path = os.path.join(self.zip_folder, zip_name)
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for file in files:
                zipf.write(file, arcname=os.path.basename(file))
                self.remove_file(file)
        return zip_path
