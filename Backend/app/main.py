import sys
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse

# Add Backend root directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.core.config import settings
from app.routers import auth, products, cart, orders, recommendations, ai, seller, admin

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Full-stack AI-Enhanced e-Commerce Platform with KNN recommendations and Google Gemini Generative AI.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enable CORS for local development and browser clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers under /api
app.include_router(auth.router, prefix=settings.API_PREFIX)
app.include_router(products.router, prefix=settings.API_PREFIX)
app.include_router(cart.router, prefix=settings.API_PREFIX)
app.include_router(orders.router, prefix=settings.API_PREFIX)
app.include_router(recommendations.router, prefix=settings.API_PREFIX)
app.include_router(ai.router, prefix=settings.API_PREFIX)
app.include_router(seller.router, prefix=settings.API_PREFIX)
app.include_router(admin.router, prefix=settings.API_PREFIX)


@app.get("/api/health", tags=["Health"])
def health_check():
    """Health check endpoint to verify backend status."""
    return {
        "status": "online",
        "app": settings.PROJECT_NAME,
        "api_version": "1.0.0"
    }


# Mount Frontend static files
frontend_dir = settings.FRONTEND_DIR

if frontend_dir.exists():
    # Mount frontend directory for direct browser viewing
    app.mount("/static", StaticFiles(directory=str(frontend_dir)), name="static")

    @app.get("/", tags=["Frontend"])
    async def serve_index():
        index_file = frontend_dir / "index.html"
        if index_file.exists():
            return FileResponse(str(index_file))
        return {"message": f"{settings.PROJECT_NAME} API is active. Open /docs for Swagger."}

    # Serve top-level frontend pages directly from root paths (e.g. /login.html, /cart.html)
    @app.get("/{page_name}.html", tags=["Frontend"])
    async def serve_html_page(page_name: str):
        target = frontend_dir / f"{page_name}.html"
        if target.exists():
            return FileResponse(str(target))
        return JSONResponse(status_code=404, content={"detail": f"Page '{page_name}.html' not found."})

    # Serve seller and admin subfolder pages
    @app.get("/seller/{page_name}.html", tags=["Frontend"])
    async def serve_seller_page(page_name: str):
        target = frontend_dir / "seller" / f"{page_name}.html"
        if target.exists():
            return FileResponse(str(target))
        return JSONResponse(status_code=404, content={"detail": f"Seller page '{page_name}.html' not found."})

    @app.get("/admin/{page_name}.html", tags=["Frontend"])
    async def serve_admin_page(page_name: str):
        target = frontend_dir / "admin" / f"{page_name}.html"
        if target.exists():
            return FileResponse(str(target))
        return JSONResponse(status_code=404, content={"detail": f"Admin page '{page_name}.html' not found."})

    # Mount css, js, and assets directories directly at /css, /js, /assets
    for sub in ["css", "js", "assets"]:
        sub_path = frontend_dir / sub
        if sub_path.exists():
            app.mount(f"/{sub}", StaticFiles(directory=str(sub_path)), name=sub)


if __name__ == "__main__":
    import os
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "0.0.0.0")
    debug = os.environ.get("DEBUG", "False").lower() in ("true", "1")
    uvicorn.run("app.main:app", host=host, port=port, reload=debug)

