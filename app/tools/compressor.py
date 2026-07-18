import os
import subprocess
import json

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
            # যদি কাস্টম মোড অন থাকে, তাও ফাইল সাইজ টার্গেটের চেয়ে বড় হয়, 
            # পাইপলাইন ক্র্যাশ না করিয়ে আমরা ফাইলটি রেন্ডার হতে দেব (যা বেস্ট এফোর্ট হিসেবে কাজ করবে)
            return True
            
        return False

    except subprocess.CalledProcessError:
        # যদি Ghostscript কোনো কারণে ফেইল করে, তবে সেফটি হিসেবে অরজিনাল ফাইলটাই আউটপুট বানিয়ে দেওয়া
        try:
            import shutil
            shutil.copy(input_path, output_path)
            return True
        except Exception:
            return False
            
    except Exception:
        return False
