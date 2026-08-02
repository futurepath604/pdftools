import os
import fitz  # PyMuPDF
from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/api/tools", tags=["OCR Engine"])
TEMP_DIR = "/tmp"
os.makedirs(TEMP_DIR, exist_ok=True)

@router.post("/ocr")
async def extract_text_ocr(file: UploadFile = File(...)):
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed for OCR")
    
    input_path = os.path.join(TEMP_DIR, file.filename)
    
    try:
        with open(input_path, "wb") as buffer:
            buffer.write(await file.read())
            
        doc = fitz.open(input_path)
        extracted_text = ""
        for page_num, page in enumerate(doc):
            extracted_text += f"--- Page {page_num + 1} ---\n"
            extracted_text += page.get_text() + "\n\n"
        doc.close()
        
        return JSONResponse(content={"filename": file.filename, "text": extracted_text})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OCR extraction failed: {str(e)}")
