import os
from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
from pypdf import PdfWriter

router = APIRouter(prefix="/api/tools", tags=["Merger"])
TEMP_DIR = "/tmp"
os.makedirs(TEMP_DIR, exist_ok=True)

@router.post("/merge")
async def merge_pdfs(files: list[UploadFile] = File(...)):
    if len(files) < 2:
        raise HTTPException(status_code=400, detail="Please upload at least 2 PDF files to merge.")
    
    merger = PdfWriter()
    output_filename = "merged_document.pdf"
    output_path = os.path.join(TEMP_DIR, output_filename)
    
    try:
        for file in files:
            if not file.filename.endswith('.pdf'):
                continue
            temp_path = os.path.join(TEMP_DIR, file.filename)
            with open(temp_path, "wb") as buffer:
                buffer.write(await file.read())
            merger.append(temp_path)
            
        merger.write(output_path)
        merger.close()
        
        return FileResponse(output_path, media_type="application/pdf", filename=output_filename)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Merge failed: {str(e)}")
