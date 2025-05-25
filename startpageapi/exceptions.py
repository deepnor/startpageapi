class StartpageError(Exception):
    pass

class StartpageHTTPError(StartpageError):
    def __init__(self, status_code: int, message: str = None):
        self.status_code = status_code
        self.message = message or f"HTTP {status_code} error"
        super().__init__(self.message)

class StartpageParseError(StartpageError):
    pass

class StartpageRateLimitError(StartpageHTTPError):
    def __init__(self):
        super().__init__(429, "Rate limit exceeded")
