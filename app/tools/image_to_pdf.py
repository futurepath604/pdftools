from PIL import Image
import io

def images_to_pdf_logic(image_files: list[bytes]) -> io.BytesIO:
    """
    একাধিক JPG/PNG ছবিকে মেমরিতেই একটি সিঙ্গেল পিডিএফ ফাইলে কনভার্ট করার লজিক।
    """
    pil_images = []
    
    for img_bytes in image_files:
        img = Image.open(io.BytesIO(img_bytes))
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        pil_images.append(img)
        
    if not pil_images:
        raise ValueError("No images provided!")
        
    output_pdf = io.BytesIO()
    first_image = pil_images[0]
    first_image.save(
        output_pdf, 
        format="PDF", 
        save_all=True, 
        append_images=pil_images[1:]
    )
    
    output_pdf.seek(0)
    return output_pdf
