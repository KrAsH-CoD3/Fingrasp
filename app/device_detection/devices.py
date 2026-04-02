"""
devices.py — Android device data loader with multi-index support.

The source CSV uses a double-encoded format: each line is a quoted string
that itself contains comma-separated, inner-quoted fields. This module
handles that transparently and builds three O(1) lookup indexes.
"""

from dataclasses import dataclass
from typing import Optional
from pathlib import Path
import logging
import csv
import io

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class Device:
    brand: str  # The Brand name - e.g., "Redmi"
    marketing_name: str  # Known as - e.g., "Redmi K50 Pro"
    device: str  # Codename - e.g., "matisse"
    model: str  # User-facing model string - e.g., "22011211C"


class DeviceStore:
    """
    In-memory store loaded once at startup.

    Indexes
    -------
    by_model : model.lower() → Device
    by_device : device.lower() → Device
    by_brand : brand.lower() → list[Device]

    Notes
    -----
    - All three indexes share the same Device objects (no duplication).
    - Models/devices that appear more than once keep the last occurrence;
    brand lists accumulate every entry.
    """

    def __init__(self) -> None:
        self.by_model: dict[str, Device] = {}
        self.by_device: dict[str, Device] = {}
        self.by_brand: dict[str, list[Device]] = {}
        self._total: int = 0

    def load(self, path: str | Path) -> int:
        """Parse the CSV file and populate all indexes.

        Malformed rows are logged and skipped.
        """
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Device CSV not found: {path}")

        by_model: dict[str, Device] = {}
        by_device: dict[str, Device] = {}
        by_brand: dict[str, list[Device]] = {}
        count = 0
        errors = 0

        with path.open(encoding="latin-1") as f:
            reader = csv.reader(f)
            next(reader)  # skip header row

            for raw in reader:
                if not raw or len(raw) < 1:
                    continue
                # Each row is a single outer field; parse it as its own CSV
                try:
                    brand, marketing_name, device, model = next(
                        csv.reader(io.StringIO(raw[0]))
                    )
                except (StopIteration, ValueError):
                    errors += 1
                    continue  # malformed row — skip

                # Validate that all fields are non-empty
                if not brand or not marketing_name or not device or not model:
                    errors += 1
                    continue

                entry = Device(
                    brand=brand.strip(),
                    marketing_name=marketing_name.strip(),
                    device=device.strip(),
                    model=model.strip(),
                )

                model_key = entry.model.lower()
                device_key = entry.device.lower()
                brand_key = entry.brand.lower()

                by_model[model_key] = entry
                by_device[device_key] = entry
                by_brand.setdefault(brand_key, []).append(entry)
                count += 1

        self.by_model = by_model
        self.by_device = by_device
        self.by_brand = by_brand
        self._total = count

        if errors > 0:
            logger.warning(
                "DeviceStore skipped %d malformed rows from %s", errors, path
            )
        logger.info("DeviceStore loaded %d devices from %s", count, path)
        return errors

    # ------------------------------------------------------------------
    # Lookups
    # ------------------------------------------------------------------

    def get_by_model(self, model: str) -> Optional[Device]:
        """Exact lookup by model string (case-insensitive)."""
        return self.by_model.get(model.strip().lower())

    def get_by_device(self, device: str) -> Optional[Device]:
        """Exact lookup by device codename (case-insensitive)."""
        return self.by_device.get(device.strip().lower())

    def get_by_brand(self, brand: str) -> list[Device]:
        """Return all devices for a brand (case-insensitive)."""
        return self.by_brand.get(brand.strip().lower(), [])

    def fuzzy_search(self, query: str, limit: int = 10) -> list[Device]:
        """
        Fuzzy search across model strings using rapidfuzz.
        Falls back to an empty list if rapidfuzz is not installed.
        """
        try:
            from rapidfuzz import process, fuzz
        except ImportError:
            logger.warning("rapidfuzz not installed; fuzzy search unavailable.")
            return []
        except Exception:
            logger.warning("rapidfuzz import failed; fuzzy search unavailable.")
            return []

        query_lower = query.strip().lower()
        matches = process.extract(
            query_lower,
            self.by_model.keys(),
            scorer=fuzz.WRatio,
            limit=limit,
            score_cutoff=70,
        )
        return [self.by_model[match[0]] for match in matches]

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @property
    def total(self) -> int:
        return self._total

    @property
    def brands(self) -> list[str]:
        """Sorted list of all unique brand names."""
        return sorted(self.by_brand.keys())

    def stats(self) -> dict:
        return {
            "total_devices": self._total,
            "unique_models": len(self.by_model),
            "unique_devices": len(self.by_device),
            "unique_brands": len(self.by_brand),
        }

    def to_dict(self, device: Device) -> dict:
        return {
            "brand": device.brand,
            "marketing_name": device.marketing_name,
            "device": device.device,
            "model": device.model,
        }


# Module-level singleton
store = DeviceStore()
