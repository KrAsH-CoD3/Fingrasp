"""Device detection logic for extracting human-readable device names from fingerprint data.

Uses a multi-signal approach combining screen resolution, device pixel ratio,
user agent parsing, WebGL GPU info, and platform strings to identify devices.
The MixVisit fingerprint wraps each module in {value, duration} — this module
handles that transparently.

Android model identification is powered by the CSV-backed DeviceStore
(~35K+ devices from Google's official supported devices list), with
manufacturer prefix matching as a brand-level fallback.
"""

from __future__ import annotations

from typing import Any
import logging
import re

from app.device_detection.databases import (
    APPLE_SILICON_PATTERNS,
    DESKTOP_GPU_PATTERNS,
    IPAD_SCREEN_DB,
    IPHONE_SCREEN_DB,
)
from app.security import validate_input

logger = logging.getLogger(__name__)

# ── Helper to unwrap MixVisit {value, duration} wrapper ──
def _unwrap(module: Any) -> Any:
    """
    MixVisit fingerprint modules wrap data as {"value": ..., "duration": ...}.
    Returns the inner value if wrapped, or the raw value otherwise.
    """
    if isinstance(module, dict) and "value" in module:
        return module["value"]
    return module


# ═══════════════════════════════════════════════════════════════════════════════
# Safe Value Extraction Helpers
# ═══════════════════════════════════════════════════════════════════════════════


def _get_nav_value(fingerprint: dict[str, Any], key: str) -> Any:
    """Safely get a value from fingerprint.navigator.value.<key>."""
    nav = fingerprint.get("navigator")
    nav_val = _unwrap(nav) if nav else None
    if isinstance(nav_val, dict):
        return nav_val.get(key)
    return None


def _get_screen_dims(fingerprint: dict[str, Any]) -> tuple[int, int] | None:
    """
    Extract screen resolution as (width, height) in portrait orientation.
    Tries screenResolution first, then falls back to screen module.
    """
    # Try screenResolution module [height, width] as per MixVisit convention
    screen_res = _unwrap(fingerprint.get("screenResolution"))
    if isinstance(screen_res, list) and len(screen_res) >= 2:
        try:
            screen_height = int(float(screen_res[0]))
            screen_width = int(float(screen_res[1]))
            logger.debug(
                f"Screen dims from screenResolution: {screen_width}x{screen_height}"
            )
            return (min(screen_width, screen_height), max(screen_width, screen_height))
        except (ValueError, TypeError) as e:
            logger.debug(f"Failed to parse screenResolution {screen_res}: {e}")

    # Try the screen module
    screen = _unwrap(fingerprint.get("screen"))
    if isinstance(screen, dict):
        try:
            screen_width = int(float(screen.get("width", 0)))
            screen_height = int(float(screen.get("height", 0)))
            if screen_width > 0 and screen_height > 0:
                logger.debug(
                    f"Screen dims from screen module: {screen_width}x{screen_height}"
                )
                return (
                    min(screen_width, screen_height),
                    max(screen_width, screen_height),
                )
            else:
                logger.debug(f"Screen module has invalid dims: {screen}")
        except (ValueError, TypeError) as e:
            logger.debug(f"Failed to parse screen module {screen}: {e}")

    logger.debug("Screen dims extraction failed: no valid source found")
    return None


def _get_dpr(fingerprint: dict[str, Any]) -> int | None:
    """Extract device pixel ratio."""
    dpr = _unwrap(fingerprint.get("devicePixelRatio"))
    if dpr is not None:
        try:
            dpr_value = int(float(dpr))
            logger.debug(f"DPR: {dpr_value}")
            return dpr_value
        except (ValueError, TypeError):
            logger.debug(f"Failed to parse DPR: {dpr}")
    return None


def _get_gpu_renderer(fingerprint: dict[str, Any]) -> str | None:
    """Extract the WebGL unmasked renderer string."""
    webgl = _unwrap(fingerprint.get("webgl"))
    if not isinstance(webgl, dict):
        return None

    # Check supportedWebGLContexts array (MixVisit format)
    contexts = webgl.get("supportedWebGLContexts")
    if isinstance(contexts, list):
        for ctx in contexts:
            if isinstance(ctx, dict):
                basics = ctx.get("basics")
                if isinstance(basics, dict):
                    renderer = basics.get("unmaskedRenderer")
                    if isinstance(renderer, str) and renderer.strip():
                        return renderer.strip()

    # Fallback: flat structure
    basics = webgl.get("basics")
    if isinstance(basics, dict):
        renderer = basics.get("unmaskedRenderer")
        if isinstance(renderer, str) and renderer.strip():
            return renderer.strip()

    return None


# ═══════════════════════════════════════════════════════════════════════════════
# Model Normalization & Core Detection Functions
# ═══════════════════════════════════════════════════════════════════════════════


def _normalize_model(raw_model: str) -> str:
    """
    Normalize a device model string from UA Client Hints for reliable matching.

    Handles real-world quirks:
      - "SM-G955U"      → "SM-G955U"  (kept as-is, startswith handles it)
      - "SM-G955U1"     → "SM-G955U1"
      - "SM-G955B/DS"   → "SM-G955B"  (strip dual-SIM marker)
      - "samsung SM-G955U" → "SM-G955U" (extract SM- code from noise)
      - "SAMSUNG-SM-G955U" → "SM-G955U"
      - " SM-G955U "    → "SM-G955U"  (trim whitespace)
    """
    model = raw_model.strip()
    if not model:
        return model

    # Strip /DS (dual-SIM) and /DD markers
    model = re.sub(r"/DS$|/DD$", "", model, flags=re.IGNORECASE)

    # If the string contains an SM- code buried in noise, extract it.
    # e.g. "samsung SM-G955U" or "SAMSUNG-SM-G955U" → "SM-G955U"
    sm_match = re.search(r"(SM-[A-Za-z0-9]+)", model)
    if sm_match:
        model = sm_match.group(1)

    return model.strip()


def _detect_iphone_by_screen(screen_dims: tuple[int, int], dpr: int) -> str | None:
    """Match an iPhone model by screen resolution and pixel ratio."""
    for (iphone_width, iphone_height), ratio, name in IPHONE_SCREEN_DB:
        if screen_dims == (iphone_width, iphone_height) and dpr == ratio:
            logger.info(
                f"iPhone detected by screen resolution {screen_dims} and DPR {dpr}: {name}"
            )
            return name
    return None


def _detect_ipad_by_screen(screen_dims: tuple[int, int], dpr: int) -> str | None:
    """Match an iPad model by screen resolution and pixel ratio."""
    for (ipad_width, ipad_height), ratio, name in IPAD_SCREEN_DB:
        if screen_dims == (ipad_width, ipad_height) and dpr == ratio:
            logger.info(
                f"iPad detected by screen resolution {screen_dims} and DPR {dpr}: {name}"
            )
            return name
    return None


def _lookup_device_store(model: str) -> str | None:
    """
    Look up a device model in the CSV-backed DeviceStore.

    Returns the marketing name from the official Google-published
    Android supported devices CSV (~35K+ devices).
    """
    from app.device_detection.devices import store

    if not store.total:
        return None

    device = store.get_by_model(model)
    if device and device.marketing_name:
        # Use marketing name; prepend brand if it's not already in it
        name = device.marketing_name
        if not name.lower().startswith(device.brand.lower()):
            name = f"{device.brand} {name}"
        logger.info(f"Device '{model}' matched in CSV Device Store: {name}")
        return name
    return None


def _identify_model(model: str) -> str | None:
    """
    Unified model identification using the CSV store.
    Returns the best human-readable name or None.
    """
    if not model or not model.strip():
        return None

    normalized = _normalize_model(model)

    # Perform lookup in the official CSV device store
    return _lookup_device_store(normalized)


def _detect_from_gpu(gpu_renderer: str) -> str | None:
    """Detect device or platform type from GPU renderer string."""
    if not gpu_renderer:
        return None

    # Apple Silicon Mac detection
    for pattern, device_name in APPLE_SILICON_PATTERNS:
        if gpu_renderer.startswith(pattern):
            logger.info(
                f"Mac identified via Apple Silicon GPU pattern '{pattern}': {device_name}"
            )
            return device_name

    # Generic Apple GPU = Apple mobile device (not a Mac)
    if gpu_renderer == "Apple GPU":
        return None

    # Desktop & mobile GPU pattern matching
    for pattern, device_name in DESKTOP_GPU_PATTERNS:
        if re.search(pattern, gpu_renderer, re.IGNORECASE):
            logger.info(f"Device identified via GPU pattern '{pattern}': {device_name}")
            return device_name

    return None


def _parse_android_model_from_ua(user_agent: str) -> str | None:
    """
    Extract the device model from an Android user agent string.

    Android UAs typically look like:
        Mozilla/5.0 (Linux; Android 14; SM-S928B) AppleWebKit/...
        Mozilla/5.0 (Linux; Android 13; Pixel 7 Pro) AppleWebKit/...
        Mozilla/5.0 (Linux; Android 14; SM-S928B Build/UP1A.231005.007) ...
    """
    match = re.search(r"Android\s[\d.]+;\s*([^);]+?)(?:\s*Build/|\s*\))", user_agent)
    if match:
        model = match.group(1).strip()
        if model and model.lower() not in ("linux", "wv", "k"):
            return model
    return None


# ═══════════════════════════════════════════════════════════════════════════════
# Main Entry Point
# ═══════════════════════════════════════════════════════════════════════════════


def extract_device_name(fingerprint: dict[str, Any]) -> str:
    """
    Extract a human-readable device name from MixVisit fingerprint data.

    The detection uses a priority-based signal hierarchy to counter spoofing:
        1. highEntropyValues (UA-CH) - Most reliable, checks OS + Model hints.
        2. userAgentData (UA-CH) - Modern API, harder to spoof than legacy fields.
        3. navigator.platform - Cross-validated against Client Hints (if available).
           Handles iPadOS "MacIntel" ambiguity via touch support and heuristics.
        4. User-Agent string - Traditional regex-based parsing (fallback).
        5. Heuristics - Screen-size based disambiguation for ambiguous iOS signals.

    Once the OS is identified, the name is refined via:
        - Apple: Screen resolution + Device Pixel Ratio (DPR) matching.
        - Android: CSV-backed DeviceStore (~35K+ models) and manufacturer prefixes.
        - Desktop: WebGL GPU renderer pattern matching (Apple Silicon, NVIDIA, etc.).

    Args:
        fingerprint: The MixVisit fingerprint dictionary. Handles {value, duration}
            wrappers transparently for all modules.

    Returns:
        A human-readable device name or "Unknown Device".
        Examples:
        - "iPhone 16 Pro Max / 17 Pro Max"
        - "Samsung Galaxy S24 Ultra"
        - "MacBook Pro (Apple M4 Pro)"
        - "Windows PC (NVIDIA RTX 40-series)"
    """
    if not isinstance(fingerprint, dict):
        return "Unknown Device"

    # ── Extract navigator signals once ──
    nav = _unwrap(fingerprint.get("navigator")) or {}
    user_agent = nav.get("userAgent") or ""
    platform = nav.get("platform") or ""
    touch_points = nav.get("maxTouchPoints") or 0

    # ── Extract Client Hint Signals (Robustly) ──
    # Different collectors put userAgentData/highEntropyValues in different places.
    # We check: 1. Top-level of fingerprint, 2. Nested inside navigator.
    def _extract_model(source):
        val = source.get("model") if isinstance(source, dict) else None
        return val.strip() if isinstance(val, str) else None

    # Check for userAgentData (UA-CH)
    user_agent_data = (
        _unwrap(fingerprint.get("userAgentData")) or nav.get("userAgentData") or {}
    )

    # Check for high-entropy values (often the result of getHighEntropyValues())
    high_entropy_values = (
        _unwrap(fingerprint.get("highEntropyValues"))
        or nav.get("highEntropyValues")
        or {}
    )

    logger.info(
        f"Signal extraction — UA: {user_agent[:20]}..., Platform: {platform}, user_agent_data: {user_agent_data}, high_entropy_values: {high_entropy_values}"
    )

    # ═══════════════════════════════════════════════════════════════════════════════
    # OS Detection - Priority-based with Cross-Validation
    # ═══════════════════════════════════════════════════════════════════════════════
    # 1. highEntropyValues (UACH) - Most reliable, requires explicit permission/collection
    # 2. userAgentData (UA-CH) - Modern standardized API, harder to spoof than legacy fields
    # 3. navigator.platform - Standard legacy field, verified against UACH if available
    # 4. User-Agent string - Fallback for older browsers
    #
    # Signal nuances:
    # - Client Hints (UACH) returns "iOS" as the platform name.
    # - Modern iPads on iPadOS 13+ return "MacIntel" for navigator.platform.
    # - We use High Entropy "model" hints to distinguish iPhone from iPad early.

    model_hint = _extract_model(high_entropy_values) or _extract_model(user_agent_data)
    is_mobile_hint = user_agent_data.get("mobile") is True
    os_type = None
    detection_source = None
    ios_detected = False

    # ── Priority 1: highEntropyValues ──
    hev_platform = high_entropy_values.get("platform")
    if hev_platform:
        hev_platform_lower = hev_platform.lower()
        if hev_platform_lower == "android":
            os_type = "android"
            detection_source = "highEntropyValues.platform"
        elif hev_platform_lower == "windows":
            os_type = "windows"
            detection_source = "highEntropyValues.platform"
        elif hev_platform_lower in ("macos", "mac os x"):
            os_type = "mac"
            detection_source = "highEntropyValues.platform"
        elif hev_platform_lower == "ios":
            ios_detected = True
            # Check if we have model hint from highEntropyValues
            if model_hint:
                model_lower = model_hint.lower()
                if model_lower.startswith("ipad"):
                    os_type = "ipad"
                    detection_source = f"highEntropyValues (iOS + model={model_hint})"
                elif model_lower.startswith("iphone"):
                    os_type = "iphone"
                    detection_source = f"highEntropyValues (iOS + model={model_hint})"
                # Fall through if model doesn't clearly indicate device type

    # ── Priority 2: userAgentData.platform ──
    if not os_type:
        user_agent_data_platform = user_agent_data.get("platform")

        if user_agent_data_platform:
            user_agent_data_platform_lower = user_agent_data_platform.lower()
            if user_agent_data_platform_lower == "android":
                os_type = "android"
                detection_source = (
                    f"userAgentData (platform=Android, mobile={is_mobile_hint})"
                )
            elif user_agent_data_platform_lower == "windows":
                os_type = "windows"
                detection_source = "userAgentData.platform"
            elif user_agent_data_platform_lower == "macos":
                os_type = "mac"
                detection_source = "userAgentData.platform"
            elif user_agent_data_platform_lower == "ios":
                ios_detected = True
                # Check model hint from userAgentData
                user_agent_data_model = user_agent_data.get("model", "")
                if user_agent_data_model:
                    user_agent_data_model_lower = user_agent_data_model.lower()
                    if user_agent_data_model_lower.startswith("ipad"):
                        os_type = "ipad"
                        detection_source = (
                            f"userAgentData (iOS + model={user_agent_data_model})"
                        )
                    elif user_agent_data_model_lower.startswith("iphone"):
                        os_type = "iphone"
                        detection_source = (
                            f"userAgentData (iOS + model={user_agent_data_model})"
                        )

    # ── Priority 3: navigator.platform with cross-validation ──
    if not os_type:
        if platform:
            plat_lower = platform.lower()
            # Cross-validate: If we detected iOS from Client Hints, verify platform matches
            if ios_detected:
                # We already know OS is iOS from trusted source
                # navigator.platform should say "iPhone" or "iPad"
                if plat_lower == "iphone":
                    os_type = "iphone"
                    detection_source = "navigator.platform (validated by Client Hints)"
                elif plat_lower == "ipad":
                    os_type = "ipad"
                    detection_source = "navigator.platform (validated by Client Hints)"
                elif plat_lower == "macintel" and touch_points > 0:
                    # iPadOS 13+ reports MacIntel, but we know it's iOS from Client Hints
                    os_type = "ipad"
                    detection_source = (
                        "navigator.platform (MacIntel+touch, validated by Client Hints)"
                    )
                else:
                    # Conflict: Client Hints says iOS but navigator.platform disagrees
                    # Trust Client Hints, use heuristics
                    logger.warning(
                        f"Signal conflict: Client Hints says iOS but navigator.platform={platform}. "
                        f"Trusting Client Hints."
                    )
                    # Fall through to Priority 5 (iOS fallback)
            else:
                # No Client Hints, use navigator.platform directly (less reliable)
                if plat_lower == "iphone":
                    os_type = "iphone"
                    detection_source = "navigator.platform"
                elif plat_lower == "ipad":
                    os_type = "ipad"
                    detection_source = "navigator.platform"
                elif plat_lower == "android":
                    os_type = "android"
                    detection_source = "navigator.platform"
                elif plat_lower.startswith("mac"):
                    if plat_lower == "macintel" and touch_points > 0:
                        os_type = "ipad"
                        detection_source = "navigator.platform (MacIntel + touch)"
                    else:
                        os_type = "mac"
                        detection_source = "navigator.platform"
                elif plat_lower.startswith("win"):
                    os_type = "windows"
                    detection_source = "navigator.platform"
                elif plat_lower in ("linux", "x11"):
                    os_type = "linux"
                    detection_source = "navigator.platform"

    # ── Priority 4a: Generic Mobile Signal Fallback ──
    if not os_type and is_mobile_hint:
        # We know it's mobile, but don't have a definitive OS name yet.
        # This occurs on some newer privacy-focused mobile browsers.
        if "Android" in user_agent:
            os_type = "android"
            detection_source = "userAgent + mobile=true hint"
        else:
            # If no Android keyword, default to iPhone for mobile-only environments
            os_type = "iphone"
            detection_source = "mobile=true hint fallback"

    # ── Priority 4b: User-Agent string parsing ──
    if not os_type:
        if "iPad" in user_agent:
            os_type = "ipad"
            detection_source = "userAgent"
        elif "iPhone" in user_agent:
            os_type = "iphone"
            detection_source = "userAgent"
        elif "Android" in user_agent:
            os_type = "android"
            detection_source = "userAgent"
        elif "Windows" in user_agent:
            os_type = "windows"
            detection_source = "userAgent"
        elif "Macintosh" in user_agent:
            os_type = "mac"
            detection_source = "userAgent"
        elif "Linux" in user_agent:
            os_type = "linux"
            detection_source = "userAgent"

    # ── Priority 5: iOS fallback with screen size heuristic ──
    if not os_type and ios_detected:
        screen_dims_temp = _get_screen_dims(fingerprint)
        if screen_dims_temp:
            # Heuristic: larger screen = likely iPad
            if screen_dims_temp[0] > 500 or screen_dims_temp[1] > 800:
                os_type = "ipad"
                detection_source = "iOS + screen size heuristic"
            else:
                os_type = "iphone"
                detection_source = "iOS + screen size heuristic"
        else:
            # Default to iPhone (more common)
            os_type = "iphone"
            detection_source = "iOS (default)"

    if os_type:
        logger.info(f"OS detected as '{os_type}' via {detection_source}")
    else:
        logger.warning(
            f"Could not detect OS from signals: platform={platform}, ua={user_agent[:50]}..."
        )

    # ── Detection Waterfall ──
    screen_dims = _get_screen_dims(fingerprint)
    dpr = _get_dpr(fingerprint)
    logger.debug(f"Extracted screen_dims: {screen_dims}, dpr: {dpr}")
    gpu_renderer = _get_gpu_renderer(fingerprint)

    logger.debug(f"Screen dims: {screen_dims}, DPR: {dpr}, GPU: {gpu_renderer}")

    if os_type == "iphone":
        if screen_dims and dpr:
            iphone_name = _detect_iphone_by_screen(screen_dims, dpr)
            if iphone_name:
                return iphone_name
        # Fallback: if GPU renderer is "Apple GPU", we know it's an iPhone/iPad
        if gpu_renderer == "Apple GPU":
            logger.debug("iPhone detected via Apple GPU fallback")
        return "iPhone"

    elif os_type == "ipad":
        if screen_dims and dpr:
            ipad_name = _detect_ipad_by_screen(screen_dims, dpr)
            if ipad_name:
                return ipad_name
        # Fallback: if GPU renderer is "Apple GPU", we know it's an iPhone/iPad
        if gpu_renderer == "Apple GPU":
            logger.debug("iPad detected via Apple GPU fallback")
        return "iPad"

    elif os_type == "android" or model_hint:
        # High-entropy models are 100% reliable
        if model_hint:
            identified = _identify_model(model_hint)
            if identified:
                return identified
            return model_hint

        # UA string parsing fallback
        ua_model = _parse_android_model_from_ua(user_agent)
        if ua_model:
            identified = _identify_model(ua_model)
            if identified:
                return identified
            return f"Android ({ua_model})"

        return "Android Device"

    elif os_type == "mac":
        if gpu_renderer:
            mac_name = _detect_from_gpu(gpu_renderer)
            if mac_name:
                return mac_name
        return "Mac"

    elif os_type == "windows":
        if gpu_renderer:
            gpu_device = _detect_from_gpu(gpu_renderer)
            if gpu_device:
                return gpu_device
        return "Windows PC"

    elif os_type == "linux":
        if gpu_renderer:
            gpu_device = _detect_from_gpu(gpu_renderer)
            if gpu_device:
                return gpu_device
        return "Linux PC"

    # ── Priority 7: Last resort — try GPU alone ──
    if gpu_renderer:
        gpu_device = _detect_from_gpu(gpu_renderer)
        if gpu_device:
            return gpu_device

    # ── Priority 8: Raw platform string ──
    if platform:
        platform_map = {
            "Win32": "Windows PC",
            "Win64": "Windows PC",
            "MacIntel": "Mac",
            "MacARM": "Mac",
            "MacPPC": "Mac",
            "iPhone": "iPhone",
            "iPad": "iPad",
            "iPod": "iPod",
        }
        for key, name in platform_map.items():
            if platform.startswith(key):
                return name
    if "Linux" in platform:
        return "Linux Device"

    return "Unknown Device"


def _get_platform_group(name: str | None) -> str:
    """Categorize a device/model name into a broad platform group."""
    if not name:
        return "unknown"
    name_lower = name.lower()
    if any(k in name_lower for k in ("iphone", "ipad", "ios", "apple gpu")):
        return "ios"
    if any(k in name_lower for k in ("android", "samsung", "galaxy", "pixel", "redmi", "pixel", "xiaomi", "oppo", "vivo")):
        return "android"
    if "mac" in name_lower or any(k in name_lower for k in ("apple m1", "apple m2", "apple m3", "apple m4")):
        return "mac"
    if "windows" in name_lower:
        return "windows"
    if "linux" in name_lower:
        return "linux"
    return "unknown"


# ═══════════════════════════════════════════════════════════════════════════════
# User-Provided Device Model Validation
# ═══════════════════════════════════════════════════════════════════════════════


def validate_device_model(
    device_model: str | None, fingerprint: dict | None = None
) -> str:
    """
    Validate user-provided device model in accordance with what the device actually is.
    
    Cross-references hardware/browser signals with user input to prevent platform
    mismatches (e.g. user selects 'iPhone' while on a Windows PC).
    """
    user_model = validate_input(device_model)
    user_model_lower = user_model.lower()
    
    # 1. Get ground truth from fingerprint detection
    detected_name = extract_device_name(fingerprint) if fingerprint else "Unknown Device"
    detected_group = _get_platform_group(detected_name)
    
    # 2. If user is 'Not Sure' or hasn't provided a model, use the detected one
    if not user_model or user_model_lower == "not_sure" or user_model_lower == "unknown device":
        logger.info(f"User selected 'Not Sure' or provided no model. Detected: {detected_name}")
        return detected_name

    # 3. Handle Platform Consistency
    user_group = _get_platform_group(user_model)
    
    # If there is a fundamental platform mismatch (e.g. User says Android, Fingerprint says iOS)
    # trust the hard signals from the fingerprint.
    if user_group != "unknown" and detected_group != "unknown" and user_group != detected_group:
        logger.warning(f"Platform mismatch! User claimed '{user_model}' ({user_group}), but signals detected '{detected_name}' ({detected_group}). Overriding user input.")
        return detected_name

    # 4. If platforms match or user input is generic, refine/enrich the user input
    # Android refinement (Marketing name lookup)
    if user_group == "android" or any(k in user_model_lower for k in ("samsung", "pixel", "galaxy", "sm-")):
        from app.device_detection.devices import store
        
        # Exact model code match
        device = store.get_by_model(user_model)
        if device and device.marketing_name:
            name = device.marketing_name
            if not name.lower().startswith(device.brand.lower()):
                name = f"{device.brand} {name}"
            logger.info(f"User Android model enriched: {user_model} -> {name}")
            return name

        # Fuzzy search fallback
        if store.total:
            try:
                matches = store.fuzzy_search(user_model, limit=1)
                if matches:
                    best = matches[0]
                    name = best.marketing_name
                    if not name.lower().startswith(best.brand.lower()):
                        name = f"{best.brand} {name}"
                    logger.info(f"User Android model fuzzy-enriched: {user_model} -> {name}")
                    return name
            except Exception:
                pass

    # For other platforms (iOS, Mac, Windows, Linux) where platforms match, trust the user input 
    # as it's often more specific about the exact model than we can be via browser APIs.
    logger.info(f"User provided specific model '{user_model}' matching detected platform '{detected_group}'. Trusting user input.")
    return user_model

