import io
from typing import List
from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import StreamingResponse
import pypdf

# Create a clean dedicated router for PDF Merging tool
router = APIRouter(prefix="/api", tags=["Merge"])

def merge_pdfs_logic(pdf_files_bytes: List[bytes]) -> io.BytesIO:
    """
    মেমরিতে একাধিক পিডিএফ ফাইল নির্দিষ্ট সিকোয়েন্সে জোড়া দেওয়ার পাইথন লজিক (pypdf compatibility ফিক্সড)।
    """
    try:
        # pypdf-এর নতুন ভার্সনে PdfWriter দিয়েই মার্জ করা সবচেয়ে নিরাপদ ও রিকমেন্ডেড
        merger = pypdf.PdfWriter()
        
        for file_bytes in pdf_files_bytes:
            if len(file_bytes) == 0:
                continue
            merger.append(io.BytesIO(file_bytes))
            
        output_stream = io.BytesIO()
        merger.write(output_stream)
        merger.close()
        output_stream.seek(0)
        return output_stream
        
    except Exception as e:
        raise RuntimeError(f"PDF Merge করতে সমস্যা হয়েছে: {str(e)}")

@router.post("/merge")
async def merge_pdfs(files: List[UploadFile] = File(...)):
    if len(files) < 2:
        raise HTTPException(status_code=400, detail="Please upload at least 2 PDF files to merge.")
    
    try:
        pdf_files_bytes = []
        for file in files:
            if not file.filename.lower().endswith('.pdf'):
                raise HTTPException(status_code=400, detail=f"File '{file.filename}' is not a valid PDF.")
            
            bytes_data = await file.read()
            pdf_files_bytes.append(bytes_data)
        
        merged_stream = merge_pdfs_logic(pdf_files_bytes)
        
        if merged_stream.getbuffer().nbytes == 0:
            raise HTTPException(status_code=400, detail="Merging resulted in an empty file. Ensure source PDFs are valid.")
            
        return StreamingResponse(
            merged_stream,
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=merged_document.pdf"}
        )
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Merging failed: {str(e)}")
