"""Static device databases for screen-based, model-based, and GPU-based detection.

Extracted from the monolithic device_detection module into its own file
so data stays separate from logic.
"""

from __future__ import annotations

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 1: iPhone Screen-Based Detection
# ═══════════════════════════════════════════════════════════════════════════════
# iOS user agents NEVER reveal the model — they all just say "iPhone".
# The only reliable browser-side signals are logical screen dimensions + DPR.
# We store (width, height) in portrait orientation (smaller dimension first).
# Source: ios-resolution.com (updated 2026-03-26), Apple developer docs.
#
# NOTE: Multiple iPhone generations share the same screen profile. We list
# ALL models that match each profile so the user gets the full picture.


IPHONE_SCREEN_DB: list[tuple[tuple[int, int], int, str]] = [
    # ── 2026 / 2025 iPhones ──
    ((440, 956), 3, "iPhone 16 Pro Max / 17 Pro Max"),
    ((420, 912), 3, "iPhone Air"),
    ((402, 874), 3, "iPhone 16 Pro / 17 / 17 Pro"),
    ((430, 932), 3, "iPhone 14 Pro Max / 15 Plus / 15 Pro Max / 16 Plus"),
    ((393, 852), 3, "iPhone 14 Pro / 15 / 15 Pro / 16"),
    # ── 2022 / 2021 / 2020 iPhones ──
    ((428, 926), 3, "iPhone 12 Pro Max / 13 Pro Max / 14 Plus"),
    ((390, 844), 3, "iPhone 12 / 12 Pro / 13 / 13 Pro / 14 / 16e / 17e"),
    ((375, 812), 3, "iPhone X / XS / 11 Pro / 12 mini / 13 mini"),
    ((414, 896), 3, "iPhone XS Max / 11 Pro Max"),
    ((414, 896), 2, "iPhone XR / 11"),
    # ── Older iPhones ──
    ((414, 736), 3, "iPhone 6 Plus / 6S Plus / 7 Plus / 8 Plus"),
    ((375, 667), 2, "iPhone 6 / 6S / 7 / 8 / SE 2nd / SE 3rd"),
    ((320, 568), 2, "iPhone 5 / 5C / 5S / SE 1st"),
    ((320, 480), 2, "iPhone 4 / 4S"),
    ((320, 480), 1, "iPhone 3G / 3GS / 1st gen"),
]

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 2: iPad Screen-Based Detection
# ═══════════════════════════════════════════════════════════════════════════════
# All modern iPads have DPR 2. Source: ios-resolution.com, Apple developer docs.

IPAD_SCREEN_DB: list[tuple[tuple[int, int], int, str]] = [
    # ── Pro 13" / 12.9" ──
    ((1032, 1376), 2, 'iPad Pro 13" (M4 / 8th gen)'),
    (
        (1024, 1366),
        2,
        'iPad Pro 12.9" (1st–6th gen) / iPad Air 13" (M2 / 7th / 8th gen)',
    ),
    # ── Pro 11" ──
    ((834, 1210), 2, 'iPad Pro 11" (M4 / 8th gen)'),
    ((834, 1194), 2, 'iPad Pro 11" (1st–4th gen) / iPad Air 4th / 5th'),
    # ── Air 11" / 10th gen iPad ──
    ((820, 1180), 2, 'iPad 10th / 11th gen / iPad Air 11" (M2 / 7th / 8th gen)'),
    # ── Pro 10.5" / Air 3rd ──
    ((834, 1112), 2, 'iPad Air 3rd / iPad Pro 10.5"'),
    # ── 9.7" iPads / iPad 7th–9th / minis ──
    ((810, 1080), 2, "iPad 7th / 8th / 9th gen"),
    ((768, 1024), 2, "iPad 5th / 6th / Air 2 / Mini 2 / 3 / 4 / 5"),
    # ── Mini 6+ ──
    ((744, 1133), 2, "iPad Mini 6th / 7th gen"),
    # ── Legacy non-retina ──
    ((768, 1024), 1, "iPad 1st / 2nd gen / Mini 1st"),
]


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 3: Apple Silicon Patterns (Mac detection via WebGL GPU)
# ═══════════════════════════════════════════════════════════════════════════════

APPLE_SILICON_PATTERNS: list[tuple[str, str]] = [
    # Order: most specific first (Ultra > Max > Pro > base)
    ("Apple M4 Ultra", "Mac (Apple M4 Ultra)"),
    ("Apple M4 Max", "Mac (Apple M4 Max)"),
    ("Apple M4 Pro", "MacBook Pro (Apple M4 Pro)"),
    ("Apple M4", "Mac (Apple M4)"),
    ("Apple M3 Ultra", "Mac (Apple M3 Ultra)"),
    ("Apple M3 Max", "Mac (Apple M3 Max)"),
    ("Apple M3 Pro", "MacBook Pro (Apple M3 Pro)"),
    ("Apple M3", "Mac (Apple M3)"),
    ("Apple M2 Ultra", "Mac Studio / Mac Pro (Apple M2 Ultra)"),
    ("Apple M2 Max", "Mac (Apple M2 Max)"),
    ("Apple M2 Pro", "MacBook Pro (Apple M2 Pro)"),
    ("Apple M2", "Mac (Apple M2)"),
    ("Apple M1 Ultra", "Mac Studio (Apple M1 Ultra)"),
    ("Apple M1 Max", "Mac (Apple M1 Max)"),
    ("Apple M1 Pro", "MacBook Pro (Apple M1 Pro)"),
    ("Apple M1", "Mac (Apple M1)"),
]

# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 7: Desktop & Mobile GPU Pattern Matching
# ═══════════════════════════════════════════════════════════════════════════════

DESKTOP_GPU_PATTERNS: list[tuple[str, str]] = [
    # ── NVIDIA ──
    (r"NVIDIA GeForce RTX 50\d{2}", "Windows PC (NVIDIA RTX 50-series)"),
    (r"NVIDIA GeForce RTX 40\d{2}", "Windows PC (NVIDIA RTX 40-series)"),
    (r"NVIDIA GeForce RTX 30\d{2}", "Windows PC (NVIDIA RTX 30-series)"),
    (r"NVIDIA GeForce RTX 20\d{2}", "Windows PC (NVIDIA RTX 20-series)"),
    (r"NVIDIA GeForce GTX 16\d{2}", "Windows PC (NVIDIA GTX 16-series)"),
    (r"NVIDIA GeForce GTX 10\d{2}", "Windows PC (NVIDIA GTX 10-series)"),
    (r"NVIDIA GeForce GTX 9\d{2}", "Windows PC (NVIDIA GTX 900-series)"),
    (r"NVIDIA GeForce MX\d+", "Windows PC (NVIDIA MX)"),
    (r"NVIDIA", "PC (NVIDIA GPU)"),
    # ── AMD ──
    (r"AMD Radeon RX 9\d{3}", "Windows PC (AMD RX 9000)"),
    (r"AMD Radeon RX 7\d{3}", "Windows PC (AMD RX 7000)"),
    (r"AMD Radeon RX 6\d{3}", "Windows PC (AMD RX 6000)"),
    (r"AMD Radeon RX 5\d{3}", "Windows PC (AMD RX 5000)"),
    (r"AMD Radeon RX Vega", "Windows PC (AMD Vega)"),
    (r"AMD Radeon", "PC (AMD Radeon)"),
    (r"Radeon", "PC (AMD Radeon)"),
    # ── Intel ──
    (r"Intel.*Arc", "Windows PC (Intel Arc)"),
    (r"Intel.*Iris.*Xe", "Windows PC (Intel Iris Xe)"),
    (r"Intel.*UHD", "Windows PC (Intel UHD)"),
    (r"Intel.*Iris", "Windows PC (Intel Iris)"),
    (r"Intel.*HD Graphics", "Windows PC (Intel HD Graphics)"),
    # ── Qualcomm Adreno (Android) ──
    (r"Adreno.*8\d{2}", "Android (Qualcomm Adreno 8xx)"),
    (r"Adreno.*7\d{2}", "Android (Qualcomm Adreno 7xx)"),
    (r"Adreno.*6\d{2}", "Android (Qualcomm Adreno 6xx)"),
    (r"Adreno.*5\d{2}", "Android (Qualcomm Adreno 5xx)"),
    (r"Adreno.*4\d{2}", "Android (Qualcomm Adreno 4xx)"),
    (r"Adreno", "Android (Qualcomm Adreno)"),
    # ── ARM Mali (Android — Samsung Exynos, MediaTek Dimensity) ──
    (r"Mali-G7\d{2}", "Android (ARM Mali G7xx)"),
    (r"Mali-G6\d{2}", "Android (ARM Mali G6xx)"),
    (r"Mali-G5\d{2}", "Android (ARM Mali G5xx)"),
    (r"Mali-G\d+", "Android (ARM Mali)"),
    (r"Mali-T\d+", "Android (ARM Mali)"),
    (r"Mali", "Android (ARM Mali)"),
    # ── ARM Immortalis (high-end MediaTek Dimensity 9000+) ──
    (r"Immortalis", "Android (ARM Immortalis)"),
    # ── Samsung Xclipse (Exynos 2200+) ──
    (r"Xclipse", "Android (Samsung Xclipse)"),
    # ── IMG PowerVR ──
    (r"PowerVR", "Android (PowerVR)"),
]
