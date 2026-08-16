"""Platform for cover integration."""

from __future__ import annotations

from functools import reduce
from typing import Any

from homeassistant.components.cover import (
    ATTR_POSITION,
    ATTR_TILT_POSITION,
    CoverEntity,
    CoverEntityFeature,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import CoordinatorConfigEntry
from .base_entity import BaseEntity
from .coordinator import Coordinator
from .vimar.model.component.vimar_cover import VimarCover
from .vimar.model.enum.action_type import ActionType
from .vimar.utils.logger import log_info


async def async_setup_entry(
    hass: HomeAssistant,
    entry: CoordinatorConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up component based on a config entry."""
    coordinator = entry.runtime_data
    components = coordinator.data.get_covers()
    entities = [Cover(coordinator, component) for component in components]
    log_info(__name__, f"Covers found: {len(entities)}")
    async_add_entities(entities, True)


class Cover(BaseEntity, CoverEntity):
    """Provides a Vimar Cover."""

    _component: VimarCover

    def __init__(self, coordinator: Coordinator, component: VimarCover) -> None:
        """Initialize the cover."""
        self._component = component
        BaseEntity.__init__(self, coordinator, component)

    @property
    def current_cover_position(self) -> int | None:
        """Return current position of cover where 0 means closed and 100 is fully open."""
        position = self._component.current_cover_position
        return 100 - position if (position is not None) else None

    @property
    def current_cover_tilt_position(self) -> int | None:
        """Return current position of cover tilt where 0 means closed and 100 is fully open."""
        position = self._component.current_tilt_position
        return 100 - position if (position is not None) else None

    # Verso del movimento in corso, finché in movimento
    _heading: str | None = None

    @property
    def is_opening(self) -> bool | None:
        """Return if the cover is opening or not. Used to determine state."""
        if self._component.is_moving is None:
            return None
        return self._travel() == "opening"

    @property
    def is_closing(self) -> bool | None:
        """Return if the cover is closing or not. Used to determine state."""
        if self._component.is_moving is None:
            return None
        return self._travel() == "closing"

    def _travel(self) -> str | None:
        """Which way this cover is going, or None if still (or unknowable)."""
        if not self._component.is_moving:
            self._heading = None
            return None
        target = self.current_cover_position
        previous = self._previous_position()
        if target is not None and previous is not None and target != previous:
            # HA scale: 100 is fully open, so a growing number means opening.
            self._heading = "opening" if target > previous else "closing"
        return self._heading

    def _previous_position(self) -> int | None:
        """The position Home Assistant is still publishing for this entity."""
        if self.hass is None or not self.entity_id:
            return None
        state = self.hass.states.get(self.entity_id)
        if state is None:
            return None
        value = state.attributes.get("current_position")
        return value if isinstance(value, int) else None

    @property
    def is_closed(self) -> bool | None:
        """Return if the cover is closed or not. Used to determine state."""
        return self._component.is_closed

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Espone `moving`: la copertura sta cambiando posizione."""
        if self._component.is_moving is None:
            return None
        return {"moving": self._component.is_moving}

    @property
    def supported_features(self) -> CoverEntityFeature:
        """Flag supported features."""
        features = [f.value for f in self._component.supported_features]
        return reduce(lambda x, y: x | y, features, CoverEntityFeature(0))

    def open_cover(self, **kwargs: Any) -> None:
        """Open the cover."""
        self.send(ActionType.OPEN)

    def close_cover(self, **kwargs: Any) -> None:
        """Close cover."""
        self.send(ActionType.CLOSE)

    def set_cover_position(self, **kwargs: Any) -> None:
        """Move the cover to a specific position."""
        position = str(100 - int(kwargs[ATTR_POSITION]))
        self.send(ActionType.SET_POSITION, position)

    def stop_cover(self, **kwargs: Any) -> None:
        """Stop the cover."""
        self.send(ActionType.STOP)

    def open_cover_tilt(self, **kwargs: Any) -> None:
        """Open the cover tilt."""
        self.send(ActionType.OPEN_SLAT)

    def close_cover_tilt(self, **kwargs: Any) -> None:
        """Close the cover tilt."""
        self.send(ActionType.CLOSE_SLAT)

    def set_cover_tilt_position(self, **kwargs: Any) -> None:
        """Move the cover tilt to a specific position."""
        position = str(100 - int(kwargs[ATTR_TILT_POSITION]))
        self.send(ActionType.SET_SLAT_POSITION, position)

    def stop_cover_tilt(self, **kwargs: Any) -> None:
        """Stop the cover."""
        self.send(ActionType.STOP_SLAT)
