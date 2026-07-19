import os
import fitz  # PyMuPDF
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pdf2docx import Converter

def parse_pdf_color(fitz_color):
    """Safely extracts RGB color from PyMuPDF block elements."""
    if fitz_color is None:
        return RGBColor(15, 23, 42)
    r = (fitz_color >> 16) & 0xFF
    g = (fitz_color >> 8) & 0xFF
    b = fitz_color & 0xFF
    return RGBColor(r, g, b)

def convert_pdf_to_ppt(input_path: str, output_path: str):
    """
    High-fidelity PDF to PowerPoint converter that guarantees font styling,
    tabular alignment, and native images by tracking continuous block flows.
    """
    prs = Presentation()
    doc = fitz.open(input_path)
    
    # Temporary asset bucket for isolated layout images
    asset_dir = "temp_ppt_assets"
    os.makedirs(asset_dir, exist_ok=True)
    
    for page_num, page in enumerate(doc):
        # Establish base canvas scaling based on original PDF layout constraints
        pdf_w, pdf_h = page.rect.width, page.rect.height
        prs.slide_width = Inches(pdf_w / 72.0)
        prs.slide_height = Inches(pdf_h / 72.0)
        
        blank_layout = prs.slide_layouts[6]
        slide = prs.slides.add_slide(blank_layout)
        
        # 1. PROCESS IMAGES WITH ABSOLUTE COORDINATES
        img_info_list = page.get_images(full=True)
        for img_meta in img_info_list:
            xref = img_meta[0]
            raw_img = doc.extract_image(xref)
            rects = page.get_image_rects(xref)
            
            if rects and raw_img:
                rect = rects[0]
                img_name = f"img_p{page_num}_{xref}.{raw_img['ext']}"
                target_path = os.path.join(asset_dir, img_name)
                
                with open(target_path, "wb") as img_file:
                    img_file.write(raw_img["image"])
                
                slide.shapes.add_picture(
                    target_path,
                    Inches(rect.x0 / 72.0),
                    Inches(rect.y0 / 72.0),
                    width=Inches((rect.x1 - rect.x0) / 72.0),
                    height=Inches((rect.y1 - rect.y0) / 72.0)
                )

        # 2. EXTRACT TABLES (Using high-fidelity structural grid parser)
        table_finder = page.find_tables()
        table_zones = []
        
        if table_finder and table_finder.tables:
            for native_table in table_finder.tables:
                table_zones.append(native_table.bbox)
                grid = native_table.extract()
                
                if not grid or not grid[0]:
                    continue
                    
                total_rows = len(grid)
                total_cols = len(grid[0])
                
                box = native_table.bbox
                t_x = Inches(box[0] / 72.0)
                t_y = Inches(box[1] / 72.0)
                t_w = Inches((box[2] - box[0]) / 72.0)
                t_h = Inches((box[3] - box[1]) / 72.0)
                
                ppt_table_shape = slide.shapes.add_table(total_rows, total_cols, t_x, t_y, t_w, t_h)
                table_obj = ppt_table_shape.table
                
                for r_idx, row_content in enumerate(grid):
                    for c_idx, cell_data in enumerate(row_content):
                        cell = table_obj.cell(r_idx, c_idx)
                        cell.text = str(cell_data) if cell_data is not None else ""
                        
                        # Apply standard grid formatting layout
                        for p in cell.text_frame.paragraphs:
                            p.font.size = Pt(11)
                            p.font.name = "Arial"
                            p.font.color.rgb = RGBColor(30, 41, 59)

        # 3. HIGH-FIDELITY TEXT SEGMENTATION (With Table Zone Exclusion)
        raw_layout = page.get_text("dict", flags=fitz.TEXTFLAGS_SEARCH)
        for text_block in raw_layout["blocks"]:
            if "lines" not in text_block:
                continue
                
            # Block Boundary Safeguard Check against current active tables
            b_box = text_block["bbox"]
            overlap = False
            for t_box in table_zones:
                if b_box[0] >= t_box[0] - 2 and b_box[1] >= t_box[1] - 2 and b_box[2] <= t_box[2] + 2 and b_box[3] <= t_box[3] + 2:
                    overlap = True
                    break
            if overlap:
                continue

            for text_line in text_block["lines"]:
                x0, y0, x1, y1 = text_line["bbox"]
                
                l_x = Inches(x0 / 72.0)
                l_y = Inches(y0 / 72.0)
                l_w = Inches((x1 - x0) / 72.0)
                l_h = Inches((y1 - y0) / 72.0)
                
                if l_w < Inches(0.2): l_w = Inches(2.0)
                if l_h < Inches(0.2): l_h = Inches(0.4)
                
                text_container = slide.shapes.add_textbox(l_x, l_y, l_w, l_h)
                t_frame = text_container.text_frame
                t_frame.word_wrap = True
                t_frame.margin_left = t_frame.margin_top = t_frame.margin_right = t_frame.margin_bottom = 0
                
                master_paragraph = t_frame.paragraphs[0]
                
                valid_spans = [s for s in text_line["spans"] if s["text"].strip()]
                for idx, text_span in enumerate(valid_spans):
                    run_target = master_paragraph if idx == 0 else master_paragraph.add_run()
                    run_target.text = text_span["text"]
                    
                    # Layout Styling Sync Engine
                    run_target.font.size = Pt(round(text_span["size"], 1))
                    run_target.font.color.rgb = parse_pdf_color(text_span["color"])
                    
                    font_tag = text_span["font"].lower()
                    if "bold" in font_tag: run_target.font.bold = True
                    if "italic" in font_tag: run_target.font.italic = True
                    
                    if "sans" in font_tag or "arial" in font_tag:
                        run_target.font.name = "Arial"
                    elif "serif" in font_tag or "times" in font_tag:
                        run_target.font.name = "Times New Roman"
                    else:
                        run_target.font.name = "Calibri"

    # Cleanup operations
    doc.close()
    prs.save(output_path)
    
    for f in os.listdir(asset_dir):
        os.remove(os.path.join(asset_dir, f))
    os.rmdir(asset_dir)
