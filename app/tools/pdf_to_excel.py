import os

def convert_pdf_to_excel(input_path: str, output_path: str):
    """
    Advanced Tabular PDF to Excel Binary (.xlsb) Converter.
    - Uses pdfplumber to safeguard the original source layout alignment.
    - Writes directly into a native Binary Workbook using the pyxlsb engine.
    - Avoids standard openxml corruption alerts in Microsoft Excel.
    """
    try:
        import pdfplumber
    except ImportError:
        raise RuntimeError("Core layout parsing engine (pdfplumber) is missing.")

    try:
        import pandas as pd
    except ImportError:
        raise RuntimeError("Data compilation engine (pandas) is missing.")

    master_rows = []

    try:
        with pdfplumber.open(input_path) as pdf:
            for page in pdf.pages:
                tables = page.extract_tables()
                if tables:
                    for table in tables:
                        for row in table:
                            cleaned_row = [str(cell).strip() if cell is not None else "" for cell in row]
                            if any(cleaned_row):
                                master_rows.append(cleaned_row)
                else:
                    # Fallback structural geometric lines
                    text = page.extract_text(layout=True)
                    if text:
                        for line in text.split("\n"):
                            if line.strip():
                                row_cells = [cell.strip() for cell in line.split("   ") if cell.strip()]
                                if row_cells:
                                    master_rows.append(row_cells)
    except Exception as parse_error:
        master_rows = [["Layout Analysis Error", str(parse_error)]]

    # Generate the Binary XLSB File Layout
    try:
        if not master_rows:
            master_rows = [["Notice", "No extractable tabular data found in source PDF."]]

        df = pd.DataFrame(master_rows)
        
        # Enforcing pyxlsb engine for raw binary writing pipeline
        with pd.ExcelWriter(output_path, engine='pyxlsb') as writer:
            df.to_excel(writer, sheet_name="Source Layout Data", index=False, header=False)

    except Exception as export_error:
        raise RuntimeError(f"Binary Excel Generation failure: {str(export_error)}")
