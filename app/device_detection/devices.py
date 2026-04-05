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

        Handles multiple encodings (UTF-16, UTF-8, Latin-1) and both
        standard and double-encoded CSV formats.
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

        # ── Detect Encoding ──
        # Official Google CSV is typically UTF-16LE with BOM.
        encoding = "utf-8"
        try:
            with path.open("rb") as f:
                header_bytes = f.read(4)
                if header_bytes.startswith((b"\xff\xfe", b"\xfe\xff")):
                    encoding = "utf-16"
                elif header_bytes.startswith(b"\xef\xbb\xbf"):
                    encoding = "utf-8-sig"
                else:
                    # Default to latin-1 if it's not clearly UTF-8/16
                    # to avoid DecodeErrors on legacy files
                    encoding = "utf-8"
        except Exception as e:
            logger.warning("Encoding detection failed for %s: %s", path, e)

        # ── Parse ──
        try:
            # We use newline='' as recommended by csv module docs
            with path.open(encoding=encoding, newline="", errors="replace") as f:
                # Some versions of the Google CSV use tabs, though the filename says CSV.
                # We'll stick to comma but be robust if it fails.
                reader = csv.reader(f)
                try:
                    next(reader) # Skip header
                except StopIteration:
                    return 0

                for raw in reader:
                    # Silently skip truly empty rows or short lines (e.g. trailing commas)
                    if not raw or len(raw) < 2 or (len(raw) == 1 and not raw[0].strip()):
                        continue

                    brand = marketing_name = device_name = model = ""
                    
                    try:
                        if len(raw) >= 4:
                            brand, marketing_name, device_name, model = [f.strip() for f in raw[0:4]]
                        else:
                            # Legacy check: "Double-encoded" format
                            inner_raw = next(csv.reader(io.StringIO(raw[0])))
                            if len(inner_raw) >= 4:
                                brand, marketing_name, device_name, model = [f.strip() for f in inner_raw[0:4]]
                            else:
                                continue # Too short, skip silently
                    except (StopIteration, ValueError, IndexError):
                        continue # Skip malformed row fragments silently

                    # Validate that critical fields are non-empty.
                    # We only log an error if we have enough columns but the data is garbage.
                    if not brand or not device_name or not model:
                        # If the entire row is empty strings, skip silently
                        if not any([brand, marketing_name, device_name, model]):
                            continue
                        errors += 1
                        continue
                    
                    if not marketing_name:
                        marketing_name = model

                    entry = Device(
                        brand=brand,
                        marketing_name=marketing_name,
                        device=device_name,
                        model=model,
                    )

                    model_key = entry.model.lower()
                    device_key = entry.device.lower()
                    brand_key = entry.brand.lower()

                    # We keep the last occurrence if multiple models/devices share the same key
                    by_model[model_key] = entry
                    by_device[device_key] = entry
                    by_brand.setdefault(brand_key, []).append(entry)
                    count += 1

        except Exception as e:
            logger.error("Critical error loading device store from %s: %s", path, e)
            return -1

        self.by_model = by_model
        self.by_device = by_device
        self.by_brand = by_brand
        self._total = count

        if errors > 0:
            logger.warning("DeviceStore skipped %d malformed rows from %s (%s)", errors, path, encoding)
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
