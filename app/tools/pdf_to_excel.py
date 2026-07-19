import os
import re

def convert_pdf_to_excel(input_path: str, output_path: str):
    """
    Advanced Consolidated PDF to Excel Converter.
    - Merges ALL pages into a Single Worksheet (No multiple sheets).
    - Preserves row and column tabular structures from the source file.
    - Autofits columns to ensure data doesn't clip or overlap.
    """
    try:
        from pypdf import PdfReader
    except ImportError:
        raise RuntimeError("Core PDF reader component (pypdf) is missing in environment.")

    try:
        import pandas as pd
    except ImportError:
        raise RuntimeError("Data processing engine (pandas) is missing in environment.")

    # Master list to hold rows from ALL pages combined
    master_data_matrix = []
    
    try:
        reader = PdfReader(input_path)
        
        for page in reader.pages:
            raw_text = page.extract_text()
            if not raw_text:
                continue
                
            lines = raw_text.split("\n")
            for line in lines:
                if not line.strip():
                    continue
                
                # Dynamic regex to detect column gaps (2 or more spaces)
                # This keeps rows together just like the source file layout
                row_cells = re.split(r'\s{2,}', line.strip())
                if any(row_cells):
                    cleaned_row = [str(cell).strip() for cell in row_cells]
                    master_data_matrix.append(cleaned_row)
                    
            del raw_text
            
    except Exception as parse_error:
        master_data_matrix = [["Parsing Error occurred", str(parse_error)]]

    # Export to a clean Single Sheet Excel File
    try:
        if master_data_matrix:
            # Create a uniform DataFrame from all accumulated rows
            df = pd.DataFrame(master_data_matrix)
            
            # Write to a single sheet ("Document Data")
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name="Document Data", index=False, header=False)
                
                # Professional Touch: Auto-fit column widths dynamically to prevent clipping
                worksheet = writer.sheets["Document Data"]
                for col in worksheet.columns:
                    max_len = 0
                    for cell in col:
                        if cell.value:
                            max_len = max(max_len, len(str(cell.value)))
                    # Add a padding of 3 spaces for a professional spaced look
                    col_letter = col[0].column_letter
                    worksheet.column_dimensions[col_letter].width = max(max_len + 3, 12)
                    
    except Exception as export_error:
        # Ultimate fail-safe to avoid application crash
        raise RuntimeError(f"Failed to generate unified Excel structure: {str(export_error)}")
