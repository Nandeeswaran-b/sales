from dataclasses import dataclass, field
from typing import Optional
from enum import Enum
import json

class ShelfStatus(Enum):
    NORMAL = "NORMAL"
    MISALIGNED = "MISALIGNED"
    MISSING = "MISSING"
    LOW_STOCK = "LOW_STOCK"

@dataclass
class Item:
    id: str
    name: str
    expected_count: int
    detected_count: int
    expected_position_x: float  # Normalized 0.0 to 1.0 (left to right)
    expected_position_y: float  # Normalized 0.0 to 1.0 (bottom to top)
    detected_position_x: float
    detected_position_y: float

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "expected_count": self.expected_count,
            "detected_count": self.detected_count,
            "expected_position_x": self.expected_position_x,
            "expected_position_y": self.expected_position_y,
            "detected_position_x": self.detected_position_x,
            "detected_position_y": self.detected_position_y
        }

@dataclass
class Shelf:
    id: str
    row: int
    col: int
    item: Optional[Item]
    status: ShelfStatus = ShelfStatus.NORMAL
    last_scanned: str = "" # ISO Timestamp
    
    def to_dict(self):
        return {
            "id": self.id,
            "row": self.row,
            "col": self.col,
            "item": self.item.to_dict() if self.item else None,
            "status": self.status.value,
            "last_scanned": self.last_scanned
        }
