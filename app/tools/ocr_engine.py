import os
import io
import shutil
from fastapi import APIRouter, File, UploadFile, Form, HTTPException
from fastapi.responses import FileResponse
import pytesseract
from pdf2image import convert_from_path
import pypdf

# Create a clean dedicated router for the OCR Engine tool
router = APIRouter(prefix="/api", tags=["PDF OCR"])

def process_pdf_ocr(input_path: str, output_path: str, lang: str = "eng") -> bool:
    """
    Converts a non-searchable scanned PDF into a searchable PDF using Tesseract OCR.
    Optimized to handle PDF layers directly in memory using BytesIO.
    """
    try:
        # ১. পিডিএফ ফাইলকে ইমেজে রূপান্তর করা (300 DPI অপ্টিমাল কোয়ালিটির জন্য)
        images = convert_from_path(input_path, dpi=300)
        
        pdf_writer = pypdf.PdfWriter()

        # ২. প্রতিটি পেজ ইমেজে OCR রান করে পিডিএফ পেজ জেনারেট করা
        for img in images:
            # Tesseract দিয়ে ইমেজকে সরাসরি টেক্সট এম্বেডেড পিডিএফ বাইটস জেনারেট করা
            page_pdf_bytes = pytesseract.image_to_pdf_or_hocr(img, extension='pdf', lang=lang)
            
            # ইন-মেমোরি BytesIO ব্যবহার করে pypdf এ পেজ যুক্ত করা (ডিস্ক ক্লিনআপের ঝামেলা নেই)
            page_stream = io.BytesIO(page_pdf_bytes)
            reader = pypdf.PdfReader(page_stream)
            pdf_writer.add_page(reader.pages[0])

        # ৩. মার্জ করা সার্চেবল পিডিএফ ফাইল রাইট করা
        with open(output_path, "wb") as out_f:
            pdf_writer.write(out_f)
            
        pdf_writer.close()
        return True
    except Exception:
        return False


# Self-contained API routing logic for OCR
@router.post("/ocr")
async def api_pdf_ocr(
    file: UploadFile = File(...),
    lang: str = Form("eng")
):
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported for OCR.")

    input_path = f"temp_ocr_in_{file.filename}"
    output_filename = f"searchable_{file.filename}"
    output_path = f"temp_ocr_out_{output_filename}"
    
    # Save uploaded file to temp directory
    with open(input_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    try:
        success = process_pdf_ocr(input_path, output_path, lang=lang)
        if not success:
            raise HTTPException(status_code=500, detail="OCR engine failed to make the PDF searchable.")
            
        return FileResponse(
            output_path, 
            media_type="application/pdf", 
            filename=output_filename,
            headers={"Content-Disposition": f"attachment; filename={output_filename}"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OCR Engine Error: {str(e)}")
    finally:
        # Clean up filesystem artifacts safely
        if os.path.exists(input_path):
            try: os.remove(input_path)
            except: pass
