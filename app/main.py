from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse
from app.tools.compressor import compress_pdf_logic
import os

app = FastAPI()

# ফ্রন্টএন্ড স্ট্যাটিক ফাইল মাউন্ট করা
app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/")
async def read_index():
    return FileResponse('app/static/index.html')

@app.post("/api/compress")
async def api_compress(file: UploadFile = File(...)):
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="শুধুমাত্র PDF ফাইল সাপোর্ট করে।")
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
        raise HTTPException(status_code=500, detail="Error processing PDF")
