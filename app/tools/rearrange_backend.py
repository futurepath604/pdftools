import os
from fastapi import APIRouter, File, UploadFile, Form, HTTPException
from fastapi.responses import FileResponse
from pypdf import PdfReader, PdfWriter

router = APIRouter(prefix="/api/tools", tags=["Rearrange Pages"])
TEMP_DIR = "/tmp"
os.makedirs(TEMP_DIR, exist_ok=True)

@router.post("/rearrange")
async def rearrange_pdf(file: UploadFile = File(...), pages: str = Form(...)):
    # Pages should be a comma-separated string like "2,0,1" (0-indexed)
    input_path = os.path.join(TEMP_DIR, file.filename)
    output_filename = f"rearranged_{file.filename}"
    output_path = os.path.join(TEMP_DIR, output_filename)
    
    try:
        with open(input_path, "wb") as buffer:
            buffer.write(await file.read())
            
        reader = PdfReader(input_path)
        writer = PdfWriter()
        
        page_indices = [int(p.strip()) for p in pages.split(",")]
        
        for idx in page_indices:
            if 0 <= idx < len(reader.pages):
                writer.add_page(reader.pages[idx])
                
        with open(output_path, "wb") as f:
            writer.write(f)
            
        return FileResponse(output_path, media_type="application/pdf", filename=output_filename)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Rearranging pages failed: {str(e)}")
