from pdf2image import convert_from_bytes
import io
import zipfile

def pdf_to_images_zip_logic(pdf_bytes: bytes) -> io.BytesIO:
    """
    পিডিএফের প্রতিটি পেজকে জেপিজি ছবিতে কনভার্ট করে একটি ZIP ফাইল বানিয়ে মেমরিতেই রিটার্ন করার লজিক।
    """
    images = convert_from_bytes(pdf_bytes, dpi=150)
    zip_buffer = io.BytesIO()
    
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for idx, img in enumerate(images):
            img_buffer = io.BytesIO()
            img.save(img_buffer, format="JPEG")
            img_buffer.seek(0)
            zip_file.writestr(f"page_{idx + 1}.jpg", img_buffer.getvalue())
            
    zip_buffer.seek(0)
    return zip_buffer
