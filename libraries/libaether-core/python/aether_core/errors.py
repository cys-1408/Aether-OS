"""Error types shared across services."""


class AetherError(Exception):
    """Base error with machine-readable code."""

    def __init__(self, code: str, message: str, *, retriable: bool = False, details=None):
        super().__init__(message)
        self.code = code
        self.message = message
        self.retriable = retriable
        self.details = details

    def to_dict(self):
        return {"code": self.code, "message": self.message,
                "retriable": self.retriable, "details": self.details}


class IpcError(AetherError):
    """Error carried over the JSON-RPC wire."""

    def __init__(self, code: str, message: str, *, jsonrpc_code: int = -32000,
                 retriable: bool = False, details=None):
        super().__init__(code, message, retriable=retriable, details=details)
        self.jsonrpc_code = jsonrpc_code
