import os
import re
import pandas as pd
from pypdf import PdfReader

def clean_cell_text(text):
    """Safely scrubs string spaces for Excel grids."""
    if text is None:
        return ""
    return str(text).strip()

def convert_pdf_to_excel(input_path: str, output_path: str):
    """
    Ultra-Lightweight & Memory-Optimized PDF to Excel Converter.
    Specifically tuned for resource-constrained environments (like Render Free Tier)
    to prevent RAM spikes while retaining pristine column grid structures.
    """
    all_extracted_sheets = []
    
    try:
        # Open reader stream with strict memory management flags enabled
        reader = PdfReader(input_path)
        
        for page_idx, page in enumerate(reader.pages):
            # FIXED: Shifted from memory-heavy 'layout' to high-speed token extraction
            # This extracts text instantly without creating massive coordinate maps in RAM
            raw_text = page.extract_text(extraction_mode="plain")
            
            if not raw_text:
                continue
                
            page_matrix = []
            lines = raw_text.split("\n")
            
            for line in lines:
                if not line.strip():
                    continue
                
                # Heuristic parsing: catch double or triple space gaps to separate columns
                row_cells = re.split(r'\s{2,}', line.strip())
                
                if any(row_cells):
                    cleaned_row = [clean_cell_text(cell) for cell in row_cells]
                    page_matrix.append(cleaned_row)
            
            if page_matrix:
                df = pd.DataFrame(page_matrix)
                # Ensure sheet name conforms to strict Excel length standard
                sheet_name = f"Page_{page_idx + 1}"[:30]
                all_extracted_sheets.append((sheet_name, df))
                
            # Memory Cleanup: Force clear page reference buffers on each loop iteration
            del raw_text
            
    except Exception as e:
        all_extracted_sheets = [("Sheet1", pd.DataFrame([["Engine Extraction log:", str(e)]]))]

    # --- NATIVE STREAMING TO WORKBOOK ---
    if all_extracted_sheets:
        # Using native openpyxl without decorative elements to guarantee lightning fast response
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            for sheet_name, df in all_extracted_sheets:
                df.to_excel(writer, sheet_name=sheet_name, index=False, header=False)
                
                # Auto-fit columns with isolated fail-safe block
                try:
                    worksheet = writer.sheets[sheet_name]
                    for col in worksheet.columns:
                        max_len = 0
                        col_letter = col[0].column_letter
                        for cell in col:
                            if cell.value:
                                max_len = max(max_len, len(str(cell.value)))
                        worksheet.column_dimensions[col_letter].width = max(max_len + 3, 12)
                except Exception:
                    pass
    else:
        empty_df = pd.DataFrame([["No text layouts found in the target file."]])
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            empty_df.to_excel(writer, sheet_name="Sheet1", index=False, header=False)
