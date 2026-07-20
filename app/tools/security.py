import pypdf
from io import BytesIO
from fastapi import APIRouter, File, UploadFile, Form, HTTPException
from fastapi.responses import StreamingResponse

# Dedicated router for Security & Premium tools
router = APIRouter(prefix="/api", tags=["Security & Premium"])

@router.post("/security-pdf")
async def security_pdf(
    file: UploadFile = File(...), 
    mode: str = Form(...), 
    password: str = Form(...)
):
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Uploaded file must be a PDF.")
        
    try:
        pdf_bytes = await file.read()
        if not pdf_bytes:
            raise HTTPException(status_code=400, detail="Uploaded PDF file is empty.")
            
        if mode == "lock":
            reader = pypdf.PdfReader(BytesIO(pdf_bytes))
            writer = pypdf.PdfWriter()
            
            for page in reader.pages:
                writer.add_page(page)
                
            writer.encrypt(password)
            
            out_buf = BytesIO()
            writer.write(out_buf)
            out_buf.seek(0)
            
            safe_filename = f"locked_{file.filename.replace(' ', '_')}"
            return StreamingResponse(
                out_buf, 
                media_type="application/pdf", 
                headers={"Content-Disposition": f"attachment; filename={safe_filename}"}
            )
            
        elif mode == "unlock":
            reader = pypdf.PdfReader(BytesIO(pdf_bytes))
            
            if reader.is_encrypted:
                # Attempt to decrypt with provided credentials
                decrypt_result = reader.decrypt(password)
                if decrypt_result == 0: # 0 indicates failure in pypdf decryption states
                    raise HTTPException(status_code=400, detail="Invalid password. Could not decrypt the PDF.")
            
            writer = pypdf.PdfWriter()
            try:
                for page in reader.pages:
                    writer.add_page(page)
            except Exception:
                raise HTTPException(status_code=400, detail="Decryption failed. Please verify the password.")
                
            out_buf = BytesIO()
            writer.write(out_buf)
            out_buf.seek(0)
            
            safe_filename = f"unlocked_{file.filename.replace(' ', '_')}"
            return StreamingResponse(
                out_buf, 
                media_type="application/pdf", 
                headers={"Content-Disposition": f"attachment; filename={safe_filename}"}
            )
        else:
            raise HTTPException(status_code=400, detail="Invalid security mode specified. Use 'lock' or 'unlock'.")
            
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Security operation failed: {str(e)}")

@router.post("/office-to-pdf")
async def office_to_pdf(file: UploadFile = File(...)):
    raise HTTPException(
        status_code=403, 
        detail="Office-to-PDF direct binary conversion requires LibreOffice subsystem on premium tier."
    )
