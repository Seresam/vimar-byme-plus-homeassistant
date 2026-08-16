from datetime import datetime, timedelta

from ...model.component.vimar_button import VimarButton
from ...model.enum.sfetype_enum import SfeType
from ...model.enum.sstype_enum import SsType
from ...model.repository.user_component import UserComponent


class SsSceneExecutorMapper:
    SSTYPE = SsType.SCENE_EXECUTOR.value

    def from_obj(self, component: UserComponent, *args) -> list[VimarButton]:
        return [
            self._button_from_obj(component, *args),
            # self._sensor_from_obj(component, *args),
        ]

    def _button_from_obj(self, component: UserComponent, *args) -> VimarButton:
        return VimarButton(
            id=component.idsf,
            name=component.name,
            device_group=component.sftype,
            device_name=component.sstype,
            device_class=None,
            area=component.ambient.name,
            main_id=None,
            executed=self._executed(component),
        )

    def _executed(self, component: UserComponent) -> bool:
        value = component.get_value(SfeType.STATE_EXECUTED)

        if value != "Executed":
            return False

        last_update = self._last_update(component)

        # Una scena presente nella sfdiscovery ha last_update=None
        # e non deve essere interpretata come appena eseguita.
        if last_update is None:
            return False

        age = datetime.now() - last_update  # noqa: DTZ005

        return timedelta(0) <= age <= timedelta(seconds=2)

    def _last_update(self, component: UserComponent) -> datetime | None:
        value = component.get_last_update(SfeType.STATE_EXECUTED)

        if not value:
            return None

        try:
            return datetime.fromisoformat(value)
        except (TypeError, ValueError):
            return None
