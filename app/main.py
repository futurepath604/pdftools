from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

# আপনার আগের তৈরি করা মডুলার কম্প্রেসার ইঞ্জিন ইম্পোর্ট করা হলো
from app.tools.compressor import compress_pdf_logic

app = FastAPI(
    title="Secure PDF Tools API",
    description="100% Free & Private PDF Tools. No files are saved on the server.",
    version="1.0.0"
)

# 🔒 চিরকালের জন্য CORS পলিসি ফিক্স (Hugging Face ফ্রন্টএন্ডের জন্য)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {
        "status": "online",
        "message": "📄 Secure PDF Tools Online API is live and fully accessible!"
    }

@app.post("/api/compress")
async def api_compress(file: UploadFile = File(...)):
    # ফাইল টাইপ ভ্যালিডেশন
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="দয়া করে শুধুমাত্র PDF ফাইল আপলোড করুন।")
    
    try:
        # ফাইল রিড করা
        content = await file.read()
        
        # ১৫ মেগাবাইট ফাইল সাইজ লিমিট চেক
        if len(content) > 15 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="ফাইল সাইজ ১৫ মেগাবাইটের বেশি হওয়া যাবে না।")
            
        # মেমরিতেই কম্প্রেস করার লজিক কল করা
        output_stream = compress_pdf_logic(content)
        
        return StreamingResponse(
            output_stream, 
            media_type="application/pdf", 
            headers={"Content-Disposition": f"attachment; filename=compressed_{file.filename}"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail="ফাইলটি প্রসেস করতে সমস্যা হয়েছে।")
