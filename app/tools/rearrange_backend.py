import json
from typing import List
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
import pypdf
import os
import uuid

router = APIRouter()

@router.post("/api/rearrange-pdf")
async def rearrange_pdf(
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
            if file_idx < 0 or file_idx >= len(temp_files):
                raise HTTPException(status_code=400, detail=f"File identifier index {file_idx + 1} out of bounds.")
                
            # Open target file and pull exactly requested pages mapping
            reader = pypdf.PdfReader(temp_files[file_idx])
            total_pages = len(reader.pages)
            
            for p_num in pages_to_add:
                if 0 <= p_num < total_pages:
                    writer.add_page(reader.pages[p_num])
                else:
                    # Skip or throw exception based on dynamic boundary condition rules
                    continue
                    
        # 4. Save file out
        with open(output_filename, "wb") as out_f:
            writer.write(out_f)
            
        return FileResponse(
            output_filename, 
            media_type="application/pdf", 
            filename="arranged_document.pdf"
        )
        
    except Exception as e:
        if os.path.exists(output_filename):
            os.remove(output_filename)
        raise HTTPException(status_code=500, detail=f"Arrangement pipeline failure: {str(e)}")
        
    finally:
        # Cleanup routine for storage state lifecycle management
        for t_file in temp_files:
            if os.path.exists(t_file):
                os.remove(t_file)
