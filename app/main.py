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


# --- 🕵️‍♂️ SMART PATH FINDER ENGINE (চিরস্থায়ী সমাধান) ---
def find_html_file(filename: str) -> str:
    """
    সার্ভারের রুট, অ্যাপ বা স্ট্যাটিক ফোল্ডারের যেকোনো জায়গা থেকে 
    খুঁজে ফাইলটির সঠিক পরম পাথ (Absolute Path) বের করার ফলব্যাক লজিক।
    """
    possible_paths = [
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", filename),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), filename),
        os.path.join(os.getcwd(), "static", filename),
        os.path.join(os.getcwd(), filename),
        os.path.join("/code", "app", "static", filename),
        os.path.join("/code", filename)
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
            
    # যদি কোথাও ফাইল না পাওয়া যায়, তবে রুট ডিরেক্টরি স্ক্যান করে খোঁজার চেষ্টা
    base_root = os.getcwd()
    for root, dirs, files in os.walk(base_root):
        if filename in files:
            return os.path.join(root, filename)
            
    raise HTTPException(status_code=404, detail=f"ক্রিটিকাল এরর: '{filename}' ফাইলটি গিটহাবের কোনো ফোল্ডারেই খুঁজে পাওয়া যায়নি।")


# --- ROUTING: MULTI-PAGE FRAMEWORK ---
@app.get("/")
async def route_home():
    return FileResponse(find_html_file("index.html"))

@app.get("/compress")
async def route_compress():
    return FileResponse(find_html_file("compress.html"))

@app.get("/merge")
async def route_merge():
    return FileResponse(find_html_file("merge.html"))


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
