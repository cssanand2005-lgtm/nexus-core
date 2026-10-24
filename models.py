from dataclasses import dataclass
from enum import Enum

class DeviceStatus(Enum):
    ACTIVE = "ACTIVE"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"

@dataclass
class TelemetryData:
    device_id: str
    temperature: float
    status: DeviceStatus

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            device_id=data.get("device_id"),
            temperature=float(data.get("temperature", 0.0)),
            status=DeviceStatus(data.get("status", "ACTIVE"))
        )