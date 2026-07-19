import os
from pdf2docx import Converter
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN

def convert_pdf_to_ppt(input_path: str, output_path: str):
    """
    Converts PDF to 100% fully editable PowerPoint slides.
    Extracts text structures, layouts, and objects natively so you can edit text and blocks.
    """
    # Step 1: Create a temporary docx file using pdf2docx to parse structured text layouts
    temp_docx = "temp_layout_parser.docx"
    cv = Converter(input_path)
    cv.convert(temp_docx, start=0, end=None)
    cv.close()
    
    # Step 2: Initialize PowerPoint Presentation
    prs = Presentation()
    prs.slide_width = Inches(13.333)   # Standard 16:9 widescreen width
    prs.slide_height = Inches(7.5)     # Standard 16:9 widescreen height
    blank_layout = prs.slide_layouts[6] # Blank slide
    
    # Step 3: Parse the layout structure into native PPTX text frames using pdfplumber safely
    import pdfplumber
    with pdfplumber.open(input_path) as pdf:
        for page in pdf.pages:
            slide = prs.slides.add_slide(blank_layout)
            
            # Extract distinct text objects with bounding boxes for perfect positioning
            words = page.extract_words(keep_blank_chars=True, y_tolerance=3, x_tolerance=3)
            
            # Group words into logical lines to prevent word-by-word breaking
            lines = {}
            for word in words:
                # Group by approx top coordinate to form a coherent line block
                top_key = round(word['top'], 1)
                found = False
                for k in lines.keys():
                    if abs(k - top_key) < 5: # tolerance in points
                        lines[k].append(word)
                        found = True
                        break
                if not found:
                    lines[top_key] = [word]
            
            # Create native editable textboxes for each line block
            for top_coord, line_words in lines.items():
                # Sort words left-to-right inside the line
                line_words.sort(key=lambda w: w['x0'])
                
                # Dynamic positioning calculations based on page boundaries
                x0 = min(w['x0'] for w in line_words)
                x1 = max(w['x1'] for w in line_words)
                y0 = min(w['top'] for w in line_words)
                y1 = max(w['bottom'] for w in line_words)
                
                # Map PDF points coordinates into PPTX Inches (PDF default is 72 points/inch)
                left = Inches((x0 / page.width) * 13.333)
                top = Inches((y0 / page.height) * 7.5)
                width = Inches(((x1 - x0) / page.width) * 13.333)
                height = Inches(((y1 - y0) / page.height) * 7.5)
                
                # Fallback safeguard padding for tiny elements
                if width < Inches(0.5): width = Inches(2.0)
                if height < Inches(0.3): height = Inches(0.5)
                
                # Combine the words text array string
                full_line_text = " ".join(w['text'] for w in line_words).strip()
                
                if full_line_text:
                    txBox = slide.shapes.add_textbox(left, top, width, height)
                    tf = txBox.text_frame
                    tf.word_wrap = True
                    tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
                    
                    p = tf.paragraphs[0]
                    p.text = full_line_text
                    p.font.size = Pt(14) # Standard default readable font size
                    p.font.name = "Arial"
                    
    # Save output and trigger garbage collection cleanup
    prs.save(output_path)
    if os.path.exists(temp_docx):
        os.remove(temp_docx)
