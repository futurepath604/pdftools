from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse
from typing import List
import os

# সব মডুলার লজিক ইম্পোর্ট করা হলো
from app.tools.compressor import compress_pdf_logic
from app.tools.merger import merge_pdfs_logic

app = FastAPI(title="Secure PDF Tools API")

# 1. PDF Compression Endpoint
@app.post("/api/compress")
async def api_compress(file: UploadFile = File(...)):
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="দয়া করে শুধুমাত্র PDF ফাইল আপলোড করুন।")
    try:
        content = await file.read()
        if len(content) > 15 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="ফাইল সাইজ ১৫ মেগাবাইটের বেশি হওয়া যাবে না।")
        
        output_stream = compress_pdf_logic(content)
        return StreamingResponse(
            output_stream, 
            media_type="application/pdf", 
            headers={"Content-Disposition": f"attachment; filename=compressed_{file.filename}"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 2. PDF Merge Endpoint
@app.post("/api/merge")
async def api_merge(files: List[UploadFile] = File(...)):
    if len(files) < 2:
        raise HTTPException(status_code=400, detail="জোড়া দেওয়ার জন্য নূন্যতম ২টি ফাইল সিলেক্ট করুন।")
    
    files_bytes = []
    for file in files:
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="সবগুলো ফাইলই PDF হতে হবে।")
        content = await file.read()
        files_bytes.append(content)
        
    try:
        output_stream = merge_pdfs_logic(files_bytes)
        return StreamingResponse(
            output_stream, 
            media_type="application/pdf", 
            headers={"Content-Disposition": "attachment; filename=merged_document.pdf"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 3. Frontend UI Routing Configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
INDEX_HTML = os.path.join(STATIC_DIR, "index.html")

@app.get("/")
async def read_index():
    if os.path.exists(INDEX_HTML):
        return FileResponse(INDEX_HTML)
    return {"error": "Frontend UI (index.html) file not found."}

if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
