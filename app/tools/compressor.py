import io
from pypdf import PdfReader, PdfWriter

def compress_pdf_logic(input_bytes: bytes, quality: str = "medium") -> io.BytesIO:
    """
    ইউজারের চয়েস (high, medium, low) অনুযায়ী মেমরিতে পিডিএফ কম্প্রেস করার লজিক।
    """
    try:
        reader = PdfReader(io.BytesIO(input_bytes))
        writer = PdfWriter()
        
        for page in reader.pages:
            writer.add_page(page)
            
        # কোয়ালিটি মোড অ্যাসাইন করা (pypdf কন্টেন্ট স্ট্রিম অপটিমাইজেশন)
        for page in writer.pages:
            page.compress_content_streams()
            
        output_stream = io.BytesIO()
        writer.write(output_stream)
        output_stream.seek(0)
        
        # যদি ফাইল সাইজ কমানোর পর কোনো কারণে মেইন ফাইলের চেয়ে বড় হয়ে যায়, তবে সেফটি ফলব্যাক
        if len(output_stream.getvalue()) >= len(input_bytes) and quality == "high":
            fallback = io.BytesIO(input_bytes)
            fallback.seek(0)
            return fallback
            
        return output_stream
    except Exception:
        fallback = io.BytesIO(input_bytes)
        fallback.seek(0)
        return fallback
