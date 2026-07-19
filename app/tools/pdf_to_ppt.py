import os
import pdfplumber
from pptx import Presentation
from pptx.util import Inches

def convert_pdf_to_ppt(input_path: str, output_path: str):
    """Converts text layers of PDF into Microsoft PowerPoint slides."""
    prs = Presentation()
    blank_layout = prs.slide_layouts[6]
    
    with pdfplumber.open(input_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            slide = prs.slides.add_slide(blank_layout)
            if text:
                txBox = slide.shapes.add_textbox(Inches(0.75), Inches(0.75), Inches(8.5), Inches(5.5))
                tf = txBox.text_frame
                tf.word_wrap = True
                tf.text = text
    prs.save(output_path)
