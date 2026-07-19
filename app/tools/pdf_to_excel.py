import os
import re
import shutil
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse

# Create a dedicated router for this tool
router = APIRouter(prefix="/api", tags=["Excel Converter"])

def convert_pdf_to_excel(input_path: str, output_path: str):
    """
    Advanced Table-Grid Layout PDF to Structured Multi-Column Excel Converter.
    """
    try:
        import pdfplumber
    except ImportError:
        raise RuntimeError("Missing pdfplumber dependency.")
        
    try:
        import openpyxl
        from openpyxl.styles import Font, Alignment
        from openpyxl.utils import get_column_letter
    except ImportError:
        raise RuntimeError("Missing openpyxl dependency.")

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Partner Dashboard"
    ws.views.sheetView[0].showGridLines = True
    
    font_config = Font(name="Calibri", size=9)
    align_left = Alignment(horizontal="left", vertical="center", wrap_text=False)
    current_row_idx = 1

    with pdfplumber.open(input_path) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables({
                "vertical_strategy": "text",
                "horizontal_strategy": "text",
                "intersection_y_tolerance": 3,
                "intersection_x_tolerance": 3
            })
            
            if tables:
                for table in tables:
                    for row in table:
                        cleaned_row = [str(cell).strip() if cell is not None else "" for cell in row]
                        if not any(cleaned_row):
                            continue
                        for col_idx, cell_value in enumerate(cleaned_row, start=1):
                            if cell_value:
                                cell_obj = ws.cell(row=current_row_idx, column=col_idx, value=cell_value)
                                cell_obj.font = font_config
                                cell_obj.alignment = align_left
                        current_row_idx += 1
                    current_row_idx += 1
            else:
                text = page.extract_text()
                if text:
                    for line in text.split("\n"):
                        if not line.strip():
                            continue
                        if "|" in line:
                            row_cells = [c.strip() for c in line.split("|")]
                        else:
                            row_cells = [c.strip() for c in line.split("  ") if c.strip()]
                            
                        for col_idx, cell_value in enumerate(row_cells, start=1):
                            cell_obj = ws.cell(row=current_row_idx, column=col_idx, value=cell_value)
                            cell_obj.font = font_config
                            cell_obj.alignment = align_left
                        current_row_idx += 1

    if current_row_idx == 1:
        ws.cell(row=1, column=1, value="No tabular entries detected in the dashboard report.").font = font_config

    for col in ws.columns:
        max_len = 0
        col_letter = get_column_letter(col[0].column)
        for cell in col:
            if cell.value:
                max_len = max(max_len, len(str(cell.value)))
        ws.column_dimensions[col_letter].width = max(max_len + 3, 12)

    wb.save(output_path)


# The API endpoint is now self-contained inside the tool file!
@router.post("/pdf-to-excel")
async def api_pdf_to_excel(file: UploadFile = File(...)):
    input_path = f"temp_{file.filename}"
    output_filename = f"{os.path.splitext(file.filename)[0]}.xlsx"
    output_path = output_filename
    
    with open(input_path, "wb") as buffer: 
        shutil.copyfileobj(file.file, buffer)
        
    try:
        convert_pdf_to_excel(input_path, output_path)
        return FileResponse(
            output_path, 
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", 
            filename=output_filename,
            headers={"Content-Disposition": f"attachment; filename={output_filename}"}
        )
    except Exception as e: 
        raise HTTPException(status_code=500, detail=f"Excel Engine Error: {str(e)}")
    finally:
        if os.path.exists(input_path): 
            try: os.remove(input_path)
            except: pass
