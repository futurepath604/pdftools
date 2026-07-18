import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

# Render Environment ও আপনার গিটহাবের ফাইল স্ট্রাকচার অনুযায়ী সঠিক ইম্পোর্ট পাথ:
from app.tools.compressor import router as compress_router
from app.tools.merger import router as merge_router
from app.tools.image_to_pdf import router as image_router
from app.tools.modify import router as modify_router
from app.tools.security import router as security_router

app = FastAPI(title="Secure PDF Tools Pro - Modular Backend")

# সাব-টুলের সব পাইথন রাউটগুলো মেইন অ্যাপে রেজিস্টার করা হচ্ছে
app.include_router(compress_router)
app.include_router(merge_router)
app.include_router(image_router)
app.include_router(modify_router)
app.include_router(security_router)

# Static files (HTML, CSS, JS) কনফিগারেশন
# Render-এ পাথ ঠিক রাখতে absolute path ব্যবহার করা হয়েছে
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")

os.makedirs(STATIC_DIR, exist_ok=True)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# ড্যাশবোর্ড বা হোম রুট (index.html)
@app.get("/")
async def read_index():
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "FFuture's Workspace PDF Tools API is running perfectly! index.html not found."}

# ফ্রন্টএন্ড পেজগুলোর রাউটিং ডাইনামিকালি হ্যান্ডেল করার জন্য
@app.get("/{page_name}")
async def serve_page(page_name: str):
    page_mapping = {
        "compress": "compress.html",
        "merge": "merge.html",
        "image-to-pdf": "image-to-pdf.html",
        "split": "split.html",
        "rotate": "rotate.html",
        "delete-pages": "delete-pages.html",
        "lock-pdf": "lock.html",
        "unlock-pdf": "unlock.html",
        "office-to-pdf": "office.html"
    }
    
    if page_name in page_mapping:
        file_path = os.path.join(STATIC_DIR, page_mapping[page_name])
        if os.path.exists(file_path):
            return FileResponse(file_path)
        raise HTTPException(status_code=404, detail=f"{page_mapping[page_name]} file missing in static folder.")
    raise HTTPException(status_code=404, detail="Page not found")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
