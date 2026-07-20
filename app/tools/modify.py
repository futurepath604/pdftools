import json
from io import BytesIO
from fastapi import APIRouter, File, UploadFile, Form, HTTPException
from fastapi.responses import StreamingResponse
import pypdf

# Create a clean dedicated router for PDF Modification tools (Split, Rotate, Delete Pages)
router = APIRouter(prefix="/api", tags=["Modify PDF"])

@router.post("/modify-pdf")
async def modify_pdf(
    file: UploadFile = File(...), 
    mode: str = Form(...), 
    params: str = Form(...)
):
    try:
        pdf_bytes = await file.read()
        if not pdf_bytes:
            raise HTTPException(status_code=400, detail="Uploaded file is empty.")

        reader = pypdf.PdfReader(BytesIO(pdf_bytes))
        writer = pypdf.PdfWriter()
        
        # Safely parse JSON parameters with fallback
        try:
            config = json.loads(params)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid JSON format in params.")
        
        total_pages = len(reader.pages)
        
        # --- MODE 1: SPLIT PAGES ---
        if mode == "split":
            target_pages = config.get("pages", [])
            if not target_pages:
                raise HTTPException(status_code=400, detail="No pages specified for splitting.")
            for idx in target_pages:
                if 0 <= idx < total_pages:
                    writer.add_page(reader.pages[idx])
                    
        # --- MODE 2: ROTATE PAGES ---
        elif mode == "rotate":
            angle = config.get("angle", 90)
            if angle % 90 != 0:
                raise HTTPException(status_code=400, detail="Rotation angle must be a multiple of 90.")
            for page in reader.pages:
                # Direct rotation can alter original reference safely via pypdf
                page.rotate(angle)
                writer.add_page(page)
                
        # --- MODE 3: DELETE PAGES ---
        elif mode == "delete_pages":
            skip_pages = config.get("pages", [])
            for idx in range(total_pages):
                if idx not in skip_pages:
                    writer.add_page(reader.pages[idx])
        else:
            raise HTTPException(status_code=400, detail="Invalid modification mode.")

        # Check if the output has at least one page
        if len(writer.pages) == 0:
            raise HTTPException(status_code=400, detail="The operation resulted in a PDF with 0 pages.")

        out_buf = BytesIO()
        writer.write(out_buf)
        writer.close()
        out_buf.seek(0)

        return StreamingResponse(
            out_buf, 
            media_type="application/pdf", 
            headers={"Content-Disposition": f"attachment; filename=modified_{file.filename}"}
        )
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Modification failed: {str(e)}")
