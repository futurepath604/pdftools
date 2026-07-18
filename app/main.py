from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse
from app.tools.compressor import compress_pdf_logic
import os

app = FastAPI()

# সার্ভারের ভেতরের আসল ফোল্ডার পাথ নিখুঁতভাবে ট্র্যাক করা
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
INDEX_HTML = os.path.join(STATIC_DIR, "index.html")

# স্ট্যাটিক ফোল্ডার মাউন্ট করা
if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/")
async def read_index():
    if os.path.exists(INDEX_HTML):
        return FileResponse(INDEX_HTML)
    return {"error": "Frontend UI file not found in the static directory."}

@app.post("/api/compress")
async def api_compress(file: UploadFile = File(...)):
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="দয়া করে শুধুমাত্র PDF ফাইল আপলোড করুন।")
    try:
        content = await file.read()
        if len(content) > 15 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="ফাইল সাইজ ১৫ মেগাবাইটের বেশি হওয়া যাবে না।")
        
        # আপনার মডুলার কম্প্রেসার ইঞ্জিন কল করা
        output_stream = compress_pdf_logic(content)
        
        return StreamingResponse(
            output_stream, 
            media_type="application/pdf", 
            headers={"Content-Disposition": f"attachment; filename=compressed_{file.filename}"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
