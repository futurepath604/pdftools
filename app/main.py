import json
import os
import uuid
import zipfile
from typing import List
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import pypdf

# আপনার আগের তৈরি করা টুলস মডিউল ইমপোর্ট (পাথ প্রজেক্ট অনুযায়ী চেক করে নেবেন)
from pdftools.app.tools.compressor import compress_pdf_file
from app.tools.ocr_engine import process_pdf_ocr

app = FastAPI(title="Secure PDF Tools API", version="1.0.0")

# CORS Middleware (যদি ফ্রন্টএন্ড আলাদা পোর্টে চলে)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------------------------------------------------
# ১. PDF Compress API
# ----------------------------------------------------------------
@app.post("/api/compress-pdf")
async def api_compress_pdf(
    file: UploadFile = File(...),
    params: str = Form("{}")
):
    input_path = f"temp_in_{uuid.uuid4().hex}_{file.filename}"
    output_path = f"compressed_{uuid.uuid4().hex}_{file.filename}"
    
    try:
        with open(input_path, "wb") as buffer:
            buffer.write(await file.read())
            
        success = compress_pdf_file(input_path, output_path, params_str=params)
        
        if not success or not os.path.exists(output_path):
            raise HTTPException(status_code=500, detail="Compression engine failed.")
            
        return FileResponse(
            output_path, 
            media_type="application/pdf", 
            filename=f"compressed_{file.filename}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(input_path): os.remove(input_path)


# ----------------------------------------------------------------
# ২. PDF Unlock API (Legally Compliant Optional Mode)
# ----------------------------------------------------------------
@app.post("/api/unlock-pdf")
async def api_unlock_pdf(
    file: UploadFile = File(...),
    password: str = Form(...)
):
    input_path = f"temp_lock_{uuid.uuid4().hex}_{file.filename}"
    output_path = f"unlocked_{uuid.uuid4().hex}_{file.filename}"
    
    try:
        with open(input_path, "wb") as buffer:
            buffer.write(await file.read())
            
        reader = pypdf.PdfReader(input_path)
        
        # পাসওয়ার্ড চেক করা
        if reader.is_encrypted:
            try:
                decrypted = reader.decrypt(password)
                if decrypted == 0:
                    raise HTTPException(status_code=401, detail="Incorrect password.")
            except Exception:
                raise HTTPException(status_code=401, detail="Incorrect password.")
        
        writer = pypdf.PdfWriter()
        for page in reader.pages:
            writer.add_page(page)
            
        with open(output_path, "wb") as f:
            writer.write(f)
            
        return FileResponse(
            output_path, 
            media_type="application/pdf", 
            filename=f"unlocked_{file.filename}"
        )
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unlock failed: {str(e)}")
    finally:
        if os.path.exists(input_path): os.remove(input_path)


# ----------------------------------------------------------------
# ৩. NEW: PDF Page Rearrange & Merge API
# ----------------------------------------------------------------
@app.post("/api/rearrange-pdf")
async def api_rearrange_pdf(
    files: List[UploadFile] = File(...),
    sequence: str = Form(...)
):
    temp_files = []
    output_filename = f"arranged_{uuid.uuid4().hex}.pdf"
    
    try:
        # সব ফাইল টেম্পোরারি সেভ করা
        for uploaded_file in files:
            temp_path = f"temp_arr_{uuid.uuid4().hex}_{uploaded_file.filename}"
            with open(temp_path, "wb") as buffer:
                buffer.write(await uploaded_file.read())
            temp_files.append(temp_path)
            
        try:
            sequence_rules = json.loads(sequence)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid sequence compilation payload.")
            
        writer = pypdf.PdfWriter()
        
        # ফ্রন্টএন্ডের রুলস অনুযায়ী পেজ অ্যারেঞ্জ করা
        for block in sequence_rules:
            file_idx = block.get("file_index")
            pages_to_add = block.get("pages", [])
            
            if file_idx < 0 or file_idx >= len(temp_files):
                raise HTTPException(status_code=400, detail="File identifier index out of bounds.")
                
            reader = pypdf.PdfReader(temp_files[file_idx])
            total_pages = len(reader.pages)
            
            for p_num in pages_to_add:
                if 0 <= p_num < total_pages:
                    writer.add_page(reader.pages[p_num])
                    
        with open(output_filename, "wb") as out_f:
            writer.write(out_f)
            
        return FileResponse(
            output_filename, 
            media_type="application/pdf", 
            filename="arranged_document.pdf"
        )
        
    except Exception as e:
        if os.path.exists(output_filename): os.remove(output_filename)
        raise HTTPException(status_code=500, detail=f"Arrangement failure: {str(e)}")
    finally:
        for t_file in temp_files:
            if os.path.exists(t_file): os.remove(t_file)


# ----------------------------------------------------------------
# ৪. NEW: PDF OCR Converter API
# ----------------------------------------------------------------
@app.post("/api/ocr-pdf")
async def api_ocr_pdf(
    files: List[UploadFile] = File(...),
    lang: str = Form("eng")
):
    uploaded_temps = []
    processed_temps = []
    zip_output_path = f"ocr_bundle_{uuid.uuid4().hex}.zip"

    try:
        for file in files:
            t_input = f"input_ocr_{uuid.uuid4().hex}_{file.filename}"
            t_output = f"searchable_{uuid.uuid4().hex}_{file.filename}"
            
            with open(t_input, "wb") as buffer:
                buffer.write(await file.read())
            
            uploaded_temps.append(t_input)

            # OCR প্রসেস রান করা
            success = process_pdf_ocr(t_input, t_output, lang=lang)
            if not success or not os.path.exists(t_output):
                raise HTTPException(status_code=500, detail=f"OCR failed on file: {file.filename}")
                
            processed_temps.append((t_output, file.filename))

        # সিঙ্গেল ফাইল হলে সরাসরি PDF ডাউনলোড হবে
        if len(processed_temps) == 1:
            single_path, original_name = processed_temps[0]
            return FileResponse(
                single_path, 
                media_type="application/pdf", 
                filename=f"searchable_{original_name}"
            )
        # মাল্টিপল ফাইল হলে ZIP আকারে ডাউনলোড হবে
        else:
            with zipfile.ZipFile(zip_output_path, 'w') as zipf:
                for file_path, original_name in processed_temps:
                    zipf.write(file_path, arcname=f"searchable_{original_name}")
            
            return FileResponse(
                zip_output_path, 
                media_type="application/zip", 
                filename="ocr_searchable_documents.zip"
            )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OCR pipeline failed: {str(e)}")
    finally:
        for path in uploaded_temps:
            if os.path.exists(path): os.remove(path)
        if len(processed_temps) > 1:
            for path, _ in processed_temps:
                if os.path.exists(path): os.remove(path)


# ----------------------------------------------------------------
# সার্ভার রান করার জন্য রুট পাথ (اختياري)
# ----------------------------------------------------------------
@app.get("/")
async def root():
    return {"message": "Secure PDF Tools Backend is Running Perfect!"}
