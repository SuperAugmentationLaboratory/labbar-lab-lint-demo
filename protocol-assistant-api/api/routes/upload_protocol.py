# endpoints/upload_protocol.py
import mimetypes
import requests,io, logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Header, UploadFile, File
from fastapi.responses import JSONResponse
from requests_toolbelt.multipart.encoder import MultipartEncoder

from auth import verify_firebase_token
from utils.initialize import DANSWER_BASE_URL, load_api_endpoints
from config.headers import get_headers
from services.upload_service import UploadService
from exceptions.upload_exceptions import UploadException
from models.upload import UploadResponse, UploadError

from logging_config import logger

router = APIRouter()
api_endpoints = load_api_endpoints()

@router.post(
    "/async-upload-protocol",
    response_model=UploadResponse,
    responses={
        400: {"model": UploadError},
        401: {"model": UploadError},
        502: {"model": UploadError}
    }
)
async def async_upload_protocol(
    files: List[UploadFile] = File(...),
    token_data=Depends(verify_firebase_token)
):
    """
    Handle protocol file uploads with comprehensive error handling and logging
    """
    try:
        # Initialize upload service
        upload_service = UploadService(
            base_url=DANSWER_BASE_URL,
            headers=get_headers()
        )
        
        # Validate request
        if not files:
            raise HTTPException(status_code=400, detail="No files provided")
        
        # Prepare form data and upload files without AsyncExitStack
        form_data = await upload_service.prepare_upload_data(files)
        result = await upload_service.upload_files(
            api_endpoints['upload_file'],
            form_data
        )
        
        return UploadResponse(
            success=True,
            files=[file.filename for file in files],
            message="Files uploaded successfully"
        )
        
    except UploadException as e:
        logger.error(f"Upload error: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=e.status_code,
            content=UploadError(
                detail=e.message,
                error_code=e.error_code,
                additional_info=e.additional_info
            ).model_dump()
        )
        
    except HTTPException as e:
        logger.error(f"HTTP error: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=e.status_code,
            content=UploadError(
                detail=str(e.detail),
                error_code="HTTP_ERROR"
            ).model_dump
        )
        
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content=UploadError(
                detail="Internal server error",
                error_code="INTERNAL_ERROR"
            ).model_dump()
        )

@router.post("/upload-protocol")
async def upload_protocol(
    files: list[UploadFile] = File(...),
    token_data=Depends(verify_firebase_token)
    ):

    # URL for uploading files to the existing API
    url_upload_file = f"{DANSWER_BASE_URL}{api_endpoints['upload_file']}"

    fields = []
    for idx, file in enumerate(files):
        file_content = await file.read()
        mime_type, _ = mimetypes.guess_type(file.filename)
        print(f"MIME type for file {idx}: {mime_type}")
        if mime_type is None:
            mime_type = 'application/octet-stream'  # Fallback if type is unknown

        fields.append(
            ('files', (file.filename, file_content, mime_type))
        )

    multipart_data = MultipartEncoder(fields=fields)
    headers = get_headers()
    # Update headers with the correct Content-Type for multipart data
    headers.update({'Content-Type': multipart_data.content_type})
    print(f"Sending post request with multipart data: {multipart_data.len}")
    # Send POST request with manually encoded multipart data
    response = requests.post(url_upload_file, headers=headers, data=multipart_data)

    # Handle response
    if response.status_code != 200:
        return JSONResponse(status_code=response.status_code, content={"detail": "Failed to upload files", "error": response.text})

    # Return the response from the existing API
    return response.json()