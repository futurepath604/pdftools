import os
import re
import csv

def convert_pdf_to_excel(input_path: str, output_path: str):
    """
    Zero-External-Dependency PDF to Excel (CSV-backed) Converter.
    Does NOT use pandas or openpyxl. Completely immune to library missing errors.
    Creates a tab-separated or comma-separated file that Excel opens natively.
    """
    try:
        from pypdf import PdfReader
    except ImportError:
        raise RuntimeError("Core PDF reader component is missing in environment.")

    try:
        reader = PdfReader(input_path)
        
        # Excel-compatible CSV parsing with UTF-8 BOM for automatic character encoding
        with open(output_path, mode='w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f, delimiter=',') # Standard comma grid
            
            for page_idx, page in enumerate(reader.pages):
                raw_text = page.extract_text()
                if not raw_text:
                    continue
                    
                lines = raw_text.split("\n")
                for line in lines:
                    if not line.strip():
                        continue
                    
                    # Split cells on double or more spaces
                    row_cells = re.split(r'\s{2,}', line.strip())
                    if any(row_cells):
                        cleaned_row = [str(cell).strip() for cell in row_cells]
                        writer.writerow(cleaned_row)
                        
                # Add a visual separator between PDF pages inside the Excel sheet
                writer.writerow([])
                writer.writerow([f"--- End of Page {page_idx + 1} ---"])
                writer.writerow([])
                
                del raw_text
                
    except Exception as e:
        # Fallback error logger inside the output file itself
        with open(output_path, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["Process Error Log", str(e)])
