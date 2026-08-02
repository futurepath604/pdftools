import pdfplumber
import pandas as pd
from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
import tempfile, os

router = APIRouter()

@router.post("/api/tools/pdf-to-excel")
async def pdf_to_excel(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(contents)
            tmp_path = tmp.name
            
        all_tables = []
        with pdfplumber.open(tmp_path) as pdf:
            for page in pdf.pages:
                tables = page.extract_tables()
                for table in tables:
                    df = pd.DataFrame(table)
                    all_tables.append(df)
                    
        os.unlink(tmp_path)
        
        if not all_tables:
            raise HTTPException(status_code=400, detail="No tables found in PDF to convert.")
            
        fd, excel_path = tempfile.mkstemp(suffix=".xlsx")
        os.close(fd)
        
        # প্রথম টেবিল বা সব টেবিল কনক্যাট করে এক্সেল সেভ করা
        with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
            for idx, df in enumerate(all_tables):
                df.to_excel(writer, sheet_name=f'Sheet_{idx+1}', index=False, header=False)
                
        return FileResponse(excel_path, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", filename=file.filename.replace(".pdf", ".xlsx"))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
