from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse
from typing import List
import os
import json

from app.tools.compressor import compress_pdf_logic
from app.tools.merger import merge_pdfs_logic

app = FastAPI(
    title="Secure PDF Tools",
    description="Professional Private PDF Processor Ecosystem",
    version="2.0.0"
)

# 1. API: Advanced Compression
@app.post("/api/compress")
async def api_compress(
    file: UploadFile = File(...),
    quality: str = Form("medium") # high, medium, low
):
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Invalid file type. PDF required.")
    try:
        content = await file.read()
        if len(content) > 15 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="File size exceeds 15MB limit.")
        
        output_stream = compress_pdf_logic(content, quality)
        return StreamingResponse(
            output_stream, 
            media_type="application/pdf", 
            headers={"Content-Disposition": f"attachment; filename=optimized_{file.filename}"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 2. API: Sequenced Merge
@app.post("/api/merge")
async def api_merge(
    files: List[UploadFile] = File(...),
    file_order: str = Form(...) # JSON string of ordered filenames
):
    if len(files) < 2:
        raise HTTPException(status_code=400, detail="Select at least 2 PDF files.")
    
    try:
        order_list = json.loads(file_order)
        # ফাইলগুলোকে সিকোয়েন্স বা প্রায়োরিটি অনুযায়ী ম্যাপ করা
        file_map = {f.filename: await f.read() for f in files}
        
        ordered_bytes = []
        for filename in order_list:
            if filename in file_map:
                ordered_bytes.append(file_map[filename])
                
        if not ordered_bytes:
            ordered_bytes = [await f.read() for f in files] # Fallback to default order
            
        output_stream = merge_pdfs_logic(ordered_bytes)
        return StreamingResponse(
            output_stream, 
            media_type="application/pdf", 
            headers={"Content-Disposition": "attachment; filename=merged_secure_doc.pdf"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 3. Web Engine & SEO Content
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
INDEX_HTML = os.path.join(STATIC_DIR, "index.html")

@app.get("/")
async def read_index():
    if os.path.exists(INDEX_HTML):
        return FileResponse(INDEX_HTML)
    return {"error": "UI Index Not Found"}

if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
