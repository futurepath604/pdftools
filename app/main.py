import os
import sys
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

# Setup paths
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if current_dir not in sys.path: sys.path.append(current_dir)
if parent_dir not in sys.path: sys.path.append(parent_dir)

app = FastAPI(title="Secure PDF Tools Ultimate API")

if os.path.exists("app/static"):
    app.mount("/static", StaticFiles(directory="app/static"), name="static")


# --- DYNAMICALLY INCLUDE SELF-CONTAINED ROUTERS ---

# ১. PDF Compressor রাউটার লোড
try:
    from app.tools.compressor import router as compress_router
    app.include_router(compress_router)
except Exception as e:
    print(f"⚠️ Failed to load PDF Compressor Router: {e}")

# ২. PDF to Excel রাউটার লোড
try:
    from app.tools.pdf_to_excel import router as pdf_to_excel_router
    app.include_router(pdf_to_excel_router)
except Exception as e:
    print(f"⚠️ Failed to load PDF to Excel Router: {e}")

# ৩. Image to PDF রাউটার লোড
try:
    from app.tools.image_to_pdf import router as image_to_pdf_router
    app.include_router(image_to_pdf_router)
except Exception as e:
    print(f"⚠️ Failed to load Image to PDF Router: {e}")

# ৪. PDF Merger রাউটার লোড
try:
    from app.tools.merger import router as merge_router
    app.include_router(merge_router)
except Exception as e:
    print(f"⚠️ Failed to load PDF Merger Router: {e}")

# ৫. PDF Modify (Split, Rotate, Delete) রাউটার লোড
try:
    from app.tools.modify import router as modify_router
    app.include_router(modify_router)
except Exception as e:
    print(f"⚠️ Failed to load PDF Modify Router: {e}")

# ৬. PDF OCR Engine রাউটার লোড
try:
    from app.tools.ocr_engine import router as ocr_router
    app.include_router(ocr_router)
except Exception as e:
    print(f"⚠️ Failed to load PDF OCR Router: {e}")

# ৭. PDF to Image রাউটার লোড
try:
    from app.tools.pdf_to_image import router as pdf_to_image_router
    app.include_router(pdf_to_image_router)
except Exception as e:
    print(f"⚠️ Failed to load PDF to Image Router: {e}")


# --- HTML UI ENDPOINTS ---
@app.get("/")
async def read_index(): return FileResponse("app/static/index.html")

@app.get("/compress")
async def read_compress(): return FileResponse("app/static/compress.html")

@app.get("/merge")
async def read_merge(): return FileResponse("app/static/merge.html")

@app.get("/pdf-to-image")
async def read_pdf_to_image(): return FileResponse("app/static/pdf-to-image.html")

@app.get("/image-to-pdf")
async def read_image_to_pdf(): return FileResponse("app/static/image-to-pdf.html")

@app.get("/split")
async def read_split(): return FileResponse("app/static/split.html")

@app.get("/rotate")
async def read_rotate(): return FileResponse("app/static/rotate.html")

@app.get("/delete-pages")
async def read_delete_pages(): return FileResponse("app/static/delete-pages.html")

@app.get("/lock")
async def read_lock(): return FileResponse("app/static/lock.html")

@app.get("/unlock")
async def read_unlock(): return FileResponse("app/static/unlock.html")

@app.get("/ocr")
async def read_ocr(): return FileResponse("app/static/ocr.html")

@app.get("/rearrange")
async def read_rearrange(): return FileResponse("app/static/rearrange.html")

@app.get("/pdf-to-word")
async def read_pdf_to_word(): return FileResponse("app/static/pdf-to-word.html")

@app.get("/pdf-to-excel")
async def read_pdf_to_excel_page(): return FileResponse("app/static/pdf-to-excel.html")

@app.get("/pdf-to-ppt")
async def read_pdf_to_ppt(): return FileResponse("app/static/pdf-to-ppt.html")

# --- ADSENSE MANDATORY LEGAL ROUTERS ---
@app.get("/privacy-policy")
async def read_privacy(): return FileResponse("app/static/privacy.html")

@app.get("/terms-of-service")
async def read_terms(): return FileResponse("app/static/terms.html")

@app.get("/contact-us")
async def read_contact(): return FileResponse("app/static/contact.html")
