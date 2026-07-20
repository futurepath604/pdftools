import json
import os
import uuid
from typing import List
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
import pypdf

# Create a clean dedicated router for PDF Rearrange tool
router = APIRouter(prefix="/api", tags=["Rearrange PDF"])

def remove_file(path: str):
    """Background task to safely remove the output file after streaming."""
    if os.path.exists(path):
        try:
            os.remove(path)
        except Exception:
            pass

@router.post("/rearrange-pdf")
async def rearrange_pdf(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...),
    sequence: str = Form(...)
):
    """
    API endpoint to arrange and rearrange pages across multiple uploaded PDFs.
    Expected sequence format parsed from frontend:
    [{"file_index": 0, "pages": [0, 1, 2]}, {"file_index": 1, "pages": [4, 1]}]
    """
    temp_files = []
    output_filename = f"arranged_{uuid.uuid4().hex}.pdf"
    
    try:
        # 1. Save all uploaded files locally into a temporary workspace safely
        for uploaded_file in files:
            if not uploaded_file.filename.lower().endswith('.pdf'):
                raise HTTPException(status_code=400, detail="All uploaded files must be PDFs.")
            
            temp_path = f"temp_{uuid.uuid4().hex}_{uploaded_file.filename}"
            with open(temp_path, "wb") as buffer:
                buffer.write(await uploaded_file.read())
            temp_files.append(temp_path)
            
        # 2. Parse the sequence payload
        try:
            sequence_rules = json.loads(sequence)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid sequence compilation payload.")
            
        # 3. Process layout sequence with pypdf structural reader
        writer = pypdf.PdfWriter()
        
        for block in sequence_rules:
            file_idx = block.get("file_index")
            pages_to_add = block.get("pages", [])
            
            # Validation check
            if file_idx is None or file_idx < 0 or file_idx >= len(temp_files):
                raise HTTPException(status_code=400, detail=f"File identifier index out of bounds.")
                
            # Open target file and pull exactly requested pages mapping
            reader = pypdf.PdfReader(temp_files[file_idx])
            total_pages = len(reader.pages)
            
            for p_num in pages_to_add:
                if 0 <= p_num < total_pages:
                    writer.add_page(reader.pages[p_num])
                else:
                    # Skip or handle out-of-bound page requests safely
                    continue
                    
        # Check if the output has at least one page
        if len(writer.pages) == 0:
            raise HTTPException(status_code=400, detail="The operation resulted in a PDF with 0 pages.")

        # 4. Save file out
        with open(output_filename, "wb") as out_f:
            writer.write(out_f)
            
        # Register background task to delete the output file after it is successfully served
        background_tasks.add_task(remove_file, output_filename)
        
        return FileResponse(
            output_filename, 
            media_type="application/pdf", 
            filename="arranged_document.pdf"
        )
        
    except HTTPException as he:
        if os.path.exists(output_filename):
            os.remove(output_filename)
        raise he
    except Exception as e:
        if os.path.exists(output_filename):
            os.remove(output_filename)
        raise HTTPException(status_code=500, detail=f"Arrangement pipeline failure: {str(e)}")
        
    finally:
        # Cleanup routine for uploaded storage state lifecycle management
        for t_file in temp_files:
            if os.path.exists(t_file):
                try:
                    os.remove(t_file)
                except:
                    pass
