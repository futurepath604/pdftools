import pypdf
import io

def compress_pdf_logic(pdf_bytes: bytes) -> io.BytesIO:
    """
    পিডিএফের কোয়ালিটি ঠিক রেখে ভেতরের ডুপ্লিকেট অবজেক্ট ও কন্টেন্ট কম্প্রেস করে সাইজ কমানোর লজিক।
    """
    reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
    writer = pypdf.PdfWriter()
    
    for page in reader.pages:
        page.compress_content_streams()
        writer.add_page(page)
        
    writer.compress_identical_objects(remove_duplicates=True, remove_unreferenced=True)
    
    output_pdf = io.BytesIO()
    writer.write(output_pdf)
    writer.close()
    
    output_pdf.seek(0)
    return output_pdf
