"""Platform for sensor integration."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from homeassistant.components.sensor import (
    RestoreSensor,
    SensorDeviceClass,
)
from homeassistant.components.sensor.const import UNIT_CONVERTERS, SensorStateClass
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType

from . import CoordinatorConfigEntry
from .base_entity import BaseEntity
from .coordinator import Coordinator
from .vimar.model.component.vimar_sensor import VimarSensor
from .vimar.utils.logger import log_info


async def async_setup_entry(
    hass: HomeAssistant,
    entry: CoordinatorConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up component based on a config entry."""
    coordinator = entry.runtime_data
    components = coordinator.data.get_sensors()
    entities = [Sensor(coordinator, component) for component in components]
    log_info(__name__, f"Sensors found: {len(entities)}")
    async_add_entities(entities, True)


class Sensor(BaseEntity, RestoreSensor):
    """Provides a Vimar Sensor.

    For sensors with `device_class=ENERGY` the integration receives raw
    instantaneous power readings from the gateway and integrates them
    over time (trapezoidal rule) into a cumulative kWh counter.
    The cumulative is persisted via `RestoreSensor` so it survives HA
    restarts and avoids the spurious counter resets that previously
    triggered HA's `total_increasing` warnings (issue #25).
    """

    _component: VimarSensor
    previous_measure: dict
    _running_total: Decimal | None

    def __init__(self, coordinator: Coordinator, component: VimarSensor) -> None:
        """Initialize the sensor."""
        self._component = component
        self.previous_measure = self._create_measure(component)
        self._running_total = None
        BaseEntity.__init__(self, coordinator, component)

    async def async_added_to_hass(self) -> None:
        """Restore the running total for ENERGY sensors across restarts."""
        await super().async_added_to_hass()
        if self.device_class != SensorDeviceClass.ENERGY:
            return
        last = await self.async_get_last_sensor_data()
        if last is None or last.native_value is None:
            return
        try:
            self._running_total = Decimal(str(last.native_value))
        except (TypeError, ValueError, ArithmeticError):
            self._running_total = None

    @property
    def device_class(self) -> SensorDeviceClass | None:
        """Return the class of this entity."""
        return self._component.device_class

    @property
    def state_class(self) -> SensorStateClass | str | None:
        """Return the state class of this entity, if any."""
        return self._component.state_class

    @property
    def options(self) -> list[str] | None:
        """Return a set of possible options."""
        return self._component.options

    @property
    def native_value(self) -> StateType | date | datetime | Decimal:
        """Return the value reported by the sensor."""
        if self.device_class == SensorDeviceClass.ENERGY:
            return self._running_total
        return self._component.native_value

    @property
    def suggested_display_precision(self) -> int | None:
        """Return the suggested number of decimal digits for display."""
        return self._component.decimal_precision

    @property
    def native_unit_of_measurement(self) -> str | None:
        """Return the unit of measurement of the sensor, if any."""
        return self._component.unit_of_measurement

    @property
    def suggested_unit_of_measurement(self) -> str | None:
        """Return the unit which should be used for the sensor's state."""
        has_converter = UNIT_CONVERTERS.get(self.device_class) is not None
        return self._component.unit_of_measurement if has_converter else None

    @callback
    def _handle_coordinator_update(self) -> None:
        super()._handle_coordinator_update()
        self._accumulate_energy()

    def _accumulate_energy(self) -> None:
        """Integrate the latest power reading into the cumulative kWh total."""
        if self.device_class != SensorDeviceClass.ENERGY:
            return
        current = self._create_measure(self._component)
        if not current:
            return
        previous = self.previous_measure
        # First valid reading: set the integration anchor
        if not previous:
            self.previous_measure = current
            return
        curr = current.get("date")
        prev = previous.get("date")
        interval = self._delta_time_in_hours(curr, prev)
        # No newer reading (same or older timestamp) -> nothing new to integrate.
        if interval is None or interval <= 0:
            # a stable signal keeps the same `last_update`
            return
        increment = self._compute_energy_increment(current, previous, interval)
        # Advance the anchor once per new reading, regardless of the increment.
        self.previous_measure = current
        if increment is None or increment <= 0:
            return
        base = self._running_total if self._running_total is not None else Decimal(0)
        self._running_total = base + increment

    def _compute_energy_increment(
        self, current: dict, previous: dict, interval: Decimal
    ) -> Decimal | None:
        """Energy delivered in the interval (trapezoidal rule): avg(P) * dt."""
        current_power = current.get("value")
        previous_power = previous.get("value")
        if current_power is None or previous_power is None:
            return None
        try:
            current_d = Decimal(str(current_power))
            previous_d = Decimal(str(previous_power))
        except (TypeError, ValueError, ArithmeticError):
            return None
        return ((current_d + previous_d) / 2) * interval

    def _delta_time_in_hours(self, t1: datetime, t2: datetime) -> Decimal | None:
        if not t1 or not t2:
            return None
        seconds_in_hour = 3600
        delta_seconds = (t1 - t2).total_seconds()
        if not delta_seconds:
            return None
        return Decimal(delta_seconds / seconds_in_hour)

    def _create_measure(self, component: VimarSensor | None = None) -> dict:
        if not component or not component.native_value:
            return {}
        return {"value": component.native_value, "date": component.last_update}
