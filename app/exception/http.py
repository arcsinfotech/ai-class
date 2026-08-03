from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
from fastapi.responses import JSONResponse
import logging

log = logging.getLogger(__name__)

class GlobalExceptionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> JSONResponse:
        try:
        
            return await call_next(request)
        
        except Exception as e:
            log.exception(e, exc_info=True)
            return JSONResponse(
                status_code=500, 
                content={
                    "error": "Something went wrong, Please try again later"
                },
                headers={"Access-Control-Allow-Origin": "*",}
            )