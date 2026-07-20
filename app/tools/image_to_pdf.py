import os
from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import StreamingResponse
from typing import List
from PIL import Image
from io import BytesIO

# Dedicated clean router for Image to PDF
router = APIRouter(prefix="/api", tags=["Image to PDF"])

@router.post("/image-to-pdf")
async def image_to_pdf(files: List[UploadFile] = File(...)):
    images = []
    try:
        for file in files:
            img_bytes = await file.read()
            if not img_bytes:
                continue
            img = Image.open(BytesIO(img_bytes)).convert("RGB")
            images.append(img)
            
        if not images:
            raise HTTPException(status_code=400, detail="No valid images uploaded.")
            
        out_buf = BytesIO()
        # Save the primary image and append the rest as multi-page PDF layers
        images[0].save(out_buf, format="PDF", save_all=True, append_images=images[1:])
        out_buf.seek(0)
        
        return StreamingResponse(
            out_buf, 
            media_type="application/pdf", 
            headers={"Content-Disposition": "attachment; filename=images_converted.pdf"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image conversion failed: {str(e)}")
    finally:
        # Memory Optimization: Explicitly close opened PIL frames to clear runtime heap
        for img in images:
            try:
                img.close()
            except:
                pass
