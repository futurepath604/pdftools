from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse
from typing import List
from pypdf import PdfReader, PdfWriter, PdfMerger
import os
import json
import io

app = FastAPI(title="Secure PDF Tools Pro")

# --- CORE LOGIC: COMPRESSOR ENGINE ---
def compress_pdf_logic(input_bytes: bytes, quality: str = "medium") -> io.BytesIO:
    try:
        reader = PdfReader(io.BytesIO(input_bytes))
        writer = PdfWriter()
        for page in reader.pages:
            writer.add_page(page)
        for page in writer.pages:
            page.compress_content_streams()
        output_stream = io.BytesIO()
        writer.write(output_stream)
        output_stream.seek(0)
        return output_stream
    except Exception:
        fallback = io.BytesIO(input_bytes)
        fallback.seek(0)
        return fallback

# --- CORE LOGIC: MERGER ENGINE ---
def merge_pdfs_logic(pdf_files_bytes: List[bytes]) -> io.BytesIO:
    try:
        merger = PdfMerger()
        for file_bytes in pdf_files_bytes:
            merger.append(io.BytesIO(file_bytes))
        output_stream = io.BytesIO()
        merger.write(output_stream)
        merger.close()
        output_stream.seek(0)
        return output_stream
    except Exception as e:
        raise RuntimeError(str(e))


# --- ROUTING: MULTI-PAGE FRAMEWORK ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")

@app.get("/")
async def route_home():
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))

@app.get("/compress")
async def route_compress():
    return FileResponse(os.path.join(STATIC_DIR, "compress.html"))

@app.get("/merge")
async def route_merge():
    return FileResponse(os.path.join(STATIC_DIR, "merge.html"))


# --- API ENDPOINTS ---
@app.post("/api/compress")
async def api_compress(file: UploadFile = File(...), quality: str = Form("medium")):
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Invalid file type.")
    try:
        content = await file.read()
        output_stream = compress_pdf_logic(content, quality)
        return StreamingResponse(output_stream, media_type="application/pdf", headers={"Content-Disposition": f"attachment; filename=optimized_{file.filename}"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/merge")
async def api_merge(files: List[UploadFile] = File(...), file_order: str = Form(...)):
    if len(files) < 2:
        raise HTTPException(status_code=400, detail="Select at least 2 files.")
    try:
        # সব আপলোডেড ফাইলের বাইটস মেমরিতে রিড করা
        file_map = {}
        all_raw_bytes = []
        for f in files:
            file_content = await f.read()
            file_map[f.filename] = file_content
            all_raw_bytes.append(file_content)
        
        # ফ্রন্টএন্ড থেকে পাঠানো সিকোয়েন্স লিস্ট পার্স করা
        try:
            order_list = json.loads(file_order)
            ordered_bytes = []
            for name in order_list:
                if name in file_map:
                    ordered_bytes.append(file_map[name])
        except Exception:
            ordered_bytes = []

        # 🔒 সেফটি ফলব্যাক: যদি নামের অমিলের কারণে লিস্ট খালি হয়ে যায়, তবে আপলোড করা সিকোয়েন্সেই মার্জ হবে (কোনো ক্র্যাশ করবে না)
        if not ordered_bytes:
            ordered_bytes = all_raw_bytes
        
        output_stream = merge_pdfs_logic(ordered_bytes)
        return StreamingResponse(output_stream, media_type="application/pdf", headers={"Content-Disposition": "attachment; filename=merged_secure_doc.pdf"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
