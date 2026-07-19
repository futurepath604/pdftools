import os
import fitz  # PyMuPDF
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN

def hex_to_rgb(hex_color):
    """Converts PyMuPDF int color to python-pptx RGBColor."""
    if hex_color is None:
        return RGBColor(15, 23, 42) # Default dark slate text
    # Extract RGB bytes
    r = (hex_color >> 16) & 0xFF
    g = (hex_color >> 8) & 0xFF
    b = hex_color & 0xFF
    return RGBColor(r, g, b)

def convert_pdf_to_ppt(input_path: str, output_path: str):
    """
    Converts PDF to PowerPoint keeping native text elements fully editable
    while matching original fonts, sizes, text colors, and absolute alignments.
    """
    prs = Presentation()
    
    # Open PDF document to extract layout metrics
    doc = fitz.open(input_path)
    
    for page in doc:
        # Get PDF Page Size (Points)
        pdf_w = page.rect.width
        pdf_h = page.rect.height
        
        # Set PPTX Slide dimensions dynamically to match the PDF aspect ratio
        prs.slide_width = Inches(pdf_w / 72.0)
        prs.slide_height = Inches(pdf_h / 72.0)
        blank_layout = prs.slide_layouts[6]
        slide = prs.slides.add_slide(blank_layout)
        
        # Extract detailed layout structures including spans, fonts, and bounding boxes
        text_page = page.get_text("dict", flags=fitz.TEXTFLAGS_SEARCH)
        
        for block in text_page["blocks"]:
            if "lines" not in block:
                continue # Skip image blocks for pure editable text processing
                
            for line in block["lines"]:
                # Calculate absolute position mapping from PDF Points to PPTX Inches
                l_x0, l_y0, l_x1, l_y1 = line["bbox"]
                left = Inches(l_x0 / 72.0)
                top = Inches(l_y0 / 72.0)
                width = Inches((l_x1 - l_x0) / 72.0)
                height = Inches((l_y1 - l_y0) / 72.0)
                
                # Safeguard for zero-width/height line bounding boxes
                if width < Inches(0.1): width = Inches(1.0)
                if height < Inches(0.1): height = Inches(0.4)
                
                # Create a native PPTX textbox at the exact matching coordinate
                txBox = slide.shapes.add_textbox(left, top, width, height)
                tf = txBox.text_frame
                tf.word_wrap = True
                tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
                
                p = tf.paragraphs[0]
                
                # Combine spans to maintain consistent line alignments and font properties
                for i, span in enumerate(span for span in line["spans"] if span["text"].strip()):
                    if i > 0:
                        run = p.add_run()
                    else:
                        run = p
                        
                    run.text = span["text"]
                    
                    # 1. Match Exact Font Size
                    run.font.size = Pt(round(span["size"], 1))
                    
                    # 2. Match Font Family / Name Safely
                    font_name = span["font"].lower()
                    if "bold" in font_name:
                        run.font.bold = True
                    if "italic" in font_name:
                        run.font.italic = True
                        
                    # Map standard font fallbacks
                    if "sans" in font_name or "arial" in font_name or "helvetica" in font_name:
                        run.font.name = "Arial"
                    elif "serif" in font_name or "times" in font_name or "roman" in font_name:
                        run.font.name = "Times New Roman"
                    elif "courier" in font_name or "mono" in font_name:
                        run.font.name = "Courier New"
                    else:
                        run.font.name = span["font"] # Try native font fallback
                        
                    # 3. Match Hex Color Properties
                    run.font.color.rgb = hex_to_rgb(span["color"])

    doc.close()
    prs.save(output_path)
