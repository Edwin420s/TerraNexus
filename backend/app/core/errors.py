from fastapi import Request
from fastapi.responses import JSONResponse

async def domain_error_handler(request: Request, exc: Exception):
    status = getattr(exc, "status_code", 400)
    code = getattr(exc, "code", "domain_error")
    message = str(exc) or "The request could not be completed."
    return JSONResponse(status_code=status, content={"error": {"code": code, "message": message}, "request_id": getattr(request.state, "request_id", None)})

class DomainError(Exception):
    status_code = 400
    code = "domain_error"

class SafetyInterlockError(DomainError):
    status_code = 409
    code = "safety_interlock_blocked"
