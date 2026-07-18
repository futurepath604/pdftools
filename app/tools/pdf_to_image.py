import io
import zipfile
from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import StreamingResponse
from pdf2image import convert_from_bytes

# main.py যেন এটি ইম্পোর্ট করতে পারে, সেজন্য 'router' ডিফائن করা হলো
router = APIRouter(prefix="/api", tags=["PDF to Image"])

def pdf_to_images_zip_logic(pdf_bytes: bytes) -> io.BytesIO:
    """
    পিডিএফের প্রতিটি পেজকে জেপিজি ছবিতে কনভার্ট করে একটি ZIP ফাইল বানিয়ে মেমরিতেই রিটার্ন করার লজিক।
    """
    images = convert_from_bytes(pdf_bytes, dpi=150)
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for idx, img in enumerate(images):
            img_buffer = io.BytesIO()
            img.save(img_buffer, format="JPEG")
            img_buffer.seek(0)
            zip_file.writestr(f"page_{idx + 1}.jpg", img_buffer.getvalue())
            
    zip_buffer.seek(0)
    return zip_buffer

# FastAPI Endpoint যা ফ্রন্টএন্ড থেকে পিডিএফ ফাইলটি রিসিভ করবে
@router.post("/pdf-to-image")
async def pdf_to_image(file: UploadFile = File(...)):
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Uploaded file must be a PDF.")
        
    try:
        # আপলোড করা ফাইলের বাইটস রিড করা
        pdf_bytes = await file.read()
        
        # কোর লজিক রান করে জিপ ফাইল বাফার নেওয়া
        zip_stream = pdf_to_images_zip_logic(pdf_bytes)
        
        # ব্রাউজারে জিপ ফাইলটি ডাউনলোড রেসপন্স হিসেবে পাঠানো
        return StreamingResponse(
            zip_stream,
            media_type="application/zip",
            headers={"Content-Disposition": f"attachment; filename={file.filename.replace('.pdf', '_images.zip')}"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF to Image conversion failed: {str(e)}")
