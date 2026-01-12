from fastapi import FastAPI, File, UploadFile, Request,HTTPException,Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
import os
import uuid
from typing import List

from file_manager import FileManager
from converter import Converter
from merge import Merger
from compressor import Compressor
from protector import Protector
from split import PdfSpliter
from image_converter import Image_converter

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to your domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

file_manager = FileManager()
converter = Converter(file_manager)
image_converter = Image_converter(file_manager)
merger = Merger(file_manager)
compressor = Compressor(file_manager)
protector = Protector(file_manager)
spliter = PdfSpliter(file_manager)


#---------Office to PDF Conversion Endpoint---------#
@app.post("/convert")
async def convert_endpoint(
    request: Request,
    files: List[UploadFile] = File(...)
):
    if not files:
        return {"error": "No files provided"}

    pdf_files = []
    for file in files:
        pdf = converter.convert_file(file)
        pdf_filename = os.path.basename(pdf)
        pdf_files.append(pdf_filename)

    if len(pdf_files) == 1:
        pdf_url = str(
            request.url_for("download_file", filename=pdf_files[0])
        )
        return {
            "message": "File converted successfully",
            "pdf_file": pdf_files[0],
            "pdf_url": pdf_url,
            "file_count": len(pdf_files)
        }

    zip_id = uuid.uuid4().hex
    zip_filename = f"converted_{zip_id}.zip"
    pdf_paths = [
        os.path.join(file_manager.upload_folder, f)
        for f in pdf_files
    ]
    file_manager.create_zip(pdf_paths, zip_filename)

    zip_url = str(
        request.url_for("download_zip", filename=zip_filename)
    )

    return {
        "message": "Files converted successfully",
        "zip_file": zip_filename,
        "zip_url": zip_url,
        "file_count": len(pdf_files)
    }

#---------PDF Merge Endpoint---------#
@app.post("/merge")
async def merge_endpoint(
    request: Request,
    files: List[UploadFile] = File(...)
):
    if not files:
        return {"error": "No files provided"}

    merged_pdf = merger.merge_pdfs(files)

    pdf_url = str(
        request.url_for("download_file", filename=merged_pdf)
    )

    return {
        "message": "Files merged successfully",
        "pdf_file": merged_pdf,
        "pdf_url": pdf_url,
        "file_count": len(merged_pdf)
    }

#---------PDF Compress Endpoint---------#
@app.post("/compress")
async def compress_endpoint(
    request: Request,
    files: List[UploadFile] = File(...),
    qualityOption: str = "medium"
):
    if not files:
        return {"error": "No files provided"}
    compressed_pdfs = []
    for file in files:
        compressed_pdf = compressor.compress(file, qualityOption)
        compressed_pdfs.append(compressed_pdf)

    if len(compressed_pdfs) == 1:
        pdf_url = str(
            request.url_for("download_file", filename=compressed_pdfs[0])
        )
        return {
            "message": "File compressed successfully",
            "pdf_file": compressed_pdfs[0],
            "pdf_url": pdf_url,
            "file_count": len(compressed_pdfs)
        }

    zip_id = uuid.uuid4().hex
    zip_filename = f"compressed_{zip_id}.zip"
    pdf_paths = [
        os.path.join(file_manager.upload_folder, f)
        for f in compressed_pdfs
    ]
    file_manager.create_zip(pdf_paths, zip_filename)

    zip_url = str(
        request.url_for("download_zip", filename=zip_filename)
    )

    return {
        "message": "Files compressed successfully",
        "zip_file": zip_filename,
        "zip_url": zip_url,
        "file_count": len(compressed_pdfs)
    }

#---------Image to PDF Conversion Endpoint---------#
@app.post("/imageconverter")
async def image_to_pdf_endpoint(
    request: Request, 
    files: List[UploadFile] = File(...), 
    check_box_value: bool = Form(False)
):
    if not files:
        return {"error": "No files provided"}
    
    pdf_filenames = []
    for file in files:
        pdf_full_path = image_converter.convert_image_to_pdf(file)
        filename_only = os.path.basename(pdf_full_path)  # ✅ ensures just the filename
        pdf_filenames.append(filename_only)
        
    if check_box_value and len(pdf_filenames) > 1:
        merged_image_pdf_name = "cloudpdf-merged-images-pdf.pdf"
        merged_image_pdf_path = os.path.join(file_manager.upload_folder, merged_image_pdf_name)
        
        merger.merge_pdf_paths([os.path.join(file_manager.upload_folder, f) for f in pdf_filenames], merged_image_pdf_path)
    
        pdf_url = str(request.url_for("download_file", filename=merged_image_pdf_name))
        return {
            "message": "Images converted and merged successfully",
            "pdf_file": merged_image_pdf_name,
            "pdf_url": pdf_url,
            "file_count": 1
        }
    else:
        # Handle single file
        if len(pdf_filenames) == 1:
            target_file = pdf_filenames[0]
            pdf_url = str(request.url_for("download_file", filename=target_file))  # ✅ just filename, not path
            return {
                "message": "Image converted successfully",
                "pdf_file": target_file,
                "pdf_url": pdf_url,
                "file_count": 1
            }

        # Multiple files → create zip
        zip_id = uuid.uuid4().hex
        zip_filename = f"images_converted_{zip_id}.zip"
        pdf_paths = [os.path.join(file_manager.upload_folder, f) for f in pdf_filenames]
        file_manager.create_zip(pdf_paths, zip_filename)

        zip_url = str(request.url_for("download_zip", filename=zip_filename))
        return {
            "message": "Images converted successfully",
            "zip_file": zip_filename,
            "zip_url": zip_url,
            "file_count": len(pdf_filenames)
        }

#---------Protect PDF Endpoint---------#
@app.post("/protect")
async def protect_endpoint(request: Request, files: List[UploadFile] = File(...), password: str = Form(...)):
    if not files:
        return {"error": "No files provided"}

    protected_pdfs = []
    for file in files:
        protected_pdf = protector.protect_pdf(file, password)
        protected_pdfs.append(protected_pdf)

    if len(protected_pdfs) == 1:
        pdf_url = str(
            request.url_for("download_file", filename=protected_pdfs[0])
        )
        return {
            "message": "File protected successfully",
            "pdf_file": protected_pdfs[0],
            "pdf_url": pdf_url,
            "file_count": len(protected_pdfs)
        }

    zip_id = uuid.uuid4().hex
    zip_filename = f"protected_{zip_id}.zip"
    pdf_paths = [
        os.path.join(file_manager.upload_folder, f)
        for f in protected_pdfs
    ]
    file_manager.create_zip(pdf_paths, zip_filename)

    zip_url = str(
        request.url_for("download_zip", filename=zip_filename)
    )

    return {
        "message": "Files protected successfully",
        "zip_file": zip_filename,
        "zip_url": zip_url,
        "file_count": len(protected_pdfs)
    }
    
#--------Split PDF Endpoint---------#
@app.post("/split")
async def split_endpoint(
    request: Request, 
    files: List[UploadFile] = File(...), 
    split_checkbox: bool = Form(False), 
    mode: str = Form("allPages"),  # default value set here
    page_range: str = Form("")     # you might also give a default empty string
):
    if not files:
        return {"error": "No file provided"}
    
    splited_pdfs = []
    print("Mode:", mode)
    
    try:
        if mode == "allPages":
            for file in files:
                split_files = spliter.split_pdf(file)
                splited_pdfs.extend(split_files)

        elif mode == "custom":
            for file in files:
                split_files = spliter.split_pdf_custom_range(file, page_range)
                splited_pdfs.extend(split_files)

            if split_checkbox and len(splited_pdfs) > 1:
                merge_splited_pdf_name = "cloudpdf-merged-splited-pdf.pdf"
                merge_split_pdf_path = os.path.join(file_manager.upload_folder, merge_splited_pdf_name)
                
                pdf_paths = [os.path.join(file_manager.upload_folder, f) for f in splited_pdfs]
                
                merger.merge_pdf_paths(pdf_paths, merge_split_pdf_path)
                splited_pdfs = [merge_splited_pdf_name]
                
        if len(splited_pdfs) == 1:
            pdf_url = str(request.url_for("download_file", filename=splited_pdfs[0]))
            return {
                "message": "File splitted successfully",
                "pdf_file": splited_pdfs[0],
                "pdf_url": pdf_url,
                "file_count": len(splited_pdfs)
            }
        else:
            zip_id = uuid.uuid4().hex
            zip_filename = f"splitted_{zip_id}.zip"
            pdf_paths = [os.path.join(file_manager.upload_folder, f) for f in splited_pdfs]
            file_manager.create_zip(pdf_paths, zip_filename)

            zip_url = str(request.url_for("download_zip", filename=zip_filename))

            return {
                "message": "Files splitted successfully",
                "zip_file": zip_filename,
                "zip_url": zip_url,
                "file_count": len(splited_pdfs)
            }
    except Exception as e:
        print("Error during splitting:", str(e))
        raise HTTPException(status_code=500, detail=str(e))


 


@app.get("/download/{filename}")
async def download_file(filename: str):
    path = os.path.join(file_manager.upload_folder, filename)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(path, filename=filename)


@app.get("/download_zip/{filename}")
async def download_zip(filename: str):
    path = os.path.join(file_manager.zip_folder, filename)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Zip not found")
    return FileResponse(path, filename=filename)