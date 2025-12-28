# REGION MANAGER - Alan yönetimi (ScreenSelector ile çok benziyor kontrol etmek gerek)

import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, Optional


# =================================================
# DATA STRUCTURE
# =================================================

@dataclass
class Region:
    name: str
    x: int
    y: int
    width: int
    height: int

    def as_tuple(self):
        return (self.x, self.y, self.width, self.height)


# =================================================
# REGION MANAGER
# =================================================

class RegionManager:
    """
    Manages screen regions used for capture and analysis.
    Deterministic, session-safe.
    """

    def __init__(self):
        self._regions: Dict[str, Region] = {}

    # -------------------------------------------------
    # CRUD OPERATIONS
    # -------------------------------------------------

    def add_region(
        self,
        name: str,
        x: int,
        y: int,
        width: int,
        height: int
    ) -> None:
        self._regions[name] = Region(
            name=name,
            x=x,
            y=y,
            width=width,
            height=height
        )

    def remove_region(self, name: str) -> None:
        if name in self._regions:
            del self._regions[name]

    def get_region(self, name: str) -> Optional[Region]:
        return self._regions.get(name)

    def list_regions(self) -> Dict[str, Region]:
        return dict(self._regions)

    def clear(self) -> None:
        self._regions.clear()

    # -------------------------------------------------
    # VALIDATION
    # -------------------------------------------------

    def validate_region(self, name: str) -> bool:
        region = self._regions.get(name)
        if not region:
            return False

        if region.width <= 0 or region.height <= 0:
            return False

        if region.x < 0 or region.y < 0:
            return False

        return True

    # -------------------------------------------------
    # PERSISTENCE
    # -------------------------------------------------

    def save(self, path: str | Path) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, "w", encoding="utf-8") as f:
            json.dump(
                {name: asdict(region) for name, region in self._regions.items()},
                f,
                indent=2
            )

    def load(self, path: str | Path) -> None:
        path = Path(path)
        if not path.exists():
            return

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        self._regions.clear()
        for name, region_data in data.items():
            self._regions[name] = Region(**region_data)
