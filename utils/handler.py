import logging
from rest_framework.views import exception_handler
from rest_framework.response import Response
from django.conf import settings

from utils.exceptions import ExceptionMessageBuilder

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    view = context.get("view", "Unknown View")
    request = context.get("request", None)
    request_info = {
        "method": request.method if request else "Unknown Method",
        "url": request.build_absolute_uri() if request else "Unknown URL",
    }

    if response is not None:
        custom_response = {
            "error": response.data.get("detail", "An error occurred.")
        }

        extra_details = {k: v for k, v in response.data.items() if k != "detail"}
        if extra_details:
            custom_response["detail"] = extra_details

        logger.warning(
            f"Handled Exception:\n"
            f"  Type: {type(exc).__name__}\n"
            f"  Detail: {response.data}\n"
            f"  View: {view.__class__.__name__}\n"
            f"  Request: {request_info}\n"
        )
        return Response(custom_response, status=response.status_code)

    if isinstance(exc, ExceptionMessageBuilder):
        custom_response = {
            "error": exc.message,
            "detail": exc.detail
        }
        logger.error(
            f"Custom Exception | Type: {type(exc).__name__} | Message: {exc.message} | "
            f"Detail: {exc.detail} | View: {view.__class__.__name__} | Request: {request_info}"
        )
        return Response(custom_response, status=exc.status_code)

    logger.error(
        f"Unhandled Exception | Type: {type(exc).__name__} | Message: {str(exc)} | "
        f"View: {view.__class__.__name__} | Request: {request_info}",
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
