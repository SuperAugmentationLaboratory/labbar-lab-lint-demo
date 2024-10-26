# services/file_service.py
import logging
import io
from typing import List, Tuple, BinaryIO
from fastapi import UploadFile
from exceptions.upload_exceptions import FileValidationError

logger = logging.getLogger(__name__)

class FileService:
    ALLOWED_MIME_TYPES = {
        'application/pdf',
        'text/plain',
        'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    }
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

    @staticmethod
    async def validate_file(file: UploadFile) -> None:
        """Validate a single file's size and type"""
        if not file.filename:
            raise FileValidationError("File must have a name")

        if file.content_type not in FileService.ALLOWED_MIME_TYPES:
            raise FileValidationError(
                f"Unsupported file type: {file.content_type}",
                {"allowed_types": list(FileService.ALLOWED_MIME_TYPES)}
            )

        # Read file content for size validation
        content = await file.read()
        if len(content) > FileService.MAX_FILE_SIZE:
            raise FileValidationError(
                "File too large",
                {"max_size": FileService.MAX_FILE_SIZE, "received_size": len(content)}
            )
        
        # Reset file pointer
        await file.seek(0)

    @staticmethod
    async def prepare_file(file: UploadFile) -> Tuple[str, str, BinaryIO, str]:
        """Prepare a single file for upload"""
        content = await file.read()
        await file.seek(0)
        return (
            'file',
            file.filename,
            io.BytesIO(content),
            file.content_type
        )