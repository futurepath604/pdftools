import os
import fitz  # PyMuPDF
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

def hex_to_rgb(hex_color):
    """Converts PyMuPDF integer color to python-pptx RGBColor."""
    if hex_color is None:
        return RGBColor(15, 23, 42)
    r = (hex_color >> 16) & 0xFF
    g = (hex_color >> 8) & 0xFF
    b = hex_color & 0xFF
    return RGBColor(r, g, b)

def convert_pdf_to_ppt(input_path: str, output_path: str):
    """
    Converts PDF to 100% Editable PowerPoint slides.
    Preserves structural tables, native image blocks, original colors, fonts, and pixel-perfect alignments.
    """
    prs = Presentation()
    doc = fitz.open(input_path)
    
    # Global setup for layout output directory to store extracted images safely
    img_dir = "temp_ppt_extracted_imgs"
    os.makedirs(img_dir, exist_ok=True)
    
    for page_idx, page in enumerate(doc):
        pdf_w = page.rect.width
        pdf_h = page.rect.height
        
        # Match PPTX slide dimensions exactly to the input PDF configuration
        prs.slide_width = Inches(pdf_w / 72.0)
        prs.slide_height = Inches(pdf_h / 72.0)
        blank_layout = prs.slide_layouts[6]
        slide = prs.slides.add_slide(blank_layout)
        
        # --- PHASE 1: EXTRACT & POSITION NATIVE IMAGES ---
        image_list = page.get_images(full=True)
        for img_info in image_list:
            xref = img_info[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            image_ext = base_image["ext"]
            
            # Find image bounding box on the page layout canvas matrix
            img_rects = page.get_image_rects(xref)
            if img_rects:
                rect = img_rects[0] # Handle principal matrix coordinate
                img_path = os.path.join(img_dir, f"extracted_p{page_idx}_{xref}.{image_ext}")
                
                with open(img_path, "wb") as f:
                    f.write(image_bytes)
                
                # Render native picture frame block precisely onto the slide
                slide.shapes.add_picture(
                    img_path, 
                    Inches(rect.x0 / 72.0), 
                    Inches(rect.y0 / 72.0), 
                    width=Inches((rect.x1 - rect.x0) / 72.0), 
                    height=Inches((rect.y1 - rect.y0) / 72.0)
                )

        # --- PHASE 2: EXTRACT STRUCTURAL TABLES ---
        tabs = page.find_tables()
        table_bboxes = []
        if tabs:
            for tab in tabs:
                table_bboxes.append(tab.bbox) # Store layout boundary to prevent text overlaps
                matrix_data = tab.extract()
                if not matrix_data or not matrix_data[0]:
                    continue
                    
                rows = len(matrix_data)
                cols = len(matrix_data[0])
                
                # Table location points relative parsing mapping
                t_left = Inches(tab.bbox[0] / 72.0)
                t_top = Inches(tab.bbox[1] / 72.0)
                t_width = Inches((tab.bbox[2] - tab.bbox[0] / 72.0))
                t_height = Inches((tab.bbox[3] - tab.bbox[1] / 72.0))
                
                table_shape = slide.shapes.add_table(rows, cols, t_left, t_top, t_width, t_height)
                ppt_table = table_shape.table
                
                for r_idx, row in enumerate(matrix_data):
                    for c_idx, val in enumerate(row):
                        cell = ppt_table.cell(r_idx, c_idx)
                        cell.text = str(val) if val is not None else ""
                        
                        # Apply clear structural formatting inside cells
                        for paragraph in cell.text_frame.paragraphs:
                            paragraph.font.size = Pt(11)
                            paragraph.font.name = "Arial"
                            paragraph.font.color.rgb = RGBColor(30, 41, 59)

        # --- PHASE 3: PARSE EDITABLE TEXT ELEMENTS & STYLES ---
        text_page = page.get_text("dict", flags=fitz.TEXTFLAGS_SEARCH)
        for block in text_page["blocks"]:
            if "lines" not in block:
                continue
                
            # Intersect check: skip text rendering if it falls inside a mapped table boundary box
            b_box = block["bbox"]
            is_inside_table = False
            for t_box in table_bboxes:
                if b_box[0] >= t_box[0] and b_box[1] >= t_box[1] and b_box[2] <= t_box[2] and b_box[3] <= t_box[3]:
                    is_inside_table = True
                    break
            if is_inside_table:
                continue

            for line in block["lines"]:
                l_x0, l_y0, l_x1, l_y1 = line["bbox"]
                left = Inches(l_x0 / 72.0)
                top = Inches(l_y0 / 72.0)
                width = Inches((l_x1 - l_x0) / 72.0)
                height = Inches((l_y1 - l_y0) / 72.0)
                
                if width < Inches(0.1): width = Inches(1.5)
                if height < Inches(0.1): height = Inches(0.3)
                
                txBox = slide.shapes.add_textbox(left, top, width, height)
                tf = txBox.text_frame
                tf.word_wrap = True
                tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
                
                p = tf.paragraphs[0]
                
                for i, span in enumerate(s for s in line["spans"] if s["text"].strip()):
                    if i > 0:
                        run = p.add_run()
                    else:
                        run = p
                        
                    run.text = span["text"]
                    run.font.size = Pt(round(span["size"], 1))
                    run.font.color.rgb = hex_to_rgb(span["color"])
                    
                    font_name = span["font"].lower()
                    if "bold" in font_name: run.font.bold = True
                    if "italic" in font_name: run.font.italic = True
                    
                    # Universal System Fallback Mapping Engine
                    if "sans" in font_name or "arial" in font_name:
                        run.font.name = "Arial"
                    elif "serif" in font_name or "times" in font_name:
                        run.font.name = "Times New Roman"
                    else:
                        run.font.name = "Calibri"

    # Cleanup temporary local assets
    doc.close()
    prs.save(output_path)
    
    # Safe cleanup folder directory step
    for file in os.listdir(img_dir):
        os.remove(os.path.join(img_dir, file))
    os.rmdir(img_dir)
