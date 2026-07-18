from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import io
from PyPDF2 import PdfReader, PdfWriter

app = FastAPI()

# 🔒 এটি চিরকালের জন্য CORS পলিসি ফিক্স করে দিল, ভবিষ্যতে আর কোনো সমস্যা হবে না
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
async def compress_pdf(file: UploadFile = File(...)):
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="শুধুমাত্র PDF ফাইল সাপোর্ট করে।")
    
    try:
        pdf_bytes = await file.read()
        reader = PdfReader(io.BytesIO(pdf_bytes))
        writer = PdfWriter()
        
        for page in reader.pages:
            writer.add_page(page)
            
        # মেমরিতেই কম্প্রেস করার লজিক (ইন-মেমরি প্রসেস)
        for page in writer.pages:
            page.compress_content_streams()
            
        output_stream = io.BytesIO()
        writer.write(output_stream)
        output_stream.seek(0)
        
        return StreamingResponse(
            output_stream,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=compressed_{file.filename}"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
