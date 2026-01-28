from fastapi import FastAPI
from app.core.config import settings
from app.routes.auth import auth_router
from app.routes.user import user_router
from contextlib import asynccontextmanager
from app.core.database import init_db
from app.middleware.auth_middleware import AuthMiddleware
from app.workers.email import start_email_worker
from app.services.queue import rabbitmq
from app.core.logger import logger
import threading

## set up cors later

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
		(auth_router, ["Auth"])
	]

	for router, tags, in routes:
		app.include_router(router, tags=tags)

# Global worker thread
_worker_thread = None

def _run_worker():
	try:
		start_email_worker()
	except Exception as e:
		logger.error(f"Email worker error: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
	global _worker_thread
	await init_db()
	
	# Start email worker in background thread
	_worker_thread = threading.Thread(target=_run_worker, daemon=True)
	_worker_thread.start()
	logger.info("Email worker thread started")
	
	yield
	
	# Shutdown email worker
	if _worker_thread and _worker_thread.is_alive():
		logger.info("Shutting down email worker...")
		rabbitmq.close()
	
app = create_fastapi_app(environment=settings.ENVIRONMENT, title="PayLink", lifespan=lifespan, root_path="/api/v1")
setup_routes(app)
app.add_middleware(AuthMiddleware)

@app.get("/health")
def health_check():
    return {"status": "healthy"}