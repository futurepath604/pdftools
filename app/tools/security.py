import os
from fastapi import APIRouter, File, UploadFile, Form, HTTPException
from fastapi.responses import FileResponse
from pypdf import PdfReader, PdfWriter

router = APIRouter(prefix="/api/tools", tags=["Security"])
TEMP_DIR = "/tmp"
os.makedirs(TEMP_DIR, exist_ok=True)

@router.post("/lock")
async def lock_pdf(file: UploadFile = File(...), password: str = Form(...)):
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Invalid file format.")
    
    input_path = os.path.join(TEMP_DIR, file.filename)
    output_path = os.path.join(TEMP_DIR, f"locked_{file.filename}")
    
    try:
        with open(input_path, "wb") as buffer:
            buffer.write(await file.read())
            
        reader = PdfReader(input_path)
        writer = PdfWriter()
        writer.append_pages_from_reader(reader)
        writer.encrypt(password)
        
        with open(output_path, "wb") as f:
            writer.write(f)
            
        return FileResponse(output_path, media_type="application/pdf", filename=f"locked_{file.filename}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Locking failed: {str(e)}")

@router.post("/unlock")
async def unlock_pdf(file: UploadFile = File(...), password: str = Form(...)):
    input_path = os.path.join(TEMP_DIR, file.filename)
    output_path = os.path.join(TEMP_DIR, f"unlocked_{file.filename}")
    
    try:
        with open(input_path, "wb") as buffer:
            buffer.write(await file.read())
            
        reader = PdfReader(input_path)
        if reader.is_encrypted:
            reader.decrypt(password)
            
        writer = PdfWriter()
        for page in reader.pages:
            writer.add_page(page)
            
        with open(output_path, "wb") as f:
            writer.write(f)
            
        return FileResponse(output_path, media_type="application/pdf", filename=f"unlocked_{file.filename}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unlock failed. Incorrect password or corrupted file.")
