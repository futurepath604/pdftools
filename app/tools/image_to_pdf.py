import os
from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
from PIL import Image

router = APIRouter(prefix="/api/tools", tags=["Image to PDF"])
TEMP_DIR = "/tmp"
os.makedirs(TEMP_DIR, exist_ok=True)

@router.post("/image-to-pdf")
async def convert_images_to_pdf(files: list[UploadFile] = File(...)):
    if not files:
        raise HTTPException(status_code=400, detail="No images uploaded")
    
    image_paths = []
    output_filename = "converted_images.pdf"
    output_path = os.path.join(TEMP_DIR, output_filename)
    
    try:
        for file in files:
            temp_path = os.path.join(TEMP_DIR, file.filename)
            with open(temp_path, "wb") as buffer:
                buffer.write(await file.read())
            image_paths.append(temp_path)
            
        images = []
        for path in image_paths:
            img = Image.open(path)
            if img.mode != 'RGB':
                img = img.convert('RGB')
            images.append(img)
            
        if images:
            images[0].save(output_path, save_all=True, append_images=images[1:])
            
        return FileResponse(output_path, media_type="application/pdf", filename=output_filename)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image to PDF conversion failed: {str(e)}")
