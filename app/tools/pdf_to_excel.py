import os
from collections import defaultdict

def convert_pdf_to_excel(input_path: str, output_path: str):
    """
    AI-Optimized Geometrical PDF to Tabular Excel Converter.
    - Groups words by their precise vertical and horizontal coordinate bounds.
    - Ensures multi-column alignments are perfectly preserved without row compression.
    - Formats the consolidated sheet uniformly with Font Size 9.
    """
    try:
        import pdfplumber
    except ImportError:
        raise RuntimeError("Missing pdfplumber dependency.")
        
    try:
        import pandas as pd
    except ImportError:
        raise RuntimeError("Missing pandas dependency.")

    all_rows = []

    with pdfplumber.open(input_path) as pdf:
        for page in pdf.pages:
            # First, check if a clean tabular graph exists natively
            tables = page.extract_tables()
            if tables:
                for table in tables:
                    for row in table:
                        if row and any(cell is not None and str(cell).strip() for cell in row):
                            all_rows.append([str(cell).strip() if cell else "" for cell in row])
                continue

            # Advanced AI Fallback: Parse structural coordinate bounds if extract_tables fails
            words = page.extract_words(x_tolerance=3, y_tolerance=3)
            if not words:
                continue

            # Group words that share nearly identical vertical (top) baselines
            lines_dict = defaultdict(list)
            for w in words:
                # Rounding to cluster items belonging to the same visual horizontal line
                top_coord = round(w['top'], 1)
                lines_dict[top_coord].append(w)

            # Sort lines chronologically from top to bottom
            for top_coord in sorted(lines_dict.keys()):
                line_words = lines_dict[top_coord]
                # Sort words inside the line from left to right (x0 bound)
                line_words.sort(key=lambda x: x['x0'])
                
                # Consolidate strings that are too close, separate those that belong to new columns
                row_cells = []
                current_cell = ""
                last_x1 = None

                for w in line_words:
                    if last_x1 is not None and (w['x0'] - last_x1) > 8:
                        # Significant horizontal gap implies a new column matrix field
                        row_cells.append(current_cell.strip())
                        current_cell = w['text']
                    else:
                        current_cell += " " + w['text'] if current_cell else w['text']
                    last_x1 = w['x1']
                
                if current_cell:
                    row_cells.append(current_cell.strip())

                if row_cells and any(cell for cell in row_cells):
                    all_rows.append(row_cells)

    if not all_rows:
        all_rows = [["Data Extraction Status", "No clean graphical or coordinate rows found."]]

    # Step 2: Formulate structured DataFrame
    df = pd.DataFrame(all_rows)

    # Step 3: Extract and promote the first non-empty structural row as column headers
    for i, row in df.iterrows():
        if any(str(cell).strip() != '' for cell in row):
            df.columns = row
            df = df.drop(i).reset_index(drop=True)
            break

    # Step 4 & 5: Save workbook matrix and enforce font configurations cleanly
    try:
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name="Partner Onboarding", index=False)
            
            worksheet = writer.sheets["Partner Onboarding"]
            
            from openpyxl.styles import Font
            font_config = Font(name="Calibri", size=9)
            
            # Formatting cells uniformly
            for row in worksheet.iter_rows(min_row=1, max_row=worksheet.max_row, min_col=1, max_col=worksheet.max_column):
                for cell in row:
                    cell.font = font_config

            # Force gridlines visibility
            worksheet.views.sheetView[0].showGridLines = True
            
            # Dynamic calculation of spacing widths
            from openpyxl.utils import get_column_letter
            for col in worksheet.columns:
                max_len = 0
                col_letter = get_column_letter(col[0].column)
                for cell in col:
                    if cell.value:
                        max_len = max(max_len, len(str(cell.value)))
                worksheet.column_dimensions[col_letter].width = max(max_len + 4, 12)

    except Exception as export_error:
        raise RuntimeError(f"Excel Coordinate Rendering failure: {str(export_error)}")
