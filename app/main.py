from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse
from typing import List
import os
import json
import io
from PIL import Image

# --- 🔄 VERSION-SAFE PYPDF IMPORTS ---
import pypdf
from pypdf import PdfReader, PdfWriter

# pypdf এর বিভিন্ন ভার্সনের সাথে সামঞ্জস্য রাখার জন্য ডায়নামিক মার্জার ইম্পোর্ট ফলব্যাক
try:
    from pypdf import PdfMerger
except ImportError:
    try:
        from pypdf._merger import PdfMerger
    except ImportError:
        # যদি একদমই ওল্ড ভার্সন হয় তবে ব্যাকওয়ার্ড কম্প্যাটিবিলিটি ট্রাই করবে
        from pypdf import PdfFileMerger as PdfMerger

app = FastAPI(title="Secure PDF Tools Pro")

# --- 🚀 ADVANCED COMPRESSION ENGINE (With Image Downsampling) ---
def compress_pdf_logic(input_bytes: bytes, quality: str = "medium") -> io.BytesIO:
    try:
        reader = PdfReader(io.BytesIO(input_bytes))
        writer = PdfWriter()
        
        if quality == "high":  # Extreme Compression
            img_max_dim = 800
            img_quality = 40
        elif quality == "medium":  # Recommended
            img_max_dim = 1200
            img_quality = 65
        else:  # Low Compression
            img_max_dim = 2000
            img_quality = 85

        for page in reader.pages:
            try:
                page.compress_content_streams()
            except Exception:
                pass
            
            if "/Resources" in page and "/XObject" in page["/Resources"]:
                try:
                    xobjects = page["/Resources"]["/XObject"].get_object()
                    for obj_name in xobjects:
                        obj = xobjects[obj_name].get_object()
                        if obj["/Subtype"] == "/Image":
                            try:
                                img_data = obj.get_data()
                                img = Image.open(io.BytesIO(img_data))
                                
                                if max(img.size) > img_max_dim:
                                    img.thumbnail((img_max_dim, img_max_dim), Image.Resampling.LANCZOS)
                                
                                out_img_bytes = io.BytesIO()
                                img.save(out_img_bytes, format="JPEG", quality=img_quality, optimize=True)
                                
                                obj._data = out_img_bytes.getvalue()
                                if "/Filter" in obj:
                                    obj[os.path.join("/Filter")] = "/DCTDecode"
                            except Exception:
                                continue
                except Exception:
                    pass
                            
            writer.add_page(page)
            
        output_stream = io.BytesIO()
        writer.write(output_stream)
        output_stream.seek(0)
        return output_stream
    except Exception:
        fallback = io.BytesIO(input_bytes)
        fallback.seek(0)
        return fallback

# --- CORE LOGIC: MERGER ENGINE ---
def merge_pdfs_logic(pdf_files_bytes: List[bytes]) -> io.BytesIO:
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
        raise RuntimeError(str(e))

# --- SMART PATH FINDER ENGINE ---
def find_html_file(filename: str) -> str:
    possible_paths = [
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", filename),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), filename),
        os.path.join(os.getcwd(), "static", filename),
        os.path.join(os.getcwd(), filename),
        os.path.join("/code", "app", "static", filename),
        os.path.join("/code", filename)
    ]
    for path in possible_paths:
        if os.path.exists(path):
            return path
    base_root = os.getcwd()
    for root, dirs, files in os.walk(base_root):
        if filename in files:
            return os.path.join(root, filename)
    raise HTTPException(status_code=404, detail=f"File {filename} not found.")

# --- ROUTING ---
@app.get("/")
async def route_home(): return FileResponse(find_html_file("index.html"))

@app.get("/compress")
async def route_compress(): return FileResponse(find_html_file("compress.html"))

@app.get("/merge")
async def route_merge(): return FileResponse(find_html_file("merge.html"))

# --- API ENDPOINTS ---
@app.post("/api/compress")
async def api_compress(file: UploadFile = File(...), quality: str = Form("medium")):
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Invalid file type.")
    try:
        content = await file.read()
        output_stream = compress_pdf_logic(content, quality)
        return StreamingResponse(output_stream, media_type="application/pdf", headers={"Content-Disposition": f"attachment; filename=optimized_{file.filename}"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/merge")
async def api_merge(files: List[UploadFile] = File(...), file_order: str = Form(...)):
    if len(files) < 2:
        raise HTTPException(status_code=400, detail="Select at least 2 files.")
    try:
        file_map = {}
        all_raw_bytes = []
        for f in files:
            file_content = await f.read()
            file_map[f.filename] = file_content
            all_raw_bytes.append(file_content)
        try:
            order_list = json.loads(file_order)
            ordered_bytes = [file_map[name] for name in order_list if name in file_map]
        except Exception:
            ordered_bytes = []
        if not ordered_bytes:
            ordered_bytes = all_raw_bytes
        output_stream = merge_pdfs_logic(ordered_bytes)
        return StreamingResponse(output_stream, media_type="application/pdf", headers={"Content-Disposition": "attachment; filename=merged_secure_doc.pdf"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
