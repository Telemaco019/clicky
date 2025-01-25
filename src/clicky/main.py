import logging
import subprocess
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from clicky.api.middlewares import LogMiddleware
from clicky.api.routes import router
from clicky.config import settings
from clicky.config.logging import setup_logging

setup_logging()
logger = logging.getLogger(__name__)


def _tailwind_build(watch: bool) -> subprocess.Popen[Any] | None:
    input_path = settings.STATIC_DIR / "src" / "tw.css"
    output_path = settings.STATIC_DIR / "css" / "main.css"
    logger.info(
        "Running tailwindcss in %s mode [input -> %s]",
        "watch" if watch else "build",
        input_path.as_posix(),
    )

    try:
        command = [
            "tailwindcss",
            "-i",
            input_path.as_posix(),
            "-o",
            output_path.as_posix(),
        ]
        if watch:
            command.append("--watch")

        # Run the process in non-blocking mode
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        logger.info("Started tailwindcss with PID %d", process.pid)
        return process
    except Exception as e:
        logger.error(f"Error running tailwindcss: {e}")
        return None


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None, None]:
    process = _tailwind_build(watch=settings.DEVELOPMENT_MODE)

    yield

    if not process:
        return

    logger.info("Stopping Tailwind process (PID %d)...", process.pid)
    process.terminate()
    try:
        process.wait(timeout=5)  # Wait for graceful termination
    except subprocess.TimeoutExpired:
        logger.warning(
            "Forcing termination of Tailwind process (PID %d)...", process.pid
        )
        process.kill()
    logger.info("Tailwind process terminated.")


def init_app() -> FastAPI:
    fastapi_app = FastAPI(
        title=settings.PROJECT_NAME,
        root_path=settings.ROOT_PATH,
        lifespan=lifespan,
    )
    fastapi_app.mount(
        "/static",
        StaticFiles(directory=settings.STATIC_DIR),
    )
    fastapi_app.add_middleware(LogMiddleware)
    fastapi_app.include_router(router)
    return fastapi_app


app = init_app()  # pragma: no cover
