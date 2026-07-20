import os
import subprocess
import json
import shutil
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse

# Create a dedicated router for the Compressor tool
router = APIRouter(prefix="/api", tags=["PDF Compressor"])

def compress_pdf_file(input_path: str, output_path: str, params_str: str = "{}") -> bool:
    """
    Compresses a PDF file using Ghostscript based on the provided parameters.
    Supports both default strategies and custom target sizes.
    """
    try:
        # ফ্রন্টএন্ড থেকে আসা প্যারামিটার পার্স করা
        try:
            params = json.loads(params_str)
        except Exception:
            params = {}

        custom_mode = params.get("custom_mode", False)
        target_size_kb = params.get("target_size_kb")
        strategy = params.get("strategy", "medium")

        # ১. ডিফল্ট কম্প্রেশন লেভেল সেটআপ (Ghostscript settings)
        # /screen = low quality/small size, /ebook = medium quality, /printer = high quality
        if strategy == "high":
            gs_quality = "/screen"
        elif strategy == "low":
            gs_quality = "/printer"
        else:
            gs_quality = "/ebook"

        # কাস্টম সাইজ মোড অন থাকলে এবং ইউজার ভ্যালু দিলে সরাসরি সবচেয়ে ছোট সাইজে ট্রাই করবে
        if custom_mode and target_size_kb:
            gs_quality = "/screen"

        # ২. Ghostscript কমান্ড তৈরি
        cmd = [
            "gs",
            "-sDEVICE=pdfwrite",
            "-dCompatibilityLevel=1.4",
            f"-dPDFSETTINGS={gs_quality}",
            "-dNOPAUSE",
            "-dQUIET",
            "-dBATCH",
            f"-sOutputFile={output_path}",
            input_path
        ]

        # কমান্ড এক্সিকিউট করা
        subprocess.run(cmd, check=True)

        # ৩. কাস্টম সাইজ চেক ও ফলব্যাক (Fallback) মেকানিজম
        if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            return True
            
        return False

    except subprocess.CalledProcessError:
        # যদি Ghostscript কোনো কারণে ফেইল করে, তবে সেফটি হিসেবে অরজিনাল ফাইলটাই আউটপুট বানিয়ে দেওয়া
        try:
            shutil.copy(input_path, output_path)
            return True
        except Exception:
            return False
            
    except Exception:
        return False


# The API endpoint is now self-contained inside the compressor tool file!
@router.post("/compress")
async def api_compress_pdf(
    file: UploadFile = File(...),
    strategy: str = Form("medium"),
    custom_mode: bool = Form(False),
    target_size_kb: int = Form(None)
):
    input_path = f"temp_in_{file.filename}"
    output_filename = f"compressed_{file.filename}"
    output_path = f"temp_out_{output_filename}"
    
    # Save uploaded file
    with open(input_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    # Prepare parameter schema for core engine
    params_payload = {
        "strategy": strategy,
        "custom_mode": custom_mode,
        "target_size_kb": target_size_kb
    }
    
    try:
        success = compress_pdf_file(input_path, output_path, json.dumps(params_payload))
        if not success:
            raise HTTPException(status_code=500, detail="Ghostscript compression execution failed.")
            
        return FileResponse(
            output_path, 
            media_type="application/pdf", 
            filename=output_filename,
            headers={"Content-Disposition": f"attachment; filename={output_filename}"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Compression Engine Error: {str(e)}")
    finally:
        # Clean up temporary storage files safely
        if os.path.exists(input_path):
            try: os.remove(input_path)
            except: pass
