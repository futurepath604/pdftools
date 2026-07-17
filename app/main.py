from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

# মডুলার টুলগুলো ইমপোর্ট করা
from app.tools.merger import merge_pdfs_logic
from app.tools.compressor import compress_pdf_logic
from app.tools.image_to_pdf import images_to_pdf_logic
from app.tools.pdf_to_image import pdf_to_images_zip_logic

app = FastAPI(
    title="Secure PDF Tools API",
    description="100% Free & Private PDF Tools. No files are saved on the server.",
    version="1.0.0"
)

# সিকিউরিটি এবং কর্স (CORS) পলিসি সেটআপ
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ১৫ মেগাবাইট ফাইল সাইজ লিমিট (সার্ভার সেফটি ও ফ্রি টিয়ার সাপোর্ট)
MAX_FILE_SIZE = 15 * 1024 * 1024 

# হোমপেজ ইন্ট্রোডাকশন
@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    <html>
        <head>
            <title>Secure PDF Tools Platform</title>
            <style>
                body { font-family: sans-serif; text-align: center; padding: 50px; background: #f8fafc; color: #334155; }
                h1 { color: #4f46e5; }
                .btn { display: inline-block; background: #4f46e5; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; margin-top: 20px; font-weight: bold; }
            </style>
        </head>
        <body>
            <h1>📄 Secure PDF Tools Online</h1>
            <p>Your files are processed in-memory (RAM) and are never stored anywhere on our servers.</p>
            <p>This API platform is ready and live!</p>
            <a href="/docs" class="btn">Try Web UI Dashboard</a>
        </body>
    </html>
    """

# ১. PDF Merge API Endpoint
@app.post("/api/merge")
async def api_merge(files: list[UploadFile] = File(...)):
    pdf_contents = []
    for file in files:
        content = await file.read()
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail=f"File {file.filename} exceeds 15MB limit!")
        pdf_contents.append(content)
        
    try:
        output_stream = merge_pdfs_logic(pdf_contents)
        return StreamingResponse(
            output_stream, 
            media_type="application/pdf", 
            headers={"Content-Disposition": "attachment; filename=merged_output.pdf"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error merging PDF files.")

# ২. PDF Compress API Endpoint
@app.post("/api/compress")
async def api_compress(file: UploadFile = File(...)):
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File exceeds 15MB limit!")
        
    try:
        output_stream = compress_pdf_logic(content)
        return StreamingResponse(
            output_stream, 
            media_type="application/pdf", 
            headers={"Content-Disposition": f"attachment; filename=compressed_{file.filename}"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error compressing PDF.")

# ৩. Image to PDF API Endpoint
@app.post("/api/image-to-pdf")
async def api_image_to_pdf(files: list[UploadFile] = File(...)):
    image_contents = []
    for file in files:
        content = await file.read()
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail=f"File {file.filename} exceeds 15MB limit!")
        image_contents.append(content)
        
    try:
        output_stream = images_to_pdf_logic(image_contents)
        return StreamingResponse(
            output_stream, 
            media_type="application/pdf", 
            headers={"Content-Disposition": "attachment; filename=images_converted.pdf"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error converting images to PDF.")

# ৪. PDF to Image (ZIP) API Endpoint
@app.post("/api/pdf-to-image")
async def api_pdf_to_image(file: UploadFile = File(...)):
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File exceeds 15MB limit!")
        
    try:
        zip_stream = pdf_to_images_zip_logic(content)
        return StreamingResponse(
            zip_stream, 
            media_type="application/zip", 
            headers={"Content-Disposition": f"attachment; filename={file.filename.split('.')[0]}_images.zip"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error converting PDF to Images.")
