import io
from fastapi import APIRouter, File, UploadFile, Form, HTTPException
from fastapi.responses import StreamingResponse
from pypdf import PdfReader, PdfWriter

# main.py যেন এটি ইম্পোর্ট করতে পারে, সেজন্য 'router' ডিফাইন করা হলো
router = APIRouter(prefix="/api", tags=["Compress"])

def compress_pdf_logic(input_bytes: bytes, quality: str = "medium") -> io.BytesIO:
    """
    মেমরিতে পিডিএফ হাই-স্পিডে কম্প্রেস করার বাগ-ফ্রি পাইথন লজিক।
    """
    try:
        reader = PdfReader(io.BytesIO(input_bytes))
        writer = PdfWriter()
        
        for page in reader.pages:
            writer.add_page(page)
            
        for page in writer.pages:
            page.compress_content_streams()
            
        output_stream = io.BytesIO()
        writer.write(output_stream)
        output_stream.seek(0)
        
        if len(output_stream.getvalue()) >= len(input_bytes) and quality == "high":
            fallback = io.BytesIO(input_bytes)
            fallback.seek(0)
            return fallback
            
        return output_stream
    except Exception:
        fallback = io.BytesIO(input_bytes)
        fallback.seek(0)
        return fallback

# FastAPI Endpoint যা ফ্রন্টএন্ড থেকে রিকোয়েস্ট রিসিভ করবে
@router.post("/compress")
async def compress_pdf(file: UploadFile = File(...), quality: str = Form("medium")):
    try:
        # আপলোড করা ফাইলের বাইটস রিড করা
        file_bytes = await file.read()
        
        # আপনার কোর লজিক রান করা
        compressed_stream = compress_pdf_logic(file_bytes, quality=quality)
        
        # ব্রাউজারে কম্প্রেসড ফাইলটি রেসপন্স হিসেবে পাঠানো
        return StreamingResponse(
            compressed_stream,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=compressed_{file.filename}"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Compression failed: {str(e)}")
