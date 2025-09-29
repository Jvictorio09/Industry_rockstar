# E:\New Downloads\industry_rockstar\myProject\myApp\middleware.py

class FrameAncestorsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        resp = self.get_response(request)
        # Allow local dev + prod partner domains to embed your widget
        resp["Content-Security-Policy"] = (
            "frame-ancestors 'self' "
            "http://localhost:8000 http://127.0.0.1:8000 "
            "http://localhost:3000 http://127.0.0.1:3000 "
            "http://localhost:5173 http://127.0.0.1:5173 "
            "https://solutionsforchange.org https://www.solutionsforchange.org"
        )
        return resp
