import pytest
from django.http import HttpResponse
from django.test import RequestFactory
from django.core.cache import cache
from utils.middlewares import RateLimitMiddleware
import time


@pytest.fixture
def rate_limit_middleware():
    """Fixture to initialize the middleware."""

    def dummy_get_response(request):
        return HttpResponse("OK")

    return RateLimitMiddleware(dummy_get_response)


@pytest.fixture
def request_factory():
    """Fixture to provide a request factory."""
    return RequestFactory()


def test_rate_limit_within_limit(rate_limit_middleware, request_factory):
    """Test that requests within the limit are allowed."""
    cache.clear()
    request = request_factory.get("/")
    request.META["REMOTE_ADDR"] = "127.0.0.1"

    for _ in range(100):
        response = rate_limit_middleware(request)
        assert response.status_code == 200


def test_rate_limit_exceeded(rate_limit_middleware, request_factory):
    """Test that exceeding the limit returns a 429 response."""
    cache.clear()
    request = request_factory.get("/")
    request.META["REMOTE_ADDR"] = "127.0.0.1"

    for _ in range(101):
        response = rate_limit_middleware(request)

    assert response.status_code == 429
    assert "Rate limit exceeded" in response.content.decode()


def test_rate_limit_reset_after_window(rate_limit_middleware, request_factory):
    """Test that the rate limit resets after the time window."""
    cache.clear()
    request = request_factory.get("/")
    request.META["REMOTE_ADDR"] = "127.0.0.1"

    for _ in range(100):
        response = rate_limit_middleware(request)
        assert response.status_code == 200

    time.sleep(60)

    response = rate_limit_middleware(request)
    assert response.status_code == 200
