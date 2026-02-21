from fastapi import FastAPI
from app.core.config import settings
from app.routes.auth import auth_router
from app.routes.user import user_router
from app.routes.links import link_router
from app.routes.payment import payment_router
from contextlib import asynccontextmanager
from app.core.database import init_db
from app.middleware.rate_limiter import RateLimiterMiddleware
from app.workers.email import start_email_worker
from app.services.queue import redis_queue
from app.core.logger import logger
import threading
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.workers.scheduler import cleanup_deleted_users
from fastapi.middleware.cors import CORSMiddleware

scheduler = AsyncIOScheduler()

origins = (
    ["http://127.0.0.1:5500", "http://localhost:5500"]
    # if settings.ENVIRONMENT == "dev"
    # else [
    #     "https://paylink.online",
    # ]
)

def create_fastapi_app(environment: str = "dev", title: str = "", root_path: str = "/api/v1", lifespan=None) -> FastAPI:
	config = {
		"title": title,
		"root_path": root_path,
	}

	if lifespan:
		config["lifespan"] = lifespan

	if environment == "prod":
		config.update({
			"redoc_url": None,
			"openapi_url": None,
			"docs_url": None
		})

	return FastAPI(**config)

def setup_routes(app: FastAPI) -> None:
	routes = [
		(user_router, ["User"]),
		(auth_router, ["Auth"]),
		(link_router, ["Links"]),
		(payment_router, ["Payments"]),
	]

	for router, tags, in routes:
		app.include_router(router, tags=tags)

# Global worker thread
worker_thread = None

def run_worker():
	try:
		start_email_worker()
	except Exception as e:
		logger.error(f"Email worker error: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
	global worker_thread
	await init_db()
	
	# Start email worker in background thread
	worker_thread = threading.Thread(target=run_worker, daemon=True)
	worker_thread.start()
	logger.info("Email worker thread started")
	
	# APScheduler for cleanup tasks
	scheduler.add_job(
        cleanup_deleted_users,
        "cron",
        hour=3,
        minute=0,
        id="cleanup_deleted_users",
        replace_existing=True
    )
	scheduler.start()
	logger.info("Scheduler started - cleanup job scheduled for 3 AM daily")
	
	yield
	
	# Shutdown scheduler
	scheduler.shutdown(wait=True)
	logger.info("Scheduler shut down")
	
	# Shutdown email worker
	if worker_thread and worker_thread.is_alive():
		logger.info("Shutting down email worker")
		redis_queue.close()
	
app = create_fastapi_app(environment=settings.ENVIRONMENT, title="PayLink", lifespan=lifespan, root_path="/api/v1")
setup_routes(app)

app.add_middleware(RateLimiterMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "healthy"}