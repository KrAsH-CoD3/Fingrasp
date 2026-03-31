"""Device detection package.

Initializes the CSV-backed DeviceStore at import time and re-exports
the public API for device name extraction.
"""

# TODO: Consider moving CSV loading to lazy loading on first access instead of import time

from pathlib import Path
import logging

from app.device_detection.detection import extract_device_name
from app.device_detection.devices import store

logger = logging.getLogger(__name__)

# Load the Android supported devices CSV at import time.
# The store is a module-level singleton shared across detection functions.
_CSV_PATH = (
    Path(__file__).resolve().parent.parent.parent
    / "static" / "assets" / "android_supported_devices.csv"
)

if _CSV_PATH.exists():
    errors = store.load(_CSV_PATH)
    if errors:
        logger.warning(
            "Android device CSV loaded with %d malformed rows skipped", errors
        )
else:
    logger.warning(
        "Android device CSV not found at %s — CSV lookups disabled", _CSV_PATH
    )


__all__ = ["extract_device_name", "store"]
