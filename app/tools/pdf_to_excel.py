import os
import re

def convert_pdf_to_excel(input_path: str, output_path: str):
    """
    Dashboard-Optimized PDF to Tabular Excel Converter.
    - Specifically designed to parse horizontal data structures separated by vertical bars '|'.
    - Implements direct openpyxl row feeding to ensure clean separation into separate cells.
    - Locks formatting properties globally to Calibri, Font Size 9, and forces standard gridlines.
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

    # Step 1: Initialize openpyxl structures directly to bypass data compression issues
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Partner Dashboard Details"
    
    # Enforce standard spreadsheet layout with visible gridlines
    ws.views.sheetView[0].showGridLines = True
    
    font_config = Font(name="Calibri", size=9)
    align_left = Alignment(horizontal="left", vertical="center")
    
    current_row_idx = 1

    # Step 2: Extract text components page by page using fine visual layouts
    with pdfplumber.open(input_path) as pdf:
        for page in pdf.pages:
            raw_text = page.extract_text(layout=True)
            if not raw_text:
                continue
                
            lines = raw_text.split("\n")
            for line in lines:
                if not line.strip():
                    continue
                
                # Check if the line is explicitly separated by pipeline matrix markers
                if "|" in line:
                    row_cells = [cell.strip() for cell in line.split("|")]
                else:
                    # Fallback for header parameters blocks: split by 2 or more space blocks
                    row_cells = [cell.strip() for cell in re.split(r'\s{2,}', line.strip()) if cell.strip()]
                
                if row_cells:
                    # Inject data sequentially into separate column cells
                    for col_idx, cell_value in enumerate(row_cells, start=1):
                        cell = ws.cell(row=current_row_idx, column=col_idx, value=str(cell_value))
                        cell.font = font_config
                        cell.alignment = align_left
                    current_row_idx += 1

    # Safe layout check: insert data notice if file parsing fetched nothing
    if current_row_idx == 1:
        ws.cell(row=1, column=1, value="No dashboard report entries detected.").font = font_config

    # Step 3: Dynamic Adaptive Autofit Columns Algorithm
    for col in ws.columns:
        max_len = 0
        col_letter = get_column_letter(col[0].column)
        for cell in col:
            if cell.value:
                max_len = max(max_len, len(str(cell.value)))
        # Allocate spacing buffer so large titles/numbers don't clip
        ws.column_dimensions[col_letter].width = max(max_len + 3, 12)

    # Step 4: Output stream to clean Excel spreadsheet format
    wb.save(output_path)
