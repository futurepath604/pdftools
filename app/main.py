import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

# আলাদা ফাইলগুলো থেকে রাউটার ইম্পোর্ট করা হচ্ছে
from apps.compress import router as compress_router
from apps.merge import router as merge_router
from apps.image_to_pdf import router as image_router
from apps.modify import router as modify_router
from apps.security import router as security_router

app = FastAPI(title="Secure PDF Tools Pro - Modular Backend")

# সব সাব-টুলের পাইথন রাউটগুলো মেইন অ্যাপে যুক্ত করা হচ্ছে
app.include_router(compress_router)
app.include_router(merge_router)
app.include_router(image_router)
app.include_router(modify_router)
app.include_router(security_router)

# Static files mapping
os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def read_index():
    index_path = os.path.join("static", "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "FFuture's Workspace PDF Modular API is running perfectly!"}

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
        file_path = os.path.join("static", page_mapping[page_name])
        if os.path.exists(file_path):
            return FileResponse(file_path)
        raise HTTPException(status_code=404, detail=f"{page_mapping[page_name]} file missing in static folder.")
    raise HTTPException(status_code=404, detail="Page not found")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
