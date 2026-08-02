import fitz
from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
import os, tempfile

router = APIRouter()

@router.post("/api/tools/merge")
async def merge_pdfs(files: list[UploadFile] = File(...)):
    try:
        merged_doc = fitz.open()
        
        for file in files:
            contents = await file.read()
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(contents)
                tmp_path = tmp.name
            
            partial_doc = fitz.open(tmp_path)
            merged_doc.insert_pdf(partial_doc)
            partial_doc.close()
            os.unlink(tmp_path)
            
        fd, output_path = tempfile.mkstemp(suffix=".pdf")
        os.close(fd)
        merged_doc.save(output_path)
        merged_doc.close()
        
        return FileResponse(output_path, media_type="application/pdf", filename="merged_document.pdf")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
