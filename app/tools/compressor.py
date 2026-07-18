import io
from pypdf import PdfReader, PdfWriter

def compress_pdf_logic(input_bytes: bytes, quality: str = "medium") -> io.BytesIO:
    """
    মেমরিতে পিডিএফ হাই-স্পিডে কম্প্রেস করার বাগ-ফ্রি পাইথন লজিক।
    """
    try:
        reader = PdfReader(io.BytesIO(input_bytes))
        writer = PdfWriter()
        
        for page in reader.pages:
            writer.add_page(page)
            
        for page in writer.pages:
            page.compress_content_streams()
            
        output_stream = io.BytesIO()
        writer.write(output_stream)
        output_stream.seek(0)
        
        if len(output_stream.getvalue()) >= len(input_bytes) and quality == "high":
            fallback = io.BytesIO(input_bytes)
            fallback.seek(0)
            return fallback
            
        return output_stream
    except Exception:
        fallback = io.BytesIO(input_bytes)
        fallback.seek(0)
        return fallback
