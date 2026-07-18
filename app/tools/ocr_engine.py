import os
import uuid
import zipfile
import pytesseract
from pdf2image import convert_from_path
import pypdf

def process_pdf_ocr(input_path: str, output_path: str, lang: str = "eng") -> bool:
    """
    Converts a non-searchable scanned PDF into a searchable PDF using Tesseract OCR.
    """
    try:
        # ১. পিডিএফ ফাইলকে ইমেজে রূপান্তর করা (300 DPI অপ্টিমাল কোয়ালিটির জন্য)
        images = convert_from_path(input_path, dpi=300)
        
        pdf_writer = pypdf.PdfWriter()
        temp_page_paths = []

        # ২. প্রতিটি পেজ ইমেজে OCR রান করে পিডিএফ পেজ জেনারেট করা
        for idx, img in enumerate(images):
            # Tesseract দিয়ে ইমেজকে সরাসরি টেক্সট এম্বেডেড পিডিএফ করা
            page_pdf_bytes = pytesseract.image_to_pdf_or_hocr(img, extension='pdf', lang=lang)
            
            temp_page_name = f"temp_page_{uuid.uuid4().hex}_{idx}.pdf"
            with open(temp_page_name, "wb") as f:
                f.write(page_pdf_bytes)
            temp_page_paths.append(temp_page_name)

            # জেনারেট হওয়া পেজটি মূল রাইটারে যুক্ত করা
            reader = pypdf.PdfReader(temp_page_name)
            pdf_writer.add_page(reader.pages[0])

        # ৩. মার্জ করা পিডিএফ ফাইল রাইট করা
        with open(output_path, "wb") as out_f:
            pdf_writer.write(out_f)

        # ক্লিনআপ টেম্পোরারি সিঙ্গেল পেজ
        for t_path in temp_page_paths:
            if os.path.exists(t_path):
                os.remove(t_path)

        return True
    except Exception:
        return False
