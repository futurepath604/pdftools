import os
import pandas as pd
import pdfplumber

def convert_pdf_to_excel(input_path: str, output_path: str):
    """Extracts tables or raw text from PDF into structured Excel sheets safely."""
    all_tables = []
    
    with pdfplumber.open(input_path) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            for table in tables:
                if table:
                    cleaned_table = [[str(cell) if cell is not None else "" for cell in row] for row in table]
                    all_tables.append(pd.DataFrame(cleaned_table))
                    
    if all_tables:
        with pd.ExcelWriter(output_path) as writer:
            for idx, df in enumerate(all_tables):
                df.to_excel(writer, sheet_name=f"Table_{idx+1}", index=False, header=False)
    else:
        fallback_data = []
        with pdfplumber.open(input_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    for line in text.split('\n'):
                        if line.strip():
                            columns = line.split('\t') if '\t' in line else [line.strip()]
                            fallback_data.append(columns)
                            
        if not fallback_data:
            fallback_data = [["No structural data or text layers detected in source PDF file."]]
            
        df = pd.DataFrame(fallback_data)
        df.to_excel(output_path, index=False, header=False)
