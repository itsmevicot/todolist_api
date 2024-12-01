import time
from django.http import JsonResponse
from django.core.cache import cache


class RateLimitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        client_ip = self.get_client_ip(request)
        cache_key = f"rate_limit:{client_ip}"
        request_limit = 100
        time_window = 60

        data = cache.get(cache_key, {"count": 0, "start_time": time.time()})
        current_time = time.time()

        if current_time - data["start_time"] > time_window:
            data = {"count": 1, "start_time": current_time}
        else:
            data["count"] += 1

        if data["count"] > request_limit:
            retry_after = int(time_window - (current_time - data["start_time"]))
            return JsonResponse(
                {
                    "error": "Rate limit exceeded",
                    "retry_after": retry_after,
                },
                status=429,
            )

        cache.set(cache_key, data, timeout=time_window)

        response = self.get_response(request)
        return response

    @staticmethod
    def get_client_ip(request):
        """Get the client's IP address from the request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
