import io
import zipfile
from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import StreamingResponse
from pdf2image import convert_from_bytes

# Dedicated router for PDF to Image tool
router = APIRouter(prefix="/api", tags=["PDF to Image"])

def pdf_to_images_zip_logic(pdf_bytes: bytes) -> io.BytesIO:
    """
    পিডিএফের প্রতিটি পেজকে জেপিজি ছবিতে কনভার্ট করে একটি ZIP ফাইল বানিয়ে মেমরিতেই রিটার্ন করার লজিক।
    """
    try:
        # Converting with 150 DPI for optimal speed and size balance
        images = convert_from_bytes(pdf_bytes, dpi=150)
        
        if not images:
            raise ValueError("The PDF could not be converted. It might be corrupted or empty.")
            
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            for idx, img in enumerate(images):
                img_buffer = io.BytesIO()
                img.save(img_buffer, format="JPEG")
                img_buffer.seek(0)
                zip_file.writestr(f"page_{idx + 1}.jpg", img_buffer.getvalue())
                
                # Memory cleanup for individual image buffers
                img_buffer.close()
                img.close()  # Close PIL handle directly
                
        zip_buffer.seek(0)
        return zip_buffer
    except Exception as e:
        raise RuntimeError(f"Processing conversion failed: {str(e)}")

@router.post("/pdf-to-image")
async def pdf_to_image(file: UploadFile = File(...)):
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Uploaded file must be a PDF.")
        
    try:
        pdf_bytes = await file.read()
        if not pdf_bytes:
            raise HTTPException(status_code=400, detail="Uploaded PDF file is empty.")
            
        zip_stream = pdf_to_images_zip_logic(pdf_bytes)
        
        # Craft safe output filename
        safe_filename = file.filename.rsplit('.', 1)[0] + "_images.zip"
        
        return StreamingResponse(
            zip_stream,
            media_type="application/zip",
            headers={"Content-Disposition": f"attachment; filename={safe_filename}"}
        )
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF to Image conversion failed: {str(e)}")
