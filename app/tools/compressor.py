import fitz  # PyMuPDF
from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
import os, tempfile

router = APIRouter()

@router.post("/api/tools/compress")
async def compress_pdf(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        doc = fitz.open(stream=contents, filetype="pdf")
        
        fd, output_path = tempfile.mkstemp(suffix=".pdf")
        os.close(fd)
        
        # garbage=4 এবং deflate=True দিয়ে সর্বোচ্চ কম্প্রেশন নিশ্চিত করা
        doc.save(output_path, garbage=4, deflate=True)
        doc.close()
        
        return FileResponse(output_path, media_type="application/pdf", filename=f"compressed_{file.filename}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
