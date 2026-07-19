import os
from collections import defaultdict

def convert_pdf_to_excel(input_path: str, output_path: str):
    """
    True Tabular Layout PDF to Multi-Column Excel Converter.
    - Groups words sharing visual horizontal rows by checking alignment baselines.
    - Uses adaptive horizontal tracking intervals to split text columns into separate cells.
    - Locks configuration settings uniformly to Calibri, Font Size 9, and enables gridlines.
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
    ws.title = "Partner Dashboard Details"
    
    ws.views.sheetView[0].showGridLines = True
    font_config = Font(name="Calibri", size=9)
    align_left = Alignment(horizontal="left", vertical="center")
    
    current_row_idx = 1

    with pdfplumber.open(input_path) as pdf:
        for page in pdf.pages:
            # Step 1: Extract words with explicit spatial bounding positions
            words = page.extract_words(x_tolerance=3, y_tolerance=3)
            if not words:
                continue

            # Group all text items based on identical horizontal row heights
            rows_map = defaultdict(list)
            for w in words:
                # Group text blocks falling inside a 2-pixel vertical tolerance band
                y_baseline = round(w['top'] / 2.0) * 2.0
                rows_map[y_baseline].append(w)

            # Step 2: Sort and map grouped items into separate tabular cells
            for y_key in sorted(rows_map.keys()):
                line_elements = rows_map[y_key]
                # Sort elements from left to right along the X-axis
                line_elements.sort(key=lambda item: item['x0'])
                
                cells_list = []
                active_cell_text = ""
                previous_x1 = None

                for element in line_elements:
                    text_chunk = element['text']
                    
                    # If the chunk is a pipeline grid divider, ignore it but trigger a new column
                    if text_chunk == "|":
                        if active_cell_text.strip():
                            cells_list.append(active_cell_text.strip())
                            active_cell_text = ""
                        previous_x1 = element['x1']
                        continue

                    # If the horizontal gap between words is larger than 12 pixels, treat it as a new column
                    if previous_x1 is not None and (element['x0'] - previous_x1) > 12:
                        cells_list.append(active_cell_text.strip())
                        active_cell_text = text_chunk
                    else:
                        active_cell_text += " " + text_chunk if active_cell_text else text_chunk
                    
                    previous_x1 = element['x1']
                
                if active_cell_text.strip():
                    cells_list.append(active_cell_text.strip())

                # Step 3: Write structured columns cleanly into the worksheet
                if cells_list and any(c for c in cells_list):
                    for col_idx, cell_value in enumerate(cells_list, start=1):
                        cell_obj = ws.cell(row=current_row_idx, column=col_idx, value=str(cell_value))
                        cell_obj.font = font_config
                        cell_obj.alignment = align_left
                    current_row_idx += 1

    if current_row_idx == 1:
        ws.cell(row=1, column=1, value="No tabular entries detected in the dashboard report.").font = font_config

    # Step 4: Dynamically auto-adjust column width metrics
    for col in ws.columns:
        max_len = 0
        col_letter = get_column_letter(col[0].column)
        for cell in col:
            if cell.value:
                max_len = max(max_len, len(str(cell.value)))
        ws.column_dimensions[col_letter].width = max(max_len + 4, 12)

    wb.save(output_path)
