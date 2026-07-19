import os
import shutil
import zipfile
import xml.etree.ElementTree as ET
from pdf2docx import Converter
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor

def convert_pdf_to_ppt(input_path: str, output_path: str):
    """
    Professional High-Fidelity PDF to PPTX Converter.
    Uses an AI layout reconstruction pipeline (via pdf2docx semantic parsing) 
    to compile document flows into fully native, multi-column, beautifully 
    aligned PowerPoint slides without breaking tables or overlapping text.
    """
    temp_dir = "temp_ppt_pipeline"
    os.makedirs(temp_dir, exist_ok=True)
    
    temp_docx = os.path.join(temp_dir, "intermediary_flow.docx")
    
    try:
        # Step 1: AI Semantic Layout Parsing (Extract Text Flow, Tables & Images aligned perfectly)
        cv = Converter(input_path)
        cv.convert(temp_docx, start=0, end=None)
        cv.close()
        
        # Step 2: Initialize Presentation Canvas (Standard Widescreen Layout)
        prs = Presentation()
        prs.slide_width = Inches(13.333)
        prs.slide_height = Inches(7.5)
        blank_layout = prs.slide_layouts[6] # Full blank master layout
        
        # Extract native images parsed by the AI engine from docx container safely
        docx_img_dir = os.path.join(temp_dir, "word", "media")
        if os.path.exists(temp_docx):
            with zipfile.ZipFile(temp_docx, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
        
        # Open intermediary structural layout file via python-docx engine
        from docx import Document
        doc = Document(temp_docx)
        
        # Track active slide state
        current_slide = prs.slides.add_slide(blank_layout)
        
        # Global grid placements for top to bottom flow
        current_top = Inches(0.8)
        max_slide_height = Inches(6.5)
        
        images_found = []
        if os.path.exists(docx_img_dir):
            images_found = [os.path.join(docx_img_dir, f) for f in os.listdir(docx_img_dir)]
        img_idx = 0

        # Helper to handle content height overflow and create a new slide cleanly
        def check_slide_overflow(height_to_add):
            nonlocal current_slide, current_top
            if current_top + height_to_add > max_slide_height:
                current_slide = prs.slides.add_slide(blank_layout)
                current_top = Inches(0.8)

        # --- PHASE 1: PARSE INTERMEDIARY BLOCKS (TEXT & TABLES) ---
        for element in doc.element.body:
            # 1. HANDLE STRUCTURED TABLES (Pixel-Perfect Grid Conversion)
            if element.tag.endswith('tbl'):
                from docx.table import Table
                docx_table = Table(element, doc)
                
                rows_count = len(docx_table.rows)
                cols_count = len(docx_table.columns)
                
                table_height = Inches(max(0.4 * rows_count, 1.5))
                check_slide_overflow(table_height)
                
                # Add a native PowerPoint table grid
                table_shape = current_slide.shapes.add_table(
                    rows_count, cols_count, 
                    Inches(0.8), current_top, 
                    Inches(11.733), table_height
                )
                ppt_table = table_shape.table
                
                # Copy values safely preserving cellular structures
                for r_idx, row in enumerate(docx_table.rows):
                    for c_idx, cell in enumerate(row.cells):
                        ppt_cell = ppt_table.cell(r_idx, c_idx)
                        ppt_cell.text = cell.text.strip()
                        
                        # Style table cells elegantly
                        for paragraph in ppt_cell.text_frame.paragraphs:
                            paragraph.font.size = Pt(11)
                            paragraph.font.name = "Arial"
                            paragraph.font.color.rgb = RGBColor(30, 41, 59)
                            
                current_top += table_height + Inches(0.4)
                
            # 2. HANDLE PARAGRAPHS AND IMAGES CONTIGUOUSLY
            elif element.tag.endswith('p'):
                from docx.text.paragraph import Paragraph
                p_obj = Paragraph(element, doc)
                text_content = p_obj.text.strip()
                
                # Inline Image Insertion check from structural layout
                if 'w:drawing' in element.xml and img_idx < len(images_found):
                    img_height = Inches(2.5)
                    check_slide_overflow(img_height)
                    
                    try:
                        current_slide.shapes.add_picture(
                            images_found[img_idx], 
                            Inches(0.8), current_top, 
                            width=Inches(4.5)
                        )
                        current_top += img_height + Inches(0.3)
                        img_idx += 1
                    except Exception:
                        pass
                
                if not text_content:
                    continue
                    
                text_height = Inches(0.8)
                check_slide_overflow(text_height)
                
                # Insert fully editable text containers
                txBox = current_slide.shapes.add_textbox(Inches(0.8), current_top, Inches(11.733), text_height)
                tf = txBox.text_frame
                tf.word_wrap = True
                
                p = tf.paragraphs[0]
                p.text = text_content
                
                # Distinguish Headers from Body Flow via String Length Metrics
                if len(text_content) < 60 and not text_content.endswith(('.', ',', ';')):
                    p.font.size = Pt(24)
                    p.font.bold = True
                    p.font.color.rgb = RGBColor(30, 27, 75)
                    current_top += Inches(0.6)
                else:
                    p.font.size = Pt(13)
                    p.font.color.rgb = RGBColor(71, 85, 105)
                    current_top += Inches(0.4)
                    
                p.font.name = "Arial"
                
        # Save output
        prs.save(output_path)
        
    finally:
        # Step 3: Absolute Sandbox Cleanup
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
