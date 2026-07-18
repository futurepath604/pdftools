from fastapi import APIRouter, File, UploadFile, Form, HTTPException
from fastapi.responses import StreamingResponse
import pypdf
from io import BytesIO

router = APIRouter(prefix="/api", tags=["Security & Premium"])

@router.post("/security-pdf")
async def security_pdf(file: UploadFile = File(...), mode: str = Form(...), password: str = Form(...)):
    try:
        pdf_bytes = await file.read()
        
        if mode == "lock":
            reader = pypdf.PdfReader(BytesIO(pdf_bytes))
            writer = pypdf.PdfWriter()
            for page in reader.pages:
                writer.add_page(page)
            writer.encrypt(password)
            
            out_buf = BytesIO()
            writer.write(out_buf)
            out_buf.seek(0)
            return StreamingResponse(
                out_buf, 
                media_type="application/pdf", 
                headers={"Content-Disposition": f"attachment; filename=locked_{file.filename}"}
            )
            
        elif mode == "unlock":
            reader = pypdf.PdfReader(BytesIO(pdf_bytes))
            if reader.is_encrypted:
                reader.decrypt(password)
            
            writer = pypdf.PdfWriter()
            for page in reader.pages:
                writer.add_page(page)
                
            out_buf = BytesIO()
            writer.write(out_buf)
            out_buf.seek(0)
            return StreamingResponse(
                out_buf, 
                media_type="application/pdf", 
                headers={"Content-Disposition": f"attachment; filename=unlocked_{file.filename}"}
            )
        else:
            raise HTTPException(status_code=400, detail="Invalid security mode.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Security operation failed: {str(e)}")

@router.post("/office-to-pdf")
async def office_to_pdf(file: UploadFile = File(...)):
    raise HTTPException(
        status_code=403, 
        detail="Office-to-PDF direct binary conversion requires LibreOffice subsystem on premium tier."
    )

