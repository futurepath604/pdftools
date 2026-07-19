import os
from pdf2docx import Converter

def convert_pdf_to_word(input_path: str, output_path: str):
    """Converts PDF to Word maintaining original layouts, fonts, and formatting."""
    cv = Converter(input_path)
    cv.convert(output_path)
    cv.close()
