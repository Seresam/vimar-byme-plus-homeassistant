from dataclasses import dataclass, field

from ...utils.mac_address import get_mac_address
from .base_request_response import BaseRequestResponse


@dataclass
class BaseResponse(BaseRequestResponse):
    error: int = 0
    result: list = field(default_factory=list)

    def __init__(
        self,
        type: str = "response",
        function: str | None = None,
        source: str = get_mac_address(),
        target: str | None = None,
        token: str | None = None,
        msgid: str | None = None,
        error: int = 0,
        result: list | None = None,
    ):
        super().__init__(
            type=type,
            function=function,
            source=source,
            target=target,
            token=token,
            msgid=msgid,
        )
        self.error = error
        self.result = result if result is not None else []
