import threading
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import Base, engine
from app.routers import accounts, events, filters, labels, scan, suggestions


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)

    from app.scanner.daemon import start_scheduler
    scheduler = start_scheduler()

    yield

    scheduler.shutdown(wait=False)


app = FastAPI(title=settings.app_name, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin, "http://localhost:80"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(accounts.router, prefix="/api/accounts", tags=["accounts"])
app.include_router(filters.router, prefix="/api/accounts/{account_id}/filters", tags=["filters"])
app.include_router(labels.router, prefix="/api/accounts/{account_id}/labels", tags=["labels"])
app.include_router(suggestions.router, prefix="/api/suggestions", tags=["suggestions"])
app.include_router(scan.router, prefix="/api/scan", tags=["scan"])
app.include_router(events.router, prefix="/api/events", tags=["events"])


def start() -> None:
    uvicorn.run("app.main:app", host=settings.api_host, port=settings.api_port, reload=False)
