import os

def convert_pdf_to_excel(input_path: str, output_path: str):
    """
    Advanced Table-Grid Layout PDF to Structured Multi-Column Excel Converter.
    - Uses pdfplumber's geometric table extraction to align cells properly.
    - Handles messy dashboard visuals without collapsing data into Column A.
    - Locks formatting properties uniformly to Calibri, Font Size 9, and enables gridlines.
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

    # Initialize workbook structures
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Partner Dashboard"
    
    # Enforce standard spreadsheet layout with visible gridlines
    ws.views.sheetView[0].showGridLines = True
    
    font_config = Font(name="Calibri", size=9)
    align_left = Alignment(horizontal="left", vertical="center", wrap_text=False)
    
    current_row_idx = 1

    # Extract structured tables using geometric visual mapping
    with pdfplumber.open(input_path) as pdf:
        for page in pdf.pages:
            # First try extracting formatted tables directly
            tables = page.extract_tables({
                "vertical_strategy": "text",
                "horizontal_strategy": "text",
                "intersection_y_tolerance": 3,
                "intersection_x_tolerance": 3
            })
            
            if tables:
                for table in tables:
                    for row in table:
                        # Clean cells and filter out complete empty rows
                        cleaned_row = [str(cell).strip() if cell is not None else "" for cell in row]
                        if not any(cleaned_row):
                            continue
                            
                        for col_idx, cell_value in enumerate(cleaned_row, start=1):
                            if cell_value:
                                cell_obj = ws.cell(row=current_row_idx, column=col_idx, value=cell_value)
                                cell_obj.font = font_config
                                cell_obj.alignment = align_left
                        current_row_idx += 1
                    current_row_idx += 1  # Add a clean row gap between different dashboard blocks
            else:
                # Fallback for plain text dashboard filters
                text = page.extract_text()
                if text:
                    for line in text.split("\n"):
                        if not line.strip():
                            continue
                        # If pipeline marks are present, split horizontally across cells
                        if "|" in line:
                            row_cells = [c.strip() for c in line.split("|")]
                        else:
                            row_cells = [c.strip() for c in line.split("  ") if c.strip()]
                            
                        for col_idx, cell_value in enumerate(row_cells, start=1):
                            cell_obj = ws.cell(row=current_row_idx, column=col_idx, value=cell_value)
                            cell_obj.font = font_config
                            cell_obj.alignment = align_left
                        current_row_idx += 1

    # Safe layout check: insert data notice if file parsing fetched nothing
    if current_row_idx == 1:
        ws.cell(row=1, column=1, value="No tabular entries detected in the dashboard report.").font = font_config

    # Dynamic Adaptive Autofit Columns Algorithm to prevent text clipping
    for col in ws.columns:
        max_len = 0
        col_letter = get_column_letter(col[0].column)
        for cell in col:
            if cell.value:
                max_len = max(max_len, len(str(cell.value)))
        ws.column_dimensions[col_letter].width = max(max_len + 3, 12)

    wb.save(output_path)
