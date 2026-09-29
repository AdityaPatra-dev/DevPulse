import time
from typing import Callable
from fastapi import Request, Response
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from starlette.middleware.base import BaseHTTPMiddleware

# Custom Metrics for Track B
REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total count of HTTP requests processed by endpoint and status code",
    ["method", "handler", "status"],
)

REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "Histogram of HTTP request processing latency in seconds",
    ["method", "handler"],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0),
)


class PrometheusMiddleware(BaseHTTPMiddleware):
    """Middleware for recording request counts and processing latency."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        method = request.method
        path = request.url.path

        # Group dynamic paths to prevent high cardinality in Prometheus
        handler = path
        if path.startswith("/incidents/") and path.split("/")[-1].isdigit():
            handler = "/incidents/{id}"

        status_code = 500
        try:
            response = await call_next(request)
            status_code = response.status_code
            return response
        finally:
            duration = time.time() - start_time
            # Ignore /metrics scraping itself from pollution if desired, or record all
            if path != "/metrics":
                REQUEST_COUNT.labels(method=method, handler=handler, status=str(status_code)).inc()
                REQUEST_LATENCY.labels(method=method, handler=handler).observe(duration)


def metrics_endpoint() -> Response:
    """Generate Prometheus metric scrape output."""
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
