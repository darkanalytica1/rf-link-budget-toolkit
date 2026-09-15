"""Free-space propagation, antenna gain and line-of-sight geometry.

All functions are pure and use explicit units in their argument names.
Formulas follow ITU-R P.525 (free-space loss) and the usual 4/3 effective
Earth radius approximation for the radio horizon (ITU-R P.453 / P.834).
"""
from __future__ import annotations

import math

C_M_S = 299_792_458.0
"""Speed of light in vacuum, m/s."""

FSPL_CONSTANT_KM_MHZ = 32.44
"""Constant for FSPL with distance in km and frequency in MHz (20log10(4*pi*1e9/c))."""


def wavelength_m(freq_hz: float) -> float:
    """Wavelength in metres, lambda = c / f."""
    if freq_hz <= 0:
        raise ValueError("frequency must be positive")
    return C_M_S / freq_hz


def fspl_db(dist_km: float, freq_mhz: float) -> float:
    """Free-space path loss between isotropic antennas, in dB.

    FSPL = 20 log10(d_km) + 20 log10(f_MHz) + 32.44

    Valid in the far field with clear line of sight and an unobstructed first
    Fresnel zone. The frequency term reflects the smaller capture area of an
    isotropic antenna at shorter wavelength, not atmospheric absorption.
    """
    if dist_km <= 0 or freq_mhz <= 0:
        raise ValueError("distance and frequency must be positive")
    return 20 * math.log10(dist_km) + 20 * math.log10(freq_mhz) + FSPL_CONSTANT_KM_MHZ


def range_for_loss_km(loss_db: float, freq_mhz: float) -> float:
    """Invert FSPL: the free-space distance (km) at which the loss equals loss_db."""
    return 10 ** ((loss_db - 20 * math.log10(freq_mhz) - FSPL_CONSTANT_KM_MHZ) / 20)


def range_factor(delta_db: float) -> float:
    """Free-space distance factor bought by delta_db of budget (6.02 dB doubles range)."""
    return 10 ** (delta_db / 20)


def gain_from_beamwidth_dbi(az_deg: float, el_deg: float, practical: bool = True) -> float:
    """Approximate antenna gain from half-power beamwidths in degrees.

    Ideal (lossless, no sidelobes): G = 41,253 / (theta_az * theta_el).
    Practical (typical efficiency and sidelobes): G ~ 30,000 / (theta_az * theta_el).
    """
    if az_deg <= 0 or el_deg <= 0:
        raise ValueError("beamwidths must be positive")
    k = 30_000.0 if practical else 41_253.0
    return 10 * math.log10(k / (az_deg * el_deg))


def radio_horizon_km(h1_m: float, h2_m: float = 0.0) -> float:
    """Line-of-sight radio horizon over smooth Earth with k = 4/3.

    d_km ~ 4.12 (sqrt(h1) + sqrt(h2)), heights in metres above the surface.
    """
    if h1_m < 0 or h2_m < 0:
        raise ValueError("heights must be non-negative")
    return 4.12 * (math.sqrt(h1_m) + math.sqrt(h2_m))


def fresnel_radius_m(dist_km: float, freq_ghz: float, d1_km: float | None = None, n: int = 1) -> float:
    """Radius of the n-th Fresnel zone at a point along the path, in metres.

    r_n = 17.32 * sqrt(n * d1 * d2 / (f_GHz * d)), distances in km.
    With d1 omitted the point is mid-path, which gives the largest radius:
    r_1 = 17.32 * sqrt(d / (4 f_GHz)).
    A common planning rule keeps at least 60 % of the first zone clear.
    """
    if dist_km <= 0 or freq_ghz <= 0 or n < 1:
        raise ValueError("distance, frequency and zone number must be positive")
    d1 = dist_km / 2 if d1_km is None else d1_km
    d2 = dist_km - d1
    if not 0 < d1 < dist_km:
        raise ValueError("d1 must lie strictly inside the path")
    return 17.32 * math.sqrt(n * d1 * d2 / (freq_ghz * dist_km))
