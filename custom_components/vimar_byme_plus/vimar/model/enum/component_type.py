from enum import Enum


class ComponentType(Enum):
    LIGHT = {"sftype": "SF_Light"}  # noqa: RUF012
    ENERGY = {"sftype": "SF_Energy"}  # noqa: RUF012
    CLIMA = {"sftype": "SF_Clima"}  # noqa: RUF012
    COVER = {"sftype": "SF_Shutter"}  # noqa: RUF012
    DOOR = {"sftype": "SF_Access"}  # noqa: RUF012
    AUDIO = {"sftype": "SF_Audio"}  # noqa: RUF012

    @staticmethod
    def from_type(value: str):
        for component_type in ComponentType:
            if component_type.value.get("sftype") == value:
                return component_type
        return None

    def id(self) -> str:
        """Return id of the entity."""
        return self.value.get("sftype")

    def device_class(self) -> str:
        """Return id of the entity."""
        return self.value.get("device_class")
