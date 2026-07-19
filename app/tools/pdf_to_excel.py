import os

def convert_pdf_to_excel(input_path: str, output_path: str):
    """
    Advanced Tabular-Aware PDF to Excel Converter.
    - Extracts actual tables with proper column boundaries using pdfplumber.
    - Merges all extracted rows into a Single unified Worksheet.
    - Fallback engine preserves structural text rows if no formal tables are found.
    """
    try:
        import pdfplumber
    except ImportError:
        raise RuntimeError("Core layout parsing engine (pdfplumber) is missing in environment.")

    try:
        import pandas as pd
    except ImportError:
        raise RuntimeError("Data compilation engine (pandas) is missing in environment.")

    master_rows = []

    try:
        with pdfplumber.open(input_path) as pdf:
            for page in pdf.pages:
                # 1. Try extracting explicit graphical tables first
                tables = page.extract_tables()
                
                if tables:
                    for table in tables:
                        for row in table:
                            # Clean cells (Remove None values and trailing whitespace)
                            cleaned_row = [str(cell).strip() if cell is not None else "" for cell in row]
                            # Only add rows that contain actual data
                            if any(cleaned_row):
                                master_rows.append(cleaned_row)
                else:
                    # 2. Fallback: Extract words with precise geometric positioning if no clear table lines exist
                    text = page.extract_text(layout=True)
                    if text:
                        for line in text.split("\n"):
                            if line.strip():
                                # Target structural data separating fields cleanly
                                row_cells = [cell.strip() for cell in line.split("   ") if cell.strip()]
                                if row_cells:
                                    master_rows.append(row_cells)
    except Exception as parse_error:
        master_rows = [["Layout Analysis Error", str(parse_error)]]

    # Export compiled data structure to Single Sheet Excel
    try:
        if not master_rows:
            master_rows = [["Notice", "No extractable tabular data found in source PDF."]]

        df = pd.DataFrame(master_rows)
        
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name="Source Layout Data", index=False, header=False)
            
            # Dynamic grid column autowidth implementation
            worksheet = writer.sheets["Source Layout Data"]
            for col in worksheet.columns:
                max_len = 0
                for cell in col:
                    if cell.value:
                        max_len = max(max_len, len(str(cell.value)))
                col_letter = col[0].column_letter
                worksheet.column_dimensions[col_letter].width = max(max_len + 3, 12)

    except Exception as export_error:
        raise RuntimeError(f"Excel Generation failure: {str(export_error)}")
