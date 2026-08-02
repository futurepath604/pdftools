import os
from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
from pdf2docx import Converter

router = APIRouter(prefix="/api/tools", tags=["PDF to Word"])
TEMP_DIR = "/tmp"
os.makedirs(TEMP_DIR, exist_ok=True)

@router.post("/pdf-to-word")
async def convert_pdf_to_word(file: UploadFile = File(...)):
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    input_path = os.path.join(TEMP_DIR, file.filename)
    output_filename = f"{os.path.splitext(file.filename)[0]}.docx"
    output_path = os.path.join(TEMP_DIR, output_filename)
    
    try:
        with open(input_path, "wb") as buffer:
            buffer.write(await file.read())
            
        cv = Converter(input_path)
        cv.convert(output_path, start=0, end=None)
        cv.close()
        
        return FileResponse(output_path, media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document", filename=output_filename)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF to Word conversion failed: {str(e)}")
