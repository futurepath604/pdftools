import os
import re
import pandas as pd
import pdfplumber

def clean_cell_text(text):
    """Cleans up raw parsed strings from PDF layers into pristine sheet text."""
    if text is None:
        return ""
    # Normalize whitespaces and remove unnecessary linebreaks within a single cell
    cleaned = re.sub(r'\s+', ' ', str(text))
    return cleaned.strip()

def convert_pdf_to_excel(input_path: str, output_path: str):
    """
    Professional High-Fidelity PDF to Excel Converter.
    Employs an advanced heuristic grid parsing engine to locate structural tables,
    resolve multi-line cell overflows, and align data matrix columns perfectly.
    """
    all_sheets_data = []
    
    with pdfplumber.open(input_path) as pdf:
        for page_idx, page in enumerate(pdf.pages):
            # AI-Style Heuristic Grid Configurations for high accuracy table boundary detection
            table_settings = {
                "vertical_strategy": "lines",
                "horizontal_strategy": "lines",
                "intersection_tolerance": 3,
                "snap_tolerance": 4,
                "join_tolerance": 3,
                "edge_min_length": 5
            }
            
            # First try: Extract strict structural tables based on explicit borders/lines
            extracted_tables = page.extract_tables(table_settings=table_settings)
            
            # Fallback Strategy: If no hard-lined tables found, attempt borderless text-alignment parsing
            if not extracted_tables or all(len(t) == 0 for t in extracted_tables):
                fallback_settings = {
                    "vertical_strategy": "text",
                    "horizontal_strategy": "text",
                    "snap_tolerance": 3,
                    "join_tolerance": 3
                }
                extracted_tables = page.extract_tables(table_settings=fallback_settings)
            
            # Process successfully localized tables
            if extracted_tables:
                for t_idx, table in enumerate(extracted_tables):
                    if not table or len(table) == 0:
                        continue
                        
                    # Clean and rebuild matrix cells without losing spacing properties
                    processed_matrix = []
                    for row in table:
                        processed_row = [clean_cell_text(cell) for cell in row]
                        # Only append if the row is not entirely empty placeholders
                        if any(processed_row):
                            processed_matrix.append(processed_row)
                            
                    if processed_matrix:
                        df = pd.DataFrame(processed_matrix)
                        sheet_name = f"Page{page_idx+1}_Table{t_idx+1}"[:30] # Excel sheet name limit constraint
                        all_sheets_data.append((sheet_name, df))
            
            else:
                # Catch-All Safety Flow: If it's a dense text document without grids, parse words line-by-line
                text_content = page.extract_text(layout=False, x_tolerance=3, y_tolerance=3)
                if text_content:
                    page_matrix = []
                    for line in text_content.split('\n'):
                        if line.strip():
                            # Intelligently split by multi-spaces (common in columns without borders)
                            row_cells = re.split(r'\s{2,}', line.strip())
                            if row_cells:
                                page_matrix.append(row_cells)
                                
                    if page_matrix:
                        df = pd.DataFrame(page_matrix)
                        sheet_name = f"Page{page_idx+1}_TextData"[:30]
                        all_sheets_data.append((sheet_name, df))
                        
    # --- WRITE INTERMEDIARY DATASETS INTO PRODUCTION WORKBOOK ---
    if all_sheets_data:
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            for sheet_name, df in all_sheets_data:
                df.to_excel(writer, sheet_name=sheet_name, index=False, header=False)
                
                # Dynamic Auto-Fit Column Width Adjustment Setup for Professional Look
                worksheet = writer.sheets[sheet_name]
                for col in worksheet.columns:
                    max_len = 0
                    col_letter = col[0].column_letter # Get the column name letter safely
                    for cell in col:
                        if cell.value:
                            max_len = max(max_len, len(str(cell.value)))
                    # Apply padded width formatting bounds
                    worksheet.column_dimensions[col_letter].width = max(max_len + 3, 12)
    else:
        # Ultimate Fallback Container for Blank or fully Scanned/Non-OCR files to prevent tool crash
        empty_df = pd.DataFrame([["No readable grid tables or textual layers could be detected in the source PDF."]])
        empty_df.to_excel(output_path, index=False, header=False)
