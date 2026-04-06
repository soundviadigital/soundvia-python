class SoundviaError(Exception):
    pass


class AuthenticationError(SoundviaError):
    pass


class NotFoundError(SoundviaError):
    pass


class RateLimitError(SoundviaError):
    def __init__(self, message: str = "Rate limit exceeded", retry_after: int | None = None):
        super().__init__(message)
        self.retry_after = retry_after


class APIError(SoundviaError):
    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code
