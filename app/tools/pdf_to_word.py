from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
from pdf2docx import Converter
import os, tempfile

router = APIRouter()

@router.post("/api/tools/pdf-to-word")
async def pdf_to_word(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        
        # ইনপুট এবং আউটপুট টেম্পোরারি ফাইল তৈরি
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as pdf_tmp:
            pdf_tmp.write(contents)
            pdf_path = pdf_tmp.name
            
        docx_path = pdf_path.replace(".pdf", ".docx")
        
        cv = Converter(pdf_path)
        cv.convert(docx_path, start=0, end=None)
        cv.close()
        
        # ক্লিনআপ পিডিএফ টেম্পোরারি ফাইল
        os.unlink(pdf_path)
        
        return FileResponse(docx_path, media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document", filename=file.filename.replace(".pdf", ".docx"))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
