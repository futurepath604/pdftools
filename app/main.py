from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse
from typing import List
import os
import json

from app.tools.compressor import compress_pdf_logic
from app.tools.merger import merge_pdfs_logic

app = FastAPI(title="Secure PDF Tools Pro")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")

# 📄 ROUTING: আলাদা আলাদা পেজ লিংক (SEO & Multi-page Framework)
@app.get("/")
async def route_home():
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))

@app.get("/compress")
async def route_compress():
    return FileResponse(os.path.join(STATIC_DIR, "compress.html"))

@app.get("/merge")
async def route_merge():
    return FileResponse(os.path.join(STATIC_DIR, "merge.html"))


# ⚡ API: Advanced Compression
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

# ⚡ API: Sequenced Merge
@app.post("/api/merge")
async def api_merge(files: List[UploadFile] = File(...), file_order: str = Form(...)):
    if len(files) < 2:
        raise HTTPException(status_code=400, detail="Select at least 2 files.")
    try:
        order_list = json.loads(file_order)
        file_map = {f.filename: await f.read() for f in files}
        ordered_bytes = [file_map[name] for name in order_list if name in file_map]
        
        output_stream = merge_pdfs_logic(ordered_bytes)
        return StreamingResponse(output_stream, media_type="application/pdf", headers={"Content-Disposition": "attachment; filename=merged_secure_doc.pdf"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
