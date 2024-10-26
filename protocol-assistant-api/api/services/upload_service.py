# services/upload_service.py
import aiohttp
import logging
from typing import List, Dict, Any
from fastapi import UploadFile
from exceptions.upload_exceptions import UpstreamServiceError
from services.file_service import FileService

logger = logging.getLogger(__name__)

class UploadService:
    def __init__(self, base_url: str, headers: Dict[str, str]):
        self.base_url = base_url
        self.headers = headers

    async def prepare_upload_data(self, files: List[UploadFile]) -> aiohttp.FormData:
        """Prepare form data for upload"""
        form = aiohttp.FormData()
        
        for file in files:
            await FileService.validate_file(file)
            # Get file content
            file_content = await file.read()
            field_name = "files"  # Consistent field name for each file
            
            form.add_field(
                field_name,
                file_content,
                filename=file.filename,
                content_type=file.content_type or 'application/octet-stream'
            )
        
        return form

    async def upload_files(self, endpoint: str, form_data: aiohttp.FormData) -> Dict[str, Any]:
        """Upload files to the specified endpoint"""
        async with aiohttp.ClientSession() as session:
            try:
                url = f"{self.base_url}{endpoint}"
                logger.debug(f"Uploading files to {url}")
                
                async with session.post(
                    url,
                    headers=self.headers,
                    data=form_data
                ) as response:
                    response_data = await response.json()
                    
                    if response.status != 200:
                        logger.error(f"Upload failed: {response.status} - {response_data}")
                        raise UpstreamServiceError(
                            "Failed to upload files to upstream service",
                            {"response": response_data, "status": response.status}
                        )
                    
                    return response_data
                    
            except aiohttp.ClientError as e:
                logger.error(f"Client error during upload: {str(e)}")
                raise UpstreamServiceError(
                    "Connection error with upstream service",
                    {"error": str(e)}
                )
