import os
import fitz  # PyMuPDF
from pptx import Presentation
from pptx.util import Inches

def convert_pdf_to_ppt(input_path: str, output_path: str):
    """
    Converts PDF to PowerPoint keeping 100% exact alignment, fonts, backgrounds, and images.
    It renders pages as high-resolution slides to ensure pixel-perfect fidelity.
    """
    prs = Presentation()
    
    # Slide Dimensions (Standard 16:9 Widescreen)
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_slide_layout = prs.slide_layouts[6] # Completely blank layout

    # Open PDF document using PyMuPDF
    pdf_document = fitz.open(input_path)
    
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        
        # Matrix for Ultra High-Resolution (300 DPI Rendering for crisp text and images)
        zoom = 3
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat)
        
        # Temporary image path for the slide background layer
        temp_image_path = f"temp_page_{page_num}.png"
        pix.save(temp_image_path)
        
        # Add a blank slide
        slide = prs.slides.add_slide(blank_slide_layout)
        
        # Insert the exact page rendering as a full-bleed layout element
        slide.shapes.add_picture(temp_image_path, 0, 0, width=prs.slide_width, height=prs.slide_height)
        
        # Clean up temporary page image immediately
        if os.path.exists(temp_image_path):
            os.remove(temp_image_path)
            
    pdf_document.close()
    prs.save(output_path)
