class KeruyunAPIError(Exception):
    def __init__(self, code: int, message: str, path: str):
        self.code = code
        self.message = message
        self.path = path
        super().__init__(f"[{code}] {message} ({path})")


class KeruyunAuthError(KeruyunAPIError):
    pass
