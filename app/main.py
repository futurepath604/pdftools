import os
import sys
import json
import shutil
from typing import List
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

# Setup paths
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if current_dir not in sys.path: sys.path.append(current_dir)
if parent_dir not in sys.path: sys.path.append(parent_dir)

# --- CORE INTEGRATED UTILITIES ---
try: from app.tools.compressor import compress_pdf_file
except Exception: compress_pdf_file = None

try: from app.tools.pdf_to_image import pdf_to_images
except Exception: pdf_to_images = None

try: from app.tools.image_to_pdf import images_to_pdf
except Exception: images_to_pdf = None

try: from app.tools.modify import modify_pdf_pages
except Exception: modify_pdf_pages = None

try: from app.tools.security import lock_pdf_file, unlock_pdf_file
except Exception: lock_pdf_file = unlock_pdf_file = None

try: from app.tools.ocr_engine import process_pdf_ocr
except Exception: process_pdf_ocr = None

try: from app.tools.rearrange_backend import rearrange_pdf_pages
except Exception: rearrange_pdf_pages = None


def merge_pdf_files(input_paths: list, output_path: str):
    from pypdf import PdfMerger
    merger = PdfMerger()
    for path in input_paths: merger.append(path)
    merger.write(output_path)
    merger.close()


app = FastAPI(title="Secure PDF Tools Ultimate API")

if os.path.exists("app/static"):
    app.mount("/static", StaticFiles(directory="app/static"), name="static")

# --- HTML UI ENDPOINTS ---
@app.get("/")
async def read_index(): return FileResponse("app/static/index.html")

@app.get("/compress")
async def read_compress(): return FileResponse("app/static/compress.html")

@app.get("/merge")
async def read_merge(): return FileResponse("app/static/merge.html")

@app.get("/pdf-to-image")
async def read_pdf_to_image(): return FileResponse("app/static/pdf-to-image.html")

@app.get("/image-to-pdf")
async def read_image_to_pdf(): return FileResponse("app/static/image-to-pdf.html")

@app.get("/split")
async def read_split(): return FileResponse("app/static/split.html")

@app.get("/rotate")
async def read_rotate(): return FileResponse("app/static/rotate.html")

@app.get("/delete-pages")
async def read_delete_pages(): return FileResponse("app/static/delete-pages.html")

@app.get("/lock")
async def read_lock(): return FileResponse("app/static/lock.html")

@app.get("/unlock")
async def read_unlock(): return FileResponse("app/static/unlock.html")

@app.get("/ocr")
async def read_ocr(): return FileResponse("app/static/ocr.html")

@app.get("/rearrange")
async def read_rearrange(): return FileResponse("app/static/rearrange.html")

@app.get("/pdf-to-word")
async def read_pdf_to_word(): return FileResponse("app/static/pdf-to-word.html")

@app.get("/pdf-to-excel")
async def read_pdf_to_excel(): return FileResponse("app/static/pdf-to-excel.html")

@app.get("/pdf-to-ppt")
async def read_pdf_to_ppt(): return FileResponse("app/static/pdf-to-ppt.html")


# --- DEDICATED API ENGINE ROUTES (FIXED FOR DYNAMIC ERROR TRACKING) ---

@app.post("/api/pdf-to-word")
async def api_pdf_to_word(file: UploadFile = File(...)):
    # Dynamically import inside the route execution block to catch actual errors
    try:
        from app.tools.pdf_to_word import convert_pdf_to_word
    except Exception as import_error:
        raise HTTPException(status_code=500, detail=f"Word Core Import Failure: {str(import_error)}")
        
    input_path = f"temp_{file.filename}"
    output_path = f"{os.path.splitext(file.filename)[0]}.docx"
    
    with open(input_path, "wb") as buffer: 
        shutil.copyfileobj(file.file, buffer)
        
    try:
        convert_pdf_to_word(input_path, output_path)
        return FileResponse(output_path, media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document", filename=output_path)
    except Exception as e: 
        raise HTTPException(status_code=500, detail=f"Word Conversion Engine Error: {str(e)}")
    finally:
        if os.path.exists(input_path): os.remove(input_path)


@app.post("/api/pdf-to-excel")
async def api_pdf_to_excel(file: UploadFile = File(...)):
    # Dynamically import inside the route execution block to catch actual errors
    try:
        from app.tools.pdf_to_excel import convert_pdf_to_excel
    except Exception as import_error:
        raise HTTPException(status_code=500, detail=f"Excel Core Import Failure: {str(import_error)}")
        
    input_path = f"temp_{file.filename}"
    output_path = f"{os.path.splitext(file.filename)[0]}.xlsx"
    
    with open(input_path, "wb") as buffer: 
        shutil.copyfileobj(file.file, buffer)
        
    try:
        convert_pdf_to_excel(input_path, output_path)
        return FileResponse(output_path, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", filename=output_path)
    except Exception as e: 
        raise HTTPException(status_code=500, detail=f"Excel Conversion Engine Error: {str(e)}")
    finally:
        if os.path.exists(input_path): os.remove(input_path)


@app.post("/api/pdf-to-ppt")
async def api_pdf_to_ppt(file: UploadFile = File(...)):
    # Dynamically import inside the route execution block to catch actual errors
    try:
        from app.tools.pdf_to_ppt import convert_pdf_to_ppt
    except Exception as import_error:
        raise HTTPException(status_code=500, detail=f"PPT Core Import Failure: {str(import_error)}")
        
    input_path = f"temp_{file.filename}"
    output_path = f"{os.path.splitext(file.filename)[0]}.pptx"
    
    with open(input_path, "wb") as buffer: 
        shutil.copyfileobj(file.file, buffer)
        
    try:
        convert_pdf_to_ppt(input_path, output_path)
        return FileResponse(output_path, media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation", filename=output_path)
    except Exception as e: 
        raise HTTPException(status_code=500, detail=f"PPT Conversion Engine Error: {str(e)}")
    finally:
        if os.path.exists(input_path): os.remove(input_path)
