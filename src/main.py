import time
import logging
from fastapi import FastAPI, Request
from prometheus_fastapi_instrumentator import Instrumentator
from prometheus_client import Counter, Histogram
from src.logging_config import setup_logging
from src.api.routes.scraperRoutes import scraperRouter
from src.api.routes.authRoutes import authRouter
from src.api.routes.stayAwake import awakeRouter

app = FastAPI()

Instrumentator().instrument(app).expose(app, include_in_schema=False)

setup_logging()
log = logging.getLogger(__name__)

AUTH_REQUEST_COUNT = Counter('auth_request_count', 'Total number of requests to authRouter', ['method', 'endpoint'])
AUTH_REQUEST_LATENCY = Histogram('auth_request_latency_seconds', 'Request latency for authRouter', ['method', 'endpoint'])

SCRAPER_REQUEST_COUNT = Counter('scraper_request_count', 'Total number of requests to scraperRouter', ['method', 'endpoint'])
SCRAPER_REQUEST_LATENCY = Histogram('scraper_request_latency_seconds', 'Request latency for scraperRouter', ['method', 'endpoint'])

DEV_REQUEST_COUNT = Counter('dev_request_count', 'Total number of requests to devRouter', ['method', 'endpoint'])
DEV_REQUEST_LATENCY = Histogram('dev_request_latency_seconds', 'Request latency for devRouter', ['method', 'endpoint'])

@app.middleware("http")
async def add_custom_metrics(request: Request, call_next):
    method = request.method
    endpoint = request.url.path

    if endpoint.startswith("/auth"):
        
        AUTH_REQUEST_COUNT.labels(method=method, endpoint=endpoint).inc()
        start_time = time.time()
        response = await call_next(request)
        latency = time.time() - start_time
        AUTH_REQUEST_LATENCY.labels(method=method, endpoint=endpoint).observe(latency)
        return response
    elif endpoint.startswith("/scraper"):

        SCRAPER_REQUEST_COUNT.labels(method=method, endpoint=endpoint).inc()
        start_time = time.time()
        response = await call_next(request)
        latency = time.time() - start_time
        SCRAPER_REQUEST_LATENCY.labels(method=method, endpoint=endpoint).observe(latency)
        return response
    elif endpoint.startswith("/dev"):

        DEV_REQUEST_COUNT.labels(method=method, endpoint=endpoint).inc()
        start_time = time.time()
        response = await call_next(request)
        latency = time.time() - start_time
        DEV_REQUEST_LATENCY.labels(method=method, endpoint=endpoint).observe(latency)
        return response
    else:
        return await call_next(request)

app.include_router(authRouter, prefix="/auth", tags=["auth"])
app.include_router(scraperRouter, prefix="/scraper" ,tags=["scraper"])
app.include_router(awakeRouter, prefix="/dev")

@app.get("/")
def read_root():
    return {"message": "Welcome to Url Scraper"}
