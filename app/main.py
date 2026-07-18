from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

# কম্প্রেসার ইঞ্জিন ইম্পোর্ট
from app.tools.compressor import compress_pdf_logic

app = FastAPI()

# CORS পলিসি কনফিগারেশন
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"] # 👈 এটি ব্রাউজারকে ফাইল ডাউনলোডের সব ডাটা দেখতে সাহায্য করবে
)

@app.get("/")
def read_root():
    return {"status": "online"}

@app.post("/api/compress")
async def api_compress(file: UploadFile = File(...)):
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="শুধুমাত্র PDF ফাইল সাপোর্ট করে।")
    
    try:
        content = await file.read()
        if len(content) > 15 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="ফাইল সাইজ ১৫ মেগাবাইটের বেশি হওয়া যাবে না।")
            
        output_stream = compress_pdf_logic(content)
        
        # হেডারগুলোকে আরও শক্তিশালী করা হয়েছে যেন ব্রাউজার ব্লক না করে
        headers = {
            "Content-Disposition": f"attachment; filename=compressed_{file.filename}",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, GET, OPTIONS",
            "Access-Control-Allow-Headers": "*"
        }
        
        return StreamingResponse(
            output_stream, 
            media_type="application/pdf", 
            headers=headers
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error processing PDF")
