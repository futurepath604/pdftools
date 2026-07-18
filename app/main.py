from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse
from app.tools.compressor import compress_pdf_logic
import os

app = FastAPI()

# ১. ব্যাকএন্ড এপিআই রাউট (সবার আগে প্রসেস হবে)
@app.post("/api/compress")
async def api_compress(file: UploadFile = File(...)):
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="শুধুমাত্র PDF ফাইল সাপোর্ট করে।")
    try:
        content = await file.read()
        if len(content) > 15 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="ফাইল সাইজ ১৫ মেগাবাইটের বেশি হওয়া যাবে না।")
        
        # পিডিএফ কম্প্রেস করার লজিক
        output_stream = compress_pdf_logic(content)
        
        return StreamingResponse(
            output_stream, 
            media_type="application/pdf", 
            headers={"Content-Disposition": f"attachment; filename=compressed_{file.filename}"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ২. ফ্রন্টএন্ড UI রাউট (পাথ ইন্ডিপেন্ডেন্ট)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
INDEX_HTML = os.path.join(STATIC_DIR, "index.html")

@app.get("/")
async def read_index():
    if os.path.exists(INDEX_HTML):
        return FileResponse(INDEX_HTML)
    return {"error": "Frontend UI file not found."}

# স্ট্যাটিক ফোল্ডার মাউন্ট (যদি অন্য কোনো এসেট থাকে)
if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
