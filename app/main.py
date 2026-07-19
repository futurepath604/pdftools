import os
import sys
import json
import shutil
from typing import List
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

# Setup path environments
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if current_dir not in sys.path: sys.path.append(current_dir)
if parent_dir not in sys.path: sys.path.append(parent_dir)

# --- SAFE IMPORTS BLOCK FOR CORE MODULES ---
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

# Separate Office Converter Imports
try: from app.tools.pdf_to_word import convert_pdf_to_word
except Exception: convert_pdf_to_word = None

try: from app.tools.pdf_to_excel import convert_pdf_to_excel
except Exception: convert_pdf_to_excel = None

try: from app.tools.pdf_to_ppt import convert_pdf_to_ppt
except Exception: convert_pdf_to_ppt = None


def merge_pdf_files(input_paths: list, output_path: str):
    try:
        from pypdf import PdfMerger
        merger = PdfMerger()
        for path in input_paths: merger.append(path)
        merger.write(output_path)
        merger.close()
    except Exception as e:
        raise Exception(f"Merge operation error: {str(e)}")


app = FastAPI(title="Secure PDF Tools Ultimate API")

# Mount Static Files securely
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


# --- CORE API ENGINE ENDPOINTS ---
@app.post("/api/compress")
async def compress_pdf(file: UploadFile = File(...)):
    if not compress_pdf_file: raise HTTPException(status_code=501, detail="Compress module missing")
    input_path = f"temp_{file.filename}"
    output_path = f"compressed_{file.filename}"
    with open(input_path, "wb") as buffer: shutil.copyfileobj(file.file, buffer)
    try:
        compress_pdf_file(input_path, output_path)
        return FileResponse(output_path, media_type="application/pdf", filename=output_path)
    except Exception as e: raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(input_path): os.remove(input_path)

@app.post("/api/merge")
async def merge_pdfs(files: List[UploadFile] = File(...)):
    input_paths = []
    output_path = "merged_document.pdf"
    for file in files:
        path = f"temp_{file.filename}"
        with open(path, "wb") as buffer: shutil.copyfileobj(file.file, buffer)
        input_paths.append(path)
    try:
        merge_pdf_files(input_paths, output_path)
        return FileResponse(output_path, media_type="application/pdf", filename=output_path)
    except Exception as e: raise HTTPException(status_code=500, detail=str(e))
    finally:
        for path in input_paths:
            if os.path.exists(path): os.remove(path)

@app.post("/api/pdf-to-image")
async def pdf_to_img(file: UploadFile = File(...)):
    if not pdf_to_images: raise HTTPException(status_code=501, detail="Converter module missing")
    input_path = f"temp_{file.filename}"
    output_zip = f"images_{file.filename}.zip"
    with open(input_path, "wb") as buffer: shutil.copyfileobj(file.file, buffer)
    try:
        pdf_to_images(input_path, output_zip)
        return FileResponse(output_zip, media_type="application/zip", filename=output_zip)
    except Exception as e: raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(input_path): os.remove(input_path)

@app.post("/api/image-to-pdf")
async def img_to_pdf(files: List[UploadFile] = File(...)):
    if not images_to_pdf: raise HTTPException(status_code=501, detail="Converter module missing")
    input_paths = []
    output_path = "images_converted.pdf"
    for file in files:
        path = f"temp_{file.filename}"
        with open(path, "wb") as buffer: shutil.copyfileobj(file.file, buffer)
        input_paths.append(path)
    try:
        images_to_pdf(input_paths, output_path)
        return FileResponse(output_path, media_type="application/pdf", filename=output_path)
    except Exception as e: raise HTTPException(status_code=500, detail=str(e))
    finally:
        for path in input_paths:
            if os.path.exists(path): os.remove(path)

@app.post("/api/modify-pdf")
async def modify_pdf(file: UploadFile = File(...), mode: str = Form(...), params: str = Form(...)):
    if not modify_pdf_pages: raise HTTPException(status_code=501, detail="Modify module missing")
    input_path = f"temp_{file.filename}"
    output_path = f"modified_{file.filename}"
    with open(input_path, "wb") as buffer: shutil.copyfileobj(file.file, buffer)
    try:
        param_dict = json.loads(params)
        modify_pdf_pages(input_path, output_path, mode, param_dict)
        return FileResponse(output_path, media_type="application/pdf", filename=output_path)
    except Exception as e: raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(input_path): os.remove(input_path)

@app.post("/api/security-pdf")
async def security_pdf(file: UploadFile = File(...), mode: str = Form(...), password: str = Form(...)):
    if not lock_pdf_file: raise HTTPException(status_code=501, detail="Security module missing")
    input_path = f"temp_{file.filename}"
    output_path = f"secured_{file.filename}"
    with open(input_path, "wb") as buffer: shutil.copyfileobj(file.file, buffer)
    try:
        if mode == "lock": lock_pdf_file(input_path, output_path, password)
        elif mode == "unlock": unlock_pdf_file(input_path, output_path, password)
        return FileResponse(output_path, media_type="application/pdf", filename=output_path)
    except Exception as e: raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(input_path): os.remove(input_path)

@app.post("/api/ocr")
async def ocr_pdf(file: UploadFile = File(...)):
    if not process_pdf_ocr: raise HTTPException(status_code=501, detail="OCR Engine missing")
    input_path = f"temp_{file.filename}"
    output_path = f"ocr_{file.filename}"
    with open(input_path, "wb") as buffer: shutil.copyfileobj(file.file, buffer)
    try:
        process_pdf_ocr(input_path, output_path)
        return FileResponse(output_path, media_type="application/pdf", filename=output_path)
    except Exception as e: raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(input_path): os.remove(input_path)

@app.post("/api/rearrange")
async def rearrange_pdf(file: UploadFile = File(...), page_order: str = Form(...)):
    if not rearrange_pdf_pages: raise HTTPException(status_code=501, detail="Rearrange module missing")
    input_path = f"temp_{file.filename}"
    output_path = f"rearranged_{file.filename}"
    with open(input_path, "wb") as buffer: shutil.copyfileobj(file.file, buffer)
    try:
        order_list = json.loads(page_order)
        rearrange_pdf_pages(input_path, output_path, order_list)
        return FileResponse(output_path, media_type="application/pdf", filename=output_path)
    except Exception as e: raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(input_path): os.remove(input_path)


# --- DEDICATED NEW OFFICE API ENDPOINTS ---
@app.post("/api/pdf-to-word")
async def api_pdf_to_word(file: UploadFile = File(...)):
    if not convert_pdf_to_word: raise HTTPException(status_code=501, detail="Word core setup missing")
    input_path = f"temp_{file.filename}"
    output_path = f"{os.path.splitext(file.filename)[0]}.docx"
    with open(input_path, "wb") as buffer: shutil.copyfileobj(file.file, buffer)
    try:
        convert_pdf_to_word(input_path, output_path)
        return FileResponse(output_path, media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document", filename=output_path)
    except Exception as e: raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(input_path): os.remove(input_path)

@app.post("/api/pdf-to-excel")
async def api_pdf_to_excel(file: UploadFile = File(...)):
    if not convert_pdf_to_excel: raise HTTPException(status_code=501, detail="Excel core setup missing")
    input_path = f"temp_{file.filename}"
    output_path = f"{os.path.splitext(file.filename)[0]}.xlsx"
    with open(input_path, "wb") as buffer: shutil.copyfileobj(file.file, buffer)
    try:
        convert_pdf_to_excel(input_path, output_path)
        return FileResponse(output_path, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", filename=output_path)
    except Exception as e: raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(input_path): os.remove(input_path)

@app.post("/api/pdf-to-ppt")
async def api_pdf_to_ppt(file: UploadFile = File(...)):
    if not convert_pdf_to_ppt: raise HTTPException(status_code=501, detail="PowerPoint core setup missing")
    input_path = f"temp_{file.filename}"
    output_path = f"{os.path.splitext(file.filename)[0]}.pptx"
    with open(input_path, "wb") as buffer: shutil.copyfileobj(file.file, buffer)
    try:
        convert_pdf_to_ppt(input_path, output_path)
        return FileResponse(output_path, media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation", filename=output_path)
    except Exception as e: raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(input_path): os.remove(input_path)
