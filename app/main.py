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


# --- 📂 PATH FIX: ABSOLUTE STATIC DIRECTORY RESOLUTION ---
# রেন্ডার সার্ভারের কারেন্ট ওয়ার্কিং ডিরেক্টরি অনুযায়ী ডাইনামিক পাথ সেটআপ
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

# প্রজেক্ট রুট বা অ্যাপ ফোল্ডার উভয় জায়গার 'static' ফোল্ডার সেফটি চেক
STATIC_DIR = os.path.join(CURRENT_DIR, "static")
if not os.path.exists(STATIC_DIR):
    # ফলব্যাক: যদি static ফোল্ডারটি রুট ডিরেক্টরিতে থাকে
    STATIC_DIR = os.path.abspath(os.path.join(CURRENT_DIR, "..", "static"))
    if not os.path.exists(STATIC_DIR):
        # সেকেন্ডারি ফলব্যাক: যদি কারেন্ট ডিরেক্টরিই রুট হয়
        STATIC_DIR = os.path.join(os.getcwd(), "static")

# --- ROUTING: MULTI-PAGE FRAMEWORK ---
@app.get("/")
async def route_home():
    target_path = os.path.join(STATIC_DIR, "index.html")
    if not os.path.exists(target_path):
        raise HTTPException(status_code=404, detail=f"Homepage not found at {target_path}")
    return FileResponse(target_path)

@app.get("/compress")
async def route_compress():
    target_path = os.path.join(STATIC_DIR, "compress.html")
    if not os.path.exists(target_path):
        raise HTTPException(status_code=404, detail=f"Compress page not found at {target_path}")
    return FileResponse(target_path)

@app.get("/merge")
async def route_merge():
    target_path = os.path.join(STATIC_DIR, "merge.html")
    if not os.path.exists(target_path):
        raise HTTPException(status_code=404, detail=f"Merge page not found at {target_path}")
    return FileResponse(target_path)


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
        file_map = {}
        all_raw_bytes = []
        for f in files:
            file_content = await f.read()
            file_map[f.filename] = file_content
            all_raw_bytes.append(file_content)
        
        try:
            order_list = json.loads(file_order)
            ordered_bytes = []
            for name in order_list:
                if name in file_map:
                    ordered_bytes.append(file_map[name])
        except Exception:
            ordered_bytes = []

        if not ordered_bytes:
            ordered_bytes = all_raw_bytes
        
        output_stream = merge_pdfs_logic(ordered_bytes)
        return StreamingResponse(output_stream, media_type="application/pdf", headers={"Content-Disposition": "attachment; filename=merged_secure_doc.pdf"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Static ফাইল মাউন্ট করা (যদি static ফোল্ডারটি এক্সিস্ট করে)
if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
