from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class PingResponse:
    message: str


@dataclass
class RobotPayload:
    robot_id: str
    name: str
    metadata: Dict[str, Any]
