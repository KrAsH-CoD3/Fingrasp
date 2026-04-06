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

    def load(self, path: str | Path) -> None:
        """Parse the CSV file and populate all indexes using a robust, modular approach."""
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Device CSV not found: {path}")

        encoding = self._detect_encoding(path)
        
        # We try the detected encoding first, falling back to latin-1 if we get 0 valid results
        # (common with certain versions of the Google supported devices list)
        for attempt_encoding in [encoding, "latin-1"]:
            temp_model, temp_device, temp_brand, count, errors = self._parse_file(path, attempt_encoding)
            
            if count > 0:
                # Atomic update: only swap the internal state if we successfully loaded data
                self.by_model = temp_model
                self.by_device = temp_device
                self.by_brand = temp_brand
                self._total = count
                
                logger.info("DeviceStore loaded %d devices using encoding '%s'", count, attempt_encoding)
                if errors > 0:
                    logger.warning("DeviceStore skipped %d malformed rows during import", errors)
                return
            
            logger.warning("DeviceStore got 0 devices with %s, checking alternatives...", attempt_encoding)

        logger.error("DeviceStore failed to load any data from %s", path)
        return

    def _detect_encoding(self, path: Path) -> str:
        """Identify the file encoding by inspecting the Byte Order Mark (BOM)."""
        try:
            with path.open("rb") as f:
                bom = f.read(4)
                if bom.startswith((b"\xff\xfe", b"\xfe\xff")): return "utf-16"
                if bom.startswith(b"\xef\xbb\xbf"): return "utf-8-sig"
            return "utf-8"
        except Exception as e:
            logger.debug("BOM detection failed: %s. Defaulting to utf-8", e)
            return "utf-8"

    def _parse_file(self, path: Path, encoding: str) -> tuple[dict, dict, dict, int, int]:
        """Main parsing loop for a single encoding attempt."""
        new_model, new_device, new_brand = {}, {}, {}
        count = errors = 0

        try:
            with path.open(encoding=encoding, newline="", errors="replace") as f:
                reader = csv.reader(f)
                try:
                    next(reader) # Skip header
                except StopIteration:
                    return {}, {}, {}, 0, 0

                for raw_row in reader:
                    normalized = self._normalize_row(raw_row)
                    if not normalized:
                        continue
                    
                    if not normalized.device or not normalized.model:
                        errors += 1
                        if errors <= 5:
                            logger.debug("Malformed row sample %d: %s", errors, raw_row)
                        continue

                    # Index the record
                    brand_key = normalized.brand.lower()
                    model_key = normalized.model.lower()
                    device_key = normalized.device.lower()

                    new_model[model_key] = normalized
                    new_device[device_key] = normalized
                    new_brand.setdefault(brand_key, []).append(normalized)
                    count += 1

            return new_model, new_device, new_brand, count, errors
        except Exception as e:
            logger.error("Parsing error with %s: %s", encoding, e)
            return {}, {}, {}, 0, 0

    def _normalize_row(self, raw: list[str]) -> Optional[Device]:
        """Unpack the raw CSV row, handling the 'Double-encoded' Google format."""
        if not raw: return None
        
        brand = marketing = dev = model = ""
        
        try:
            # Case 1: Standard multi-column CSV
            if len(raw) >= 4:
                brand, marketing, dev, model = [f.strip() for f in raw[0:4]]
            # Case 2: Double-quoted single-column format (The "Google Trap")
            else:
                inner = next(csv.reader(io.StringIO(raw[0])))
                if len(inner) >= 4:
                    brand, marketing, dev, model = [f.strip() for f in inner[0:4]]
                else:
                    return None
        except Exception:
            return None

        # Post-processing: Default values for empty brand/marketing names
        return Device(
            brand=brand or "Unknown",
            marketing_name=marketing or model or "Unknown Device",
            device=dev,
            model=model
        )

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
