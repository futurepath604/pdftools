import os

def convert_pdf_to_excel(input_path: str, output_path: str):
    """
    Advanced Layout PDF to Excel Converter inspired by Shyama's Pipeline.
    - Uses pdfplumber to precisely parse tabular layouts into rows.
    - Dynamically detects and promotes the first non-empty row as the header.
    - Formats all output cells directly to Font Size 9 to match source style closely.
    - Keeps everything strictly inside a single unified worksheet.
    """
    try:
        import pdfplumber
    except ImportError:
        raise RuntimeError("Missing pdfplumber library.")
        
    try:
        import pandas as pd
    except ImportError:
        raise RuntimeError("Missing pandas library.")

    all_rows = []

    # Step 1: Extract all structural tables from PDF page by page
    with pdfplumber.open(input_path) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            for table in tables:
                for row in table:
                    # Filter out empty or completely null rows safely
                    if row and any(cell is not None and str(cell).strip() for cell in row):
                        all_rows.append([str(cell).strip() if cell else "" for cell in row])

    if not all_rows:
        all_rows = [["Notice", "No structured tabular data could be extracted from this PDF layout."]]

    # Step 2: Convert to DataFrame
    df = pd.DataFrame(all_rows)

    # Step 3: Use first non-empty row as header
    for i, row in df.iterrows():
        if any(str(cell).strip() != '' for cell in row):
            df.columns = row
            df = df.drop(i).reset_index(drop=True)
            break

    # Step 4 & 5: Export to Excel with custom styling engine directly via ExcelWriter
    # This prevents the server from crashing due to re-opening locked files
    try:
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name="Partner Details", index=False)
            
            # Access openpyxl worksheet context to apply font configuration
            worksheet = writer.sheets["Partner Details"]
            
            from openpyxl.styles import Font
            font_style = Font(name="Calibri", size=9)
            
            # Formatting cells and dynamically tuning grid dimensions
            for row in worksheet.iter_rows(min_row=1, max_row=worksheet.max_row, min_col=1, max_col=worksheet.max_column):
                for cell in row:
                    cell.font = font_style

            # Grid line enablement & column autofitting
            worksheet.views.sheetView[0].showGridLines = True
            from openpyxl.utils import get_column_letter
            for col in worksheet.columns:
                max_len = 0
                col_letter = get_column_letter(col[0].column)
                for cell in col:
                    if cell.value:
                        max_len = max(max_len, len(str(cell.value)))
                worksheet.column_dimensions[col_letter].width = max(max_len + 3, 11)

    except Exception as export_error:
        raise RuntimeError(f"Excel Generation failure: {str(export_error)}")
