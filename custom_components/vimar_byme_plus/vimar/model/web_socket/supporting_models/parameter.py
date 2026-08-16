from dataclasses import dataclass, field


@dataclass
class Parameter:
    idambient: list = field(default_factory=list)

    def __init__(self, ambient_ids: list[int] | None = None):
        self.idambient = ambient_ids if ambient_ids is not None else []
