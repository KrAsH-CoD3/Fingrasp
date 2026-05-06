"""Static device databases for screen-based, model-based, and GPU-based detection.

Extracted from the monolithic device_detection module into its own file
so data stays separate from logic.
"""

from __future__ import annotations

SCREEN_DB = list[tuple[tuple[int, int], int, str]]
IOS_MODELS = list[str]

# ═══════════════════════════════════════════════════════════════════════════════
# --- iPhone Device Detection Mapping ---
# ═══════════════════════════════════════════════════════════════════════════════
# iOS user agents NEVER reveal the model — they all just say "iPhone".
# The only reliable browser-side signals are logical screen dimensions + DPR.
# We store (width, height) in portrait orientation (smaller dimension first).
# Source: ios-resolution.com (updated 2026-03-26), Apple developer docs.
#
# NOTE: Multiple iPhone generations share the same screen profile. We list
# ALL models that match each profile so the user gets the full picture.


IPHONE_SCREEN_DB: SCREEN_DB = [
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
# --- iPad Device Detection Mapping ---
# ═══════════════════════════════════════════════════════════════════════════════
# All modern iPads have DPR 2. Source: ios-resolution.com, Apple developer docs.

IPAD_SCREEN_DB: SCREEN_DB = [
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
# --- Curated Device Models for Web Interface ---
# ═══════════════════════════════════════════════════════════════════════════════
# Every model listed individually for accurate user selection.
# The user's exact model is used as device_name in the DB.

INDIVIDUAL_IPHONE_MODELS: IOS_MODELS = [
    # 2026
    "iPhone 17 Pro Max",
    "iPhone 17 Pro",
    "iPhone 17",
    "iPhone 17e",
    "iPhone Air",
    # 2025
    "iPhone 16 Pro Max",
    "iPhone 16 Pro",
    "iPhone 16 Plus",
    "iPhone 16",
    "iPhone 16e",
    # 2024
    "iPhone 15 Pro Max",
    "iPhone 15 Pro",
    "iPhone 15 Plus",
    "iPhone 15",
    # 2023
    "iPhone 14 Pro Max",
    "iPhone 14 Pro",
    "iPhone 14 Plus",
    "iPhone 14",
    # 2022
    "iPhone 13 Pro Max",
    "iPhone 13 Pro",
    "iPhone 13",
    "iPhone 13 mini",
    # 2021
    "iPhone 12 Pro Max",
    "iPhone 12 Pro",
    "iPhone 12",
    "iPhone 12 mini",
    # 2020
    "iPhone SE 3rd generation",
    "iPhone SE 2nd generation",
    # 2019
    "iPhone 11 Pro Max",
    "iPhone 11 Pro",
    "iPhone 11",
    # 2018
    "iPhone XS Max",
    "iPhone XS",
    "iPhone XR",
    "iPhone X",
    # 2017
    "iPhone 8 Plus",
    "iPhone 8",
    # 2016
    "iPhone 7 Plus",
    "iPhone 7",
    # 2015
    "iPhone 6S Plus",
    "iPhone 6S",
    "iPhone SE 1st generation",
    # 2014
    "iPhone 6 Plus",
    "iPhone 6",
    # 2013
    "iPhone 5S",
    "iPhone 5C",
    # 2012
    "iPhone 5",
    # 2011
    "iPhone 4S",
    # 2010
    "iPhone 4",
    # 2009
    "iPhone 3GS",
    # 2008
    "iPhone 3G",
    # 2007
    "iPhone 1st generation",
]

INDIVIDUAL_IPAD_MODELS: IOS_MODELS = [
    # iPad Pro
    'iPad Pro 13" (M4)',
    'iPad Pro 12.9" (6th generation)',
    'iPad Pro 12.9" (5th generation)',
    'iPad Pro 12.9" (4th generation)',
    'iPad Pro 12.9" (3rd generation)',
    'iPad Pro 12.9" (2nd generation)',
    'iPad Pro 12.9" (1st generation)',
    'iPad Pro 11" (M4)',
    'iPad Pro 11" (4th generation)',
    'iPad Pro 11" (3rd generation)',
    'iPad Pro 11" (2nd generation)',
    'iPad Pro 11" (1st generation)',
    'iPad Pro 10.5"',
    'iPad Pro 9.7"',
    # iPad Air
    'iPad Air 13" (M2)',
    'iPad Air 13" (7th generation)',
    'iPad Air 13" (8th generation)',
    'iPad Air 11" (M2)',
    'iPad Air 11" (7th generation)',
    'iPad Air 11" (8th generation)',
    "iPad Air 5th generation (M1)",
    "iPad Air 4th generation",
    "iPad Air 3rd generation",
    "iPad Air 2",
    "iPad Air 1st generation",
    # iPad
    "iPad 11th generation",
    "iPad 10th generation",
    "iPad 9th generation",
    "iPad 8th generation",
    "iPad 7th generation",
    "iPad 6th generation",
    "iPad 5th generation",
    # iPad Mini
    "iPad Mini 7th generation",
    "iPad Mini 6th generation",
    "iPad Mini 5th generation",
    "iPad Mini 4",
    "iPad Mini 3",
    "iPad Mini 2",
    "iPad Mini 1st generation",
]

INDIVIDUAL_MAC_MODELS: IOS_MODELS = [
    # MacBook Pro
    'MacBook Pro 16" (M4 Max)',
    'MacBook Pro 16" (M4 Pro)',
    'MacBook Pro 14" (M4 Max)',
    'MacBook Pro 14" (M4 Pro)',
    'MacBook Pro 14" (M4)',
    'MacBook Pro 16" (M3 Max)',
    'MacBook Pro 16" (M3 Pro)',
    'MacBook Pro 14" (M3 Max)',
    'MacBook Pro 14" (M3 Pro)',
    'MacBook Pro 14" (M3)',
    'MacBook Pro 16" (M2 Max)',
    'MacBook Pro 16" (M2 Pro)',
    'MacBook Pro 14" (M2 Max)',
    'MacBook Pro 14" (M2 Pro)',
    'MacBook Pro 13" (M2)',
    'MacBook Pro 16" (M1 Max)',
    'MacBook Pro 16" (M1 Pro)',
    'MacBook Pro 14" (M1 Max)',
    'MacBook Pro 14" (M1 Pro)',
    'MacBook Pro 13" (M1)',
    'MacBook Pro 17" (Intel)',
    'MacBook Pro 16" (Intel)',
    'MacBook Pro 15" (Intel)',
    'MacBook Pro 13" (Intel)',
    # MacBook Air
    'MacBook Air 15" (M3)',
    'MacBook Air 13" (M3)',
    'MacBook Air 15" (M2)',
    'MacBook Air 13" (M2)',
    "MacBook Air (M1)",
    'MacBook Air 13" (Intel)',
    'MacBook Air 11" (Intel)',
    "MacBook Air (Intel)",
    # MacBook
    'MacBook 12" (Retina)',
    "MacBook (Intel)",
    # iMac
    'iMac 24" (M3)',
    'iMac 24" (M1)',
    'iMac Pro 27" (Intel)',
    'iMac 27" (Intel)',
    'iMac 24" (Intel)',
    'iMac 21.5" (Intel)',
    'iMac 20" (Intel)',
    # Mac Pro
    "Mac Pro (M2 Ultra)",
    "Mac Pro (Intel)",
    "Mac Pro (Late 2013)",
    # Mac Studio
    "Mac Studio (M2 Ultra)",
    "Mac Studio (M2 Max)",
    "Mac Studio (M1 Ultra)",
    "Mac Studio (M1 Max)",
    # Mac Mini
    "Mac Mini (M2 Pro)",
    "Mac Mini (M2)",
    "Mac Mini (M1)",
    "Mac Mini (Intel)",
]


# ═══════════════════════════════════════════════════════════════════════════════
# --- Screen Profile to Model Lookup Mappings ---
# ═══════════════════════════════════════════════════════════════════════════════
# Explicit mapping from "WxHxDPR" screen profile keys to the exact individual
# model names from the lists above. This is used by the frontend to filter the
# dropdown to only show models matching the user's actual hardware.
# Zero parsing ambiguity — every model is listed by name.

IPHONE_SCREEN_MODELS: dict[str, list[str]] = {
    "440x956x3": ["iPhone 16 Pro Max", "iPhone 17 Pro Max"],
    "420x912x3": ["iPhone Air"],
    "402x874x3": ["iPhone 16 Pro", "iPhone 17", "iPhone 17 Pro"],
    "430x932x3": ["iPhone 14 Pro Max", "iPhone 15 Plus", "iPhone 15 Pro Max", "iPhone 16 Plus"],
    "393x852x3": ["iPhone 14 Pro", "iPhone 15", "iPhone 15 Pro", "iPhone 16"],
    "428x926x3": ["iPhone 12 Pro Max", "iPhone 13 Pro Max", "iPhone 14 Plus"],
    "390x844x3": ["iPhone 12", "iPhone 12 Pro", "iPhone 13", "iPhone 13 Pro", "iPhone 14", "iPhone 16e", "iPhone 17e"],
    "375x812x3": ["iPhone X", "iPhone XS", "iPhone 11 Pro", "iPhone 12 mini", "iPhone 13 mini"],
    "414x896x3": ["iPhone XS Max", "iPhone 11 Pro Max"],
    "414x896x2": ["iPhone XR", "iPhone 11"],
    "414x736x3": ["iPhone 6 Plus", "iPhone 6S Plus", "iPhone 7 Plus", "iPhone 8 Plus"],
    "375x667x2": ["iPhone 6", "iPhone 6S", "iPhone 7", "iPhone 8", "iPhone SE 2nd generation", "iPhone SE 3rd generation"],
    "320x568x2": ["iPhone 5", "iPhone 5C", "iPhone 5S", "iPhone SE 1st generation"],
    "320x480x2": ["iPhone 4", "iPhone 4S"],
    "320x480x1": ["iPhone 3G", "iPhone 3GS", "iPhone 1st generation"],
}

IPAD_SCREEN_MODELS: dict[str, list[str]] = {
    "1032x1376x2": [
        'iPad Pro 13" (M4)',
    ],
    "1024x1366x2": [
        'iPad Pro 12.9" (6th generation)',
        'iPad Pro 12.9" (5th generation)',
        'iPad Pro 12.9" (4th generation)',
        'iPad Pro 12.9" (3rd generation)',
        'iPad Pro 12.9" (2nd generation)',
        'iPad Pro 12.9" (1st generation)',
        'iPad Air 13" (M2)',
        'iPad Air 13" (7th generation)',
        'iPad Air 13" (8th generation)',
    ],
    "834x1210x2": [
        'iPad Pro 11" (M4)',
    ],
    "834x1194x2": [
        'iPad Pro 11" (4th generation)',
        'iPad Pro 11" (3rd generation)',
        'iPad Pro 11" (2nd generation)',
        'iPad Pro 11" (1st generation)',
        "iPad Air 5th generation (M1)",
        "iPad Air 4th generation",
    ],
    "820x1180x2": [
        "iPad 10th generation",
        "iPad 11th generation",
        'iPad Air 11" (M2)',
        'iPad Air 11" (7th generation)',
        'iPad Air 11" (8th generation)',
    ],
    "834x1112x2": [
        "iPad Air 3rd generation",
        'iPad Pro 10.5"',
    ],
    "810x1080x2": [
        "iPad 7th generation",
        "iPad 8th generation",
        "iPad 9th generation",
    ],
    "768x1024x2": [
        "iPad 5th generation",
        "iPad 6th generation",
        "iPad Air 2",
        "iPad Air 1st generation",
        "iPad Mini 2",
        "iPad Mini 3",
        "iPad Mini 4",
        "iPad Mini 5th generation",
    ],
    "744x1133x2": [
        "iPad Mini 6th generation",
        "iPad Mini 7th generation",
    ],
    "768x1024x1": [
        "iPad Mini 1st generation",
    ],
}


# ═══════════════════════════════════════════════════════════════════════════════
# --- Mac & Apple Silicon WebGL Identification Patterns ---
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
# --- Desktop & Mobile GPU Vendor Pattern Matching ---
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
