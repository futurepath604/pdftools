import io
from typing import List
from pypdf import PdfMerger

def merge_pdfs_logic(pdf_files_bytes: List[bytes]) -> io.BytesIO:
    """মেমরিতে একাধিক পিডিএফ ফাইল জোড়া দেওয়ার ফাস্ট লজিক।"""
    try:
        merger = PdfMerger()
        
        for file_bytes in pdf_files_bytes:
            merger.append(io.BytesIO(file_bytes))
            
        output_stream = io.BytesIO()
        merger.write(output_stream)
        merger.close()
        output_stream.seek(0)
        return output_stream
        
    except Exception as e:
        raise RuntimeError(f"PDF Merge করতে সমস্যা হয়েছে: {str(e)}")
