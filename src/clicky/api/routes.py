import logging
from typing import Annotated

import sqlfluff
from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from clicky.api.deps import (
    Clickhouse_T,
    OpenAIService_T,
    SessionService_T,
    UserSession_T,
)
from clicky.api.schemas import Props, RunQueryProps
from clicky.config import settings
from clicky.services import OptimizedQuery

templates = Jinja2Templates(directory=settings.TEMPLATES_DIR)
router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/")
async def index(req: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request=req,
        name="index.html",
        context={
            "props": {},
        },
    )


@router.post("/queries/format")
async def format_query(req: Request, query: Annotated[str, Form()]) -> HTMLResponse:
    res = sqlfluff.fix(query, dialect="clickhouse")
    return templates.TemplateResponse(
        request=req,
        name="components/_query_input.html",
        context={"props": {"query": res}},
    )


@router.post("/queries/optimize")
async def optimize_query(
    openai_svc: OpenAIService_T,
    *,
    req: Request,
    query: Annotated[str, Form()],
) -> HTMLResponse:
    optimized_query: OptimizedQuery | None = None
    error: str | None = None
    try:
        optimized_query = await openai_svc.optimize_query(
            query=query,
        )
    except Exception as e:
        logger.exception(e)
        error = str(e)
    return templates.TemplateResponse(
        name="responses/optimize_query_resp.html",
        request=req,
        context={
            "props": Props(
                content=optimized_query,
                error=error,
            ),
        },
    )


@router.post("/queries/run")
async def run_query(
    clickhouse_service: Clickhouse_T,
    session_service: SessionService_T,
    user_session: UserSession_T,
    *,
    req: Request,
    query: Annotated[str, Form()],
) -> HTMLResponse:
    error: str | None = None
    content: RunQueryProps | None = None
    try:
        # Run the query
        result = await clickhouse_service.run_query(query)
        # Create a new executed query entry
        executed_query = await session_service.save_query(
            session_id=user_session.id,
            query=query,
            result=result,
        )
        content = RunQueryProps(
            query_id=executed_query.id,
            query=query,
            query_result=result,
        )
    except Exception as e:
        error = str(e)
    return templates.TemplateResponse(
        request=req,
        name="responses/run_query_resp.html",
        context={
            "props": Props(
                error=error,
                content=content,
            ),
        },
    )
