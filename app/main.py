import os
import sys
import json
import shutil
from typing import List
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

# Render এবং ডকার এনভায়রনমেন্টের পাইথন পাথ ফিক্স করার পার্মানেন্ট সলিউশন
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if current_dir not in sys.path:
    sys.path.append(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

# আপনার রিয়েল ফাইল নামের ওপর ভিত্তি করে ডাইরেক্ট ইমপোর্ট
try:
    from app.tools.compressor import compress_pdf_file
    from app.tools.merger import merge_pdf_files
    from app.tools.pdf_to_image import pdf_to_images
    from app.tools.image_to_pdf import images_to_pdf
    from app.tools.modify import modify_pdf_pages
    from app.tools.security import lock_pdf_file, unlock_pdf_file
except ImportError:
    from tools.compressor import compress_pdf_file
    from tools.merger import merge_pdf_files
    from tools.pdf_to_image import pdf_to_images
    from tools.image_to_pdf import images_to_pdf
    from tools.modify import modify_pdf_pages
    from tools.security import lock_pdf_file, unlock_pdf_file

app = FastAPI(title="Secure PDF Tools API")

# Mount Static Files for Frontend UI
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# --- HTML ROUTES ---
@app.get("/")
async def read_index():
    return FileResponse("app/static/index.html")

@app.get("/compress")
async def read_compress():
    return FileResponse("app/static/compress.html")

@app.get("/merge")
async def read_merge():
    return FileResponse("app/static/merge.html")

@app.get("/pdf-to-image")
async def read_pdf_to_image():
    return FileResponse("app/static/pdf-to-image.html")

@app.get("/image-to-pdf")
async def read_image_to_pdf():
    return FileResponse("app/static/image-to-pdf.html")

@app.get("/split")
async def read_split():
    return FileResponse("app/static/split.html")

@app.get("/rotate")
async def read_rotate():
    return FileResponse("app/static/rotate.html")

@app.get("/delete-pages")
async def read_delete_pages():
    return FileResponse("app/static/delete-pages.html")

@app.get("/lock")
async def read_lock():
    return FileResponse("app/static/lock.html")

@app.get("/unlock")
async def read_unlock():
    return FileResponse("app/static/unlock.html")


# --- API ENDPOINTS ---

@app.post("/api/compress")
async def compress_pdf(file: UploadFile = File(...)):
    input_path = f"temp_input_{file.filename}"
    output_path = f"compressed_{file.filename}"
    with open(input_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    try:
        compress_pdf_file(input_path, output_path)
        return FileResponse(output_path, media_type="application/pdf", filename=output_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(input_path): os.remove(input_path)


@app.post("/api/merge")
async def merge_pdfs(files: List[UploadFile] = File(...)):
    input_paths = []
    output_path = "merged_document.pdf"
    for file in files:
        path = f"temp_{file.filename}"
        with open(path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        input_paths.append(path)
    try:
        merge_pdf_files(input_paths, output_path)
        return FileResponse(output_path, media_type="application/pdf", filename=output_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        for path in input_paths:
            if os.path.exists(path): os.remove(path)


@app.post("/api/pdf-to-image")
async def pdf_to_img(file: UploadFile = File(...)):
    input_path = f"temp_{file.filename}"
    output_zip = f"images_{file.filename}.zip"
    with open(input_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    try:
        pdf_to_images(input_path, output_zip)
        return FileResponse(output_zip, media_type="application/zip", filename=output_zip)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(input_path): os.remove(input_path)


@app.post("/api/image-to-pdf")
async def img_to_pdf(files: List[UploadFile] = File(...)):
    input_paths = []
    output_path = "images_converted.pdf"
    for file in files:
        path = f"temp_{file.filename}"
        with open(path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        input_paths.append(path)
    try:
        images_to_pdf(input_paths, output_path)
        return FileResponse(output_path, media_type="application/pdf", filename=output_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        for path in input_paths:
            if os.path.exists(path): os.remove(path)


@app.post("/api/modify-pdf")
async def modify_pdf(
    file: UploadFile = File(...),
    mode: str = Form(...),
    params: str = Form(...)
):
    input_path = f"temp_{file.filename}"
    output_path = f"modified_{file.filename}"
    with open(input_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    try:
        param_dict = json.loads(params)
        modify_pdf_pages(input_path, output_path, mode, param_dict)
        return FileResponse(output_path, media_type="application/pdf", filename=output_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(input_path): os.remove(input_path)


@app.post("/api/security-pdf")
async def security_pdf(
    file: UploadFile = File(...),
    mode: str = Form(...),
    password: str = Form(...)
):
    input_path = f"temp_{file.filename}"
    output_path = f"secured_{file.filename}"
    with open(input_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    try:
        if mode == "lock":
            lock_pdf_file(input_path, output_path, password)
        elif mode == "unlock":
            unlock_pdf_file(input_path, output_path, password)
        else:
            raise HTTPException(status_code=400, detail="Invalid security mode")
        return FileResponse(output_path, media_type="application/pdf", filename=output_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(input_path): os.remove(input_path)
