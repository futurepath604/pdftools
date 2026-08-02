import os
import sys
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from config import settings

# Setup paths
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if current_dir not in sys.path: sys.path.append(current_dir)
if parent_dir not in sys.path: sys.path.append(parent_dir)

app = FastAPI(title=settings.APP_TITLE)

# Static files mount with fallback check
static_path = os.path.join(current_dir, "app", "static")
if not os.path.exists(static_path):
    static_path = os.path.join(current_dir, "static")

if os.path.exists(static_path):
    app.mount("/static", StaticFiles(directory=static_path), name="static")

# --- GLOBAL CONFIG API (Frontend branding-er jonno) ---
@app.get("/api/config")
async def get_config():
    return {
        "appName": settings.APP_NAME,
        "shortName": settings.APP_SHORT_NAME,
        "tagline": settings.APP_TAGLINE,
        "logoEmoji": settings.LOGO_EMOJI,
        "footer": settings.FOOTER_TEXT
    }

# --- DYNAMICALLY INCLUDE SELF-CONTAINED ROUTERS ---
routers_to_load = [
    ("app.tools.compressor", "router"),
    ("app.tools.pdf_to_excel", "router"),
    ("app.tools.image_to_pdf", "router"),
    ("app.tools.merger", "router"),
    ("app.tools.modify", "router"),
    ("app.tools.ocr_engine", "router"),
    ("app.tools.pdf_to_image", "router"),
    ("app.tools.pdf_to_ppt", "router"),
    ("app.tools.pdf_to_word", "router"),
    ("app.tools.rearrange_backend", "router"),
    ("app.tools.security", "router"),
]

for module_path, router_name in routers_to_load:
    try:
        mod = __import__(module_path, fromlist=[router_name])
        app.include_router(getattr(mod, router_name))
    except Exception as e:
        print(f"⚠️ Failed to load Router {module_path}: {e}")

# Helper for secure HTML serving
def serve_html(filename: str):
    path_primary = os.path.join(current_dir, "app", "static", filename)
    path_secondary = os.path.join(current_dir, "static", filename)
    if os.path.exists(path_primary):
        return FileResponse(path_primary)
    return FileResponse(path_secondary)

# --- HTML UI ENDPOINTS ---
@app.get("/")
async def read_index(): return serve_html("index.html")

@app.get("/compress")
@app.get("/compress.html")
async def read_compress(): return serve_html("compress.html")

@app.get("/merge")
@app.get("/merge.html")
async def read_merge(): return serve_html("merge.html")

@app.get("/pdf-to-image")
@app.get("/pdf-to-image.html")
async def read_pdf_to_image(): return serve_html("pdf-to-image.html")

@app.get("/image-to-pdf")
@app.get("/image-to-pdf.html")
async def read_image_to_pdf(): return serve_html("image-to-pdf.html")

@app.get("/split")
@app.get("/split.html")
async def read_split(): return serve_html("split.html")

@app.get("/rotate")
@app.get("/rotate.html")
async def read_rotate(): return serve_html("rotate.html")

@app.get("/delete-pages")
@app.get("/delete-pages.html")
async def read_delete_pages(): return serve_html("delete-pages.html")

@app.get("/lock")
@app.get("/lock.html")
async def read_lock(): return serve_html("lock.html")

@app.get("/unlock")
@app.get("/unlock.html")
async def read_unlock(): return serve_html("unlock.html")

@app.get("/ocr")
@app.get("/ocr.html")
async def read_ocr(): return serve_html("ocr.html")

@app.get("/rearrange")
@app.get("/rearrange.html")
async def read_rearrange(): return serve_html("rearrange.html")

@app.get("/pdf-to-word")
@app.get("/pdf-to-word.html")
async def read_pdf_to_word(): return serve_html("pdf-to-word.html")

@app.get("/pdf-to-excel")
@app.get("/pdf-to-excel.html")
async def read_pdf_to_excel_page(): return serve_html("pdf-to-excel.html")

@app.get("/pdf-to-ppt")
@app.get("/pdf-to-ppt.html")
async def read_pdf_to_ppt(): return serve_html("pdf-to-ppt.html")

# --- ADSENSE MANDATORY LEGAL ROUTERS ---
@app.get("/privacy-policy")
@app.get("/privacy.html")
async def read_privacy(): return serve_html("privacy.html")

@app.get("/terms-of-service")
@app.get("/terms.html")
async def read_terms(): return serve_html("terms.html")

@app.get("/contact-us")
@app.get("/contact.html")
async def read_contact(): return serve_html("contact.html")
