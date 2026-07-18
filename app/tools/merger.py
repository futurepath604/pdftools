import io
from typing import List
from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import StreamingResponse
from pypdf import PdfMerger

# main.py যেন এটি সহজেই ইম্পোর্ট করতে পারে, সেজন্য 'router' ডিফাইন করা হলো
router = APIRouter(prefix="/api", tags=["Merge"])

def merge_pdfs_logic(pdf_files_bytes: List[bytes]) -> io.BytesIO:
    """
    মেমরিতে একাধিক পিডিএফ ফাইল নির্দিষ্ট সিকোয়েন্সে জোড়া দেওয়ার পাইথন লজিক।
    """
    try:
        merger = PdfMerger()
        
        for file_bytes in pdf_files_bytes:
            merger.append(io.BytesIO(file_bytes))
            
        output_stream = io.BytesIO()
        merger.write(output_stream)
        merger.close()
        output_stream.seek(0)
        return output_stream
        
    except Exception as e:
        raise RuntimeError(f"PDF Merge করতে সমস্যা হয়েছে: {str(e)}")

# FastAPI Endpoint যা ফ্রন্টএন্ড থেকে মাল্টিপল ফাইল রিসিভ করবে
@router.post("/merge")
async def merge_pdfs(files: List[UploadFile] = File(...)):
    if len(files) < 2:
        raise HTTPException(status_code=400, detail="Please upload at least 2 PDF files to merge.")
    
    try:
        pdf_files_bytes = []
        for file in files:
            # নিশ্চিত করা হচ্ছে যেন ফাইলটি পিডিএফ হয়
            if not file.filename.lower().endswith('.pdf'):
                raise HTTPException(status_code=400, detail=f"File '{file.filename}' is not a valid PDF.")
            bytes_data = await file.read()
            pdf_files_bytes.append(bytes_data)
        
        # কোর মার্জ লজিক কল করা হচ্ছে
        merged_stream = merge_pdfs_logic(pdf_files_bytes)
        
        # জোড়া লাগানো ফাইলটি ব্রাউজারে ডাউনলোড রেসপন্স হিসেবে পাঠানো
        return StreamingResponse(
            merged_stream,
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=merged_document.pdf"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Merging failed: {str(e)}")
