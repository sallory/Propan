import asyncio
from typing import Any, Optional

from propan.brokers.model.schemas import BaseHandler


async def call_handler(
    handler: BaseHandler,
    message: Any,
    callback: bool = False,
    callback_timeout: Optional[float] = 30.0,
    raise_timeout: bool = False,
) -> Any:
    r = handler.callback(message)
    try:
        result = await asyncio.wait_for(r, timeout=callback_timeout)
    except asyncio.TimeoutError as e:
        if raise_timeout is True:  # pragma: no branch
            raise e
        result = None

    if callback is True:  # pragma: no branch
        return result