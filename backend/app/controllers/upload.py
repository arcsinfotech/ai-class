import os
import uuid
from fastapi import APIRouter, File, UploadFile, HTTPException
from app.models import supabase_client
from app.schemas.upload import UploadRequest
from app.configs import settings

router = APIRouter()

BUCKET_NAME = "ai-class"
SIGNED_URL_EXPIRY = 60*10

MAX_FILE_SIZE = 10 * 1024 * 1024
MIN_FILE_SIZE = 1024

ALLOWED_EXTENTIONS= ['.pdf', '.docx']

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    supabase = supabase_client.supabase

    if supabase is None:
        raise HTTPException(status_code=503, detail="Supabase client not initialized")
    
    if file.size is not None and file.size > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File size exceeds the maximum allowed size")
    
    if file.size is None and file.size < MIN_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File size is too small")
    
    extension = os.path.splitext(file.filename)[1]

    print(extension.lower())
    if extension.lower() not in ALLOWED_EXTENTIONS:
        raise HTTPException(status_code=400, detail="Unsupported file extension")

    file_name = f"{uuid.uuid4()}{extension}"

    file_data = await file.read()

    await supabase.storage.from_(BUCKET_NAME).upload(
        path=file_name,
        file=file_data,
        file_options={
            "content-type": file.content_type or "applcation/octet-stream"
        }
    )

    public_url = await supabase.storage.from_(BUCKET_NAME).get_public_url(
        file_name
    )

    return {
        "message": "File uploaded successfully",
        "filename": file.filename,
        "path": file_name,
        "url": public_url
    }


@router.post("/upload2")
async def upload_file2(data: UploadRequest):

    supabase = supabase_client.supabase

    if supabase is None:
        raise HTTPException(status_code=503, detail="Supabase client not initialized")
    
    file_name = f"{uuid.uuid4()}.pdf"

    try:
        response = await supabase.storage.from_(BUCKET_NAME).create_signed_upload_url(file_name)

        return {
            "message": "Upload URL generated successfully",
            "path": file_name,
            "token": response['token'],
            "signed_url": response['signed_url'],
            "expires_at": SIGNED_URL_EXPIRY,
            "future_url": f"{settings.SUPABASE_URL}/storage/v1/object/public/{BUCKET_NAME}/{file_name}"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading file: {str(e)}")