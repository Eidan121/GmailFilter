import asyncio

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.scanner.notifier import get_sse_queue

router = APIRouter()


@router.get("/stream")
async def sse_stream():
    async def event_generator():
        queue = get_sse_queue()
        yield "data: {\"type\":\"connected\"}\n\n"
        while True:
            try:
                data = await asyncio.wait_for(queue.get(), timeout=30.0)
                yield f"data: {data}\n\n"
            except asyncio.TimeoutError:
                yield ": heartbeat\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
