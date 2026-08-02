import os
import pdfplumber
import pandas as pd
from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import FileResponse

router = APIRouter(prefix="/api/tools", tags=["PDF to Excel"])
TEMP_DIR = "/tmp"
os.makedirs(TEMP_DIR, exist_ok=True)

@router.post("/pdf-to-excel")
async def convert_pdf_to_excel(file: UploadFile = File(...)):
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    input_path = os.path.join(TEMP_DIR, file.filename)
    output_filename = f"{os.path.splitext(file.filename)[0]}.xlsx"
    output_path = os.path.join(TEMP_DIR, output_filename)
    
    try:
        with open(input_path, "wb") as buffer:
            buffer.write(await file.read())
            
        all_tables = []
        with pdfplumber.open(input_path) as pdf:
            for page in pdf.pages:
                tables = page.extract_tables()
                for table in tables:
                    df = pd.DataFrame(table)
                    all_tables.append(df)
                    
        if not all_tables:
            raise HTTPException(status_code=400, detail="No tables found in the PDF to convert.")
            
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            for i, df in enumerate(all_tables):
                df.to_excel(writer, sheet_name=f"Sheet_{i+1}", index=False, header=False)
                
        return FileResponse(output_path, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", filename=output_filename)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF to Excel conversion failed: {str(e)}")
