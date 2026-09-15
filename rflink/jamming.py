"""Jammer-to-signal ratio, burn-through and GNSS jamming geometry.

These are free-space screening estimates. The outcome of jamming is decided
by J/S at the victim receiver, not at the jammer, and the J/S a given
receiver tolerates depends on its waveform, coding and processing.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

from .propagation import fspl_db, range_factor

GPS_L1_MHZ = 1575.42
GPS_L1_MIN_RX_DBM = -128.5
"""IS-GPS-200 minimum received L1 C/A power at the surface: -158.5 dBW = -128.5 dBm."""


def comms_js_db(
    jammer_power_dbm: float,
    jammer_gain_dbi: float,
    tx_power_dbm: float,
    tx_gain_dbi: float,
    dist_signal_km: float,
    dist_jammer_km: float,
    rx_gain_to_jammer_dbi: float = 0.0,
    rx_gain_to_tx_dbi: float = 0.0,
    rx_bandwidth_hz: float | None = None,
    jammer_bandwidth_hz: float | None = None,
) -> float:
    """Communications J/S at the victim receiver (both paths free space, same frequency).

    J/S = (Pj + Gj + Grj) - (Pt + Gt + Grt) + 20 log10(ds / dj) + 10 log10(Br / Bj)

    The bandwidth term only applies when the jammer spreads its power over a
    wider band than the receiver (Bj > Br); otherwise it is zero.
    """
    if dist_signal_km <= 0 or dist_jammer_km <= 0:
        raise ValueError("distances must be positive")
    js = (jammer_power_dbm + jammer_gain_dbi + rx_gain_to_jammer_dbi) - (tx_power_dbm + tx_gain_dbi + rx_gain_to_tx_dbi)
    js += 20 * math.log10(dist_signal_km / dist_jammer_km)
    if rx_bandwidth_hz and jammer_bandwidth_hz and jammer_bandwidth_hz > rx_bandwidth_hz:
        js += 10 * math.log10(rx_bandwidth_hz / jammer_bandwidth_hz)
    return js


@dataclass(frozen=True)
class BurnThrough:
    js_db: float
    js_required_db: float

    @property
    def spare_db(self) -> float:
        """J/S above what the jammer needs. Positive means the link is jammed."""
        return self.js_db - self.js_required_db

    @property
    def distance_factor(self) -> float:
        """How far the geometry can change before the balance flips (free space)."""
        return range_factor(abs(self.spare_db))

    def signal_distance_to_burn_through_km(self, dist_signal_km: float) -> float:
        """Distance the wanted transmitter must close to for the link to survive."""
        return dist_signal_km / range_factor(self.spare_db)

    def jammer_standoff_km(self, dist_jammer_km: float) -> float:
        """Furthest jammer distance that still achieves the required J/S."""
        return dist_jammer_km * range_factor(self.spare_db)


def burn_through(js_db: float, js_required_db: float) -> BurnThrough:
    return BurnThrough(js_db, js_required_db)


@dataclass(frozen=True)
class GnssJamming:
    fspl_db: float
    jammer_rx_dbm: float
    js_db: float
    lock_loss_js_db: float

    @property
    def spare_db(self) -> float:
        return self.js_db - self.lock_loss_js_db

    def denial_range_km(self, dist_km: float, horizon_km: float | None = None) -> float:
        """Free-space distance at which J/S falls to the lock-loss threshold, capped by the horizon."""
        d = dist_km * range_factor(self.spare_db)
        return min(d, horizon_km) if horizon_km else d


def gnss_js(
    jammer_power_dbm: float,
    jammer_gain_dbi: float,
    dist_km: float,
    freq_mhz: float = GPS_L1_MHZ,
    signal_dbm: float = GPS_L1_MIN_RX_DBM,
    lock_loss_js_db: float = 30.0,
    rx_gain_to_jammer_dbi: float = 0.0,
) -> GnssJamming:
    """J/S of a GNSS jammer at a receiver: J = Pj + Gj - FSPL(d, f); J/S = J - S.

    lock_loss_js_db is a planning assumption, not a property of GNSS: tracking
    loss for an unaided civil receiver is often placed somewhere around 25-35 dB
    J/S, and it varies widely with receiver design, aiding and antenna.
    """
    loss = fspl_db(dist_km, freq_mhz)
    j = jammer_power_dbm + jammer_gain_dbi + rx_gain_to_jammer_dbi - loss
    return GnssJamming(loss, j, j - signal_dbm, lock_loss_js_db)
