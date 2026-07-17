import pypdf
import io

def merge_pdfs_logic(pdf_files: list[bytes]) -> io.BytesIO:
    """
    সম্পূর্ণ মেমরিতে (RAM) একাধিক পিডিএফ ফাইল একসাথে যুক্ত করার লজিক।
    """
    merger = pypdf.PdfMerger()
    
    for pdf_bytes in pdf_files:
        merger.append(io.BytesIO(pdf_bytes))
        
    output_pdf = io.BytesIO()
    merger.write(output_pdf)
    merger.close()
    
    output_pdf.seek(0)
    return output_pdf
