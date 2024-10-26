# exceptions/upload_exceptions.py
class UploadException(Exception):
    def __init__(self, message: str, error_code: str, status_code: int = 400, additional_info: dict = None):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.additional_info = additional_info or {}
        super().__init__(self.message)

class FileValidationError(UploadException):
    def __init__(self, message: str, additional_info: dict = None):
        super().__init__(message, "FILE_VALIDATION_ERROR", 400, additional_info)

class UpstreamServiceError(UploadException):
    def __init__(self, message: str, additional_info: dict = None):
        super().__init__(message, "UPSTREAM_SERVICE_ERROR", 502, additional_info)