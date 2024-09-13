from starlette.middleware.base import BaseHTTPMiddleware

class ContentSecurityPolicyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers["Content-Security-Policy"] = "default-src 'self'; connect-src 'self' https://smartspeztech.com https://*.cloudfront.net http: https:;"
        return response