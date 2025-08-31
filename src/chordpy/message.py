import json
from typing import Any


class message:
    def __init__(self, type, **params) -> None:
        self._type = type
        self._params = params

    def _to_dict(self) -> dict[str, Any]:
        return {"type": self._type, "parameters": self._params}

    def to_json(self) -> str:
        return json.dumps(self._to_dict())

    def __repr__(self) -> str:
        return f"message:\n{(f'{key}: {value}\n' for key, value in self._to_dict().items())}"
