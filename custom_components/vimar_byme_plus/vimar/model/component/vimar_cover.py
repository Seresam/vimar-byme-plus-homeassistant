from dataclasses import dataclass
from enum import Enum

from .vimar_component import VimarComponent


class CoverEntityFeature(Enum):
    OPEN = 1
    CLOSE = 2
    SET_POSITION = 4
    STOP = 8
    OPEN_TILT = 16
    CLOSE_TILT = 32
    STOP_TILT = 64
    SET_TILT_POSITION = 128


@dataclass
class VimarCover(VimarComponent):
    current_cover_position: int | None
    current_tilt_position: int | None
    is_closed: bool | None
    supported_features: list[CoverEntityFeature]
    is_moving: bool | None = None

    @staticmethod
    def get_table_header() -> list:
        return [
            "Area",
            "Name",
            "Type",
            "Position",
            "isClosed",
            "isMoving",
        ]

    def to_table(self) -> list:
        return [
            self.area,
            self.name,
            self.device_name,
            self.current_cover_position,
            self.is_closed,
            self.is_moving,
        ]
