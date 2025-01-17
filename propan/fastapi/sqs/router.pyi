import logging
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Sequence, Type, Union

from aiobotocore.config import AioConfig
from fastapi import params
from fastapi.datastructures import Default
from fastapi.routing import APIRoute
from fastapi.utils import generate_unique_id
from starlette import routing
from starlette.responses import JSONResponse, Response
from starlette.types import ASGIApp

from propan import SQSBroker
from propan.brokers.sqs.schema import SQSQueue
from propan.fastapi.core.router import PropanRouter
from propan.log import access_logger
from propan.types import AnyCallable

<<<<<<< HEAD
class SQSRouter(PropanRouter):
    broker: SQSBroker

=======
class SQSRouter(PropanRouter[SQSBroker]):
>>>>>>> 1acd1a468477ed27a085d3d1c6f38d967e64f1f9
    def __init__(
        self,
        url: str = "http://localhost:9324/",
        *,
        region_name: Optional[str] = None,
        api_version: Optional[str] = None,
        use_ssl: bool = True,
        verify: Optional[bool] = None,
        aws_access_key_id: Optional[str] = None,
        aws_secret_access_key: Optional[str] = None,
        aws_session_token: Optional[str] = None,
        config: Optional[AioConfig] = None,
        # FastAPI kwargs
        prefix: str = "",
        tags: Optional[List[Union[str, Enum]]] = None,
        dependencies: Optional[Sequence[params.Depends]] = None,
        default_response_class: Type[Response] = Default(JSONResponse),
        responses: Optional[Dict[Union[int, str], Dict[str, Any]]] = None,
        callbacks: Optional[List[routing.BaseRoute]] = None,
        routes: Optional[List[routing.BaseRoute]] = None,
        redirect_slashes: bool = True,
        default: Optional[ASGIApp] = None,
        dependency_overrides_provider: Optional[Any] = None,
        route_class: Type[APIRoute] = APIRoute,
        on_startup: Optional[Sequence[Callable[[], Any]]] = None,
        on_shutdown: Optional[Sequence[Callable[[], Any]]] = None,
        deprecated: Optional[bool] = None,
        include_in_schema: bool = True,
        generate_unique_id_function: Callable[[APIRoute], str] = Default(
            generate_unique_id
        ),
        # Broker kwargs
        logger: Optional[logging.Logger] = access_logger,
        log_level: int = logging.INFO,
        log_fmt: Optional[str] = None,
        apply_types: bool = True,
    ) -> None:
        pass
    def add_api_mq_route(  # type: ignore[override]
        self,
        queue: Union[str, SQSQueue],
        *,
        wait_interval: int = 1,
        max_messages_number: int = 10,  # 1...10
        attributes: Sequence[str] = (),
        message_attributes: Sequence[str] = (),
        request_attempt_id: Optional[str] = None,
        visibility_timeout: int = 0,
        retry: Union[bool, int] = False,
        endpoint: AnyCallable,
    ) -> None:
        pass
    def event(  # type: ignore[override]
        self,
        queue: Union[str, SQSQueue],
        *,
        wait_interval: int = 1,
        max_messages_number: int = 10,  # 1...10
        attributes: Sequence[str] = (),
        message_attributes: Sequence[str] = (),
        request_attempt_id: Optional[str] = None,
        visibility_timeout: int = 0,
        retry: Union[bool, int] = False,
    ) -> None:
        pass
