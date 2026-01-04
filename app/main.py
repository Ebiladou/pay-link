from fastapi import FastAPI
from app.core.config import settings
from app.routes.auth import auth_router
from app.routes.user import user_router
from contextlib import asynccontextmanager
from app.core.database import init_db

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
		
@asynccontextmanager
async def lifespan(app: FastAPI):
	await init_db()
	yield
	
app = create_fastapi_app(environment=settings.ENVIRONMENT, title="PayLink", lifespan=lifespan, root_path="/api/v1")
setup_routes(app)

@app.get("/health")
def health_check():
    return {"status": "healthy"}