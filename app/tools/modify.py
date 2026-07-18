from fastapi import APIRouter, File, UploadFile, Form, HTTPException
from fastapi.responses import StreamingResponse
import pypdf
import json
from io import BytesIO

router = APIRouter(prefix="/api", tags=["Modify PDF"])

@router.post("/modify-pdf")
async def modify_pdf(file: UploadFile = File(...), mode: str = Form(...), params: str = Form(...)):
    try:
        pdf_bytes = await file.read()
        reader = pypdf.PdfReader(BytesIO(pdf_bytes))
        writer = pypdf.PdfWriter()
        config = json.loads(params)
        
        if mode == "split":
            target_pages = config.get("pages", [])
            for idx in target_pages:
                if 0 <= idx < len(reader.pages):
                    writer.add_page(reader.pages[idx])
                    
        elif mode == "rotate":
            angle = config.get("angle", 90)
            for page in reader.pages:
                page.rotate(angle)
                writer.add_page(page)
                
        elif mode == "delete_pages":
            skip_pages = config.get("pages", [])
            for idx in range(len(reader.pages)):
                if idx not in skip_pages:
                    writer.add_page(reader.pages[idx])
        else:
            raise HTTPException(status_code=400, detail="Invalid modification mode.")

        out_buf = BytesIO()
        writer.write(out_buf)
        out_buf.seek(0)

        return StreamingResponse(
            out_buf, 
            media_type="application/pdf", 
            headers={"Content-Disposition": f"attachment; filename=modified_{file.filename}"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Modification failed: {str(e)}")

