from dataclasses import dataclass, field

from ...utils.mac_address import get_mac_address
from .base_request_response import BaseRequestResponse


@dataclass
class BaseRequest(BaseRequestResponse):
    args: list = field(default_factory=list)
    params: list = field(default_factory=list)

    def __init__(
        self,
        type: str = "request",
        function: str | None = None,
        source: str = get_mac_address(),
        target: str | None = None,
        token: str | None = None,
        msgid: str | None = None,
        args: list | None = None,
        params: list | None = None,
    ):
        super().__init__(
            type=type,
            function=function,
            source=source,
            target=target,
            token=token,
            msgid=msgid,
        )
        self.args = args if args is not None else []
        self.params = params if params is not None else []
