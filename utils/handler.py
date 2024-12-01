import logging
from rest_framework.views import exception_handler
from rest_framework.response import Response
from django.conf import settings

from utils.exceptions import ExceptionMessageBuilder

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    view = context.get("view", None)
    view_name = view.__class__.__name__ if view else "Unknown View"
    request = context.get("request", None)
    request_info = {
        "method": getattr(request, "method", "Unknown Method"),
        "url": getattr(request, "build_absolute_uri", lambda: "Unknown URL")(),
    }

    if response is not None:
        custom_response = {
            "error": response.data.get("detail", "An error occurred."),
            "detail": {k: v for k, v in response.data.items() if k != "detail"},
        }
        logger.warning(
            f"Handled Exception:\n"
            f"  Type: {type(exc).__name__}\n"
            f"  Detail: {response.data}\n"
            f"  View: {view_name}\n"
            f"  Request Method: {request_info['method']}\n"
            f"  Request URL: {request_info['url']}\n"
        )
        return Response(custom_response, status=response.status_code)

    if isinstance(exc, ExceptionMessageBuilder):
        custom_response = {
            "error": exc.message,
            "detail": exc.detail,
        }
        logger.error(
            f"Custom Exception:\n"
            f"  Type: {type(exc).__name__}\n"
            f"  Message: {exc.message}\n"
            f"  Detail: {exc.detail}\n"
            f"  View: {view_name}\n"
            f"  Request Method: {request_info['method']}\n"
            f"  Request URL: {request_info['url']}\n"
        )
        return Response(custom_response, status=exc.status_code)

    logger.error(
        f"Unhandled Exception:\n"
        f"  Type: {type(exc).__name__}\n"
        f"  Message: {str(exc)}\n"
        f"  View: {view_name}\n"
        f"  Request Method: {request_info['method']}\n"
        f"  Request URL: {request_info['url']}\n",
        exc_info=True,
    )

    if settings.DEBUG:
        return Response(
            {
                "error": str(exc),
            },
            status=500,
        )

    return Response(
        {
            "error": "An unexpected error occurred.",
        },
        status=500,
    )
