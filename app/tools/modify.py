import os
from fastapi import APIRouter, File, UploadFile, Form, HTTPException
from fastapi.responses import FileResponse
from pypdf import PdfReader, PdfWriter

router = APIRouter(prefix="/api/tools", tags=["Modify PDF"])
TEMP_DIR = "/tmp"
os.makedirs(TEMP_DIR, exist_ok=True)

@router.post("/rotate")
async def rotate_pdf(file: UploadFile = File(...), angle: int = Form(90)):
    input_path = os.path.join(TEMP_DIR, file.filename)
    output_filename = f"rotated_{file.filename}"
    output_path = os.path.join(TEMP_DIR, output_filename)
    
    try:
        with open(input_path, "wb") as buffer:
            buffer.write(await file.read())
            
        reader = PdfReader(input_path)
        writer = PdfWriter()
        
        for page in reader.pages:
            page.rotate(angle)
            writer.add_page(page)
            
        with open(output_path, "wb") as f:
            writer.write(f)
            
        return FileResponse(output_path, media_type="application/pdf", filename=output_filename)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Rotation failed: {str(e)}")

@router.post("/delete-pages")
async def delete_pages(file: UploadFile = File(...), pages: str = Form(...)):
    # Comma-separated 0-indexed pages to delete e.g. "0,2"
    input_path = os.path.join(TEMP_DIR, file.filename)
    output_filename = f"modified_{file.filename}"
    output_path = os.path.join(TEMP_DIR, output_filename)
    
    try:
        with open(input_path, "wb") as buffer:
            buffer.write(await file.read())
            
        reader = PdfReader(input_path)
        writer = PdfWriter()
        
        del_indices = [int(p.strip()) for p in pages.split(",")]
        
        for idx, page in enumerate(reader.pages):
            if idx not in del_indices:
                writer.add_page(page)
                
        with open(output_path, "wb") as f:
            writer.write(f)
            
        return FileResponse(output_path, media_type="application/pdf", filename=output_filename)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Deleting pages failed: {str(e)}")
