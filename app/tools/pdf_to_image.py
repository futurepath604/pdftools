import os
import fitz  # PyMuPDF
import zipfile
from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import FileResponse

router = APIRouter(prefix="/api/tools", tags=["PDF to Image"])
TEMP_DIR = "/tmp"
os.makedirs(TEMP_DIR, exist_ok=True)

@router.post("/pdf-to-image")
async def convert_pdf_to_image(file: UploadFile = File(...)):
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    input_path = os.path.join(TEMP_DIR, file.filename)
    zip_filename = f"{os.path.splitext(file.filename)[0]}_images.zip"
    zip_path = os.path.join(TEMP_DIR, zip_filename)
    
    try:
        with open(input_path, "wb") as buffer:
            buffer.write(await file.read())
            
        doc = fitz.open(input_path)
        image_files = []
        
        for i, page in enumerate(doc):
            pix = page.get_pixmap(dpi=150)
            img_filename = f"page_{i+1}.png"
            img_path = os.path.join(TEMP_DIR, img_filename)
            pix.save(img_path)
            image_files.append(img_path)
        doc.close()
        
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for img in image_files:
                zipf.write(img, os.path.basename(img))
                
        return FileResponse(zip_path, media_type="application/zip", filename=zip_filename)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF to Image conversion failed: {str(e)}")
