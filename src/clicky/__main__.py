import uvicorn

from clicky.config import settings

if __name__ == "__main__":  # pragma: no cover
    uvicorn.run(
        "clicky.main:app",
        host=settings.SERVER_HOST,
        port=settings.SERVER_PORT,
        reload=settings.DEVELOPMENT_MODE,
        access_log=False,
    )
