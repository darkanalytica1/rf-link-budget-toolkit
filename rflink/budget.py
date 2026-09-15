"""Link budget, thermal noise floor, SNR and the Shannon bound."""
from __future__ import annotations

import math
from dataclasses import dataclass, field

from .propagation import fspl_db

THERMAL_NOISE_DBM_HZ = -174.0
"""kTB noise density at T0 = 290 K, in dBm/Hz (10log10(1.380649e-23 * 290 * 1000))."""


def dbm_to_w(dbm: float) -> float:
    return 10 ** ((dbm - 30) / 10)


def w_to_dbm(watts: float) -> float:
    if watts <= 0:
        raise ValueError("power must be positive")
    return 10 * math.log10(watts) + 30


def eirp_dbm(tx_power_dbm: float, tx_gain_dbi: float, feed_loss_db: float = 0.0) -> float:
    """Effective isotropic radiated power: transmit power + antenna gain - feed losses."""
    return tx_power_dbm + tx_gain_dbi - feed_loss_db


def noise_floor_dbm(bandwidth_hz: float, noise_figure_db: float = 0.0) -> float:
    """Receiver noise floor: N = -174 + 10 log10(B) + NF (dBm)."""
    if bandwidth_hz <= 0:
        raise ValueError("bandwidth must be positive")
    return THERMAL_NOISE_DBM_HZ + 10 * math.log10(bandwidth_hz) + noise_figure_db


def shannon_capacity_bps(bandwidth_hz: float, snr_db: float) -> float:
    """Upper bound on error-free rate: C = B log2(1 + SNR)."""
    return bandwidth_hz * math.log2(1 + 10 ** (snr_db / 10))


@dataclass(frozen=True)
class LinkBudget:
    """Inputs of a one-way line-of-sight link. Powers in dBm, gains in dBi, losses in dB."""

    freq_mhz: float
    dist_km: float
    tx_power_dbm: float
    tx_gain_dbi: float
    rx_gain_dbi: float
    bandwidth_hz: float
    noise_figure_db: float
    misc_loss_db: float = 0.0
    required_snr_db: float = 0.0
    extra_path_loss_db: float = 0.0

    def evaluate(self) -> "LinkResult":
        path = fspl_db(self.dist_km, self.freq_mhz) + self.extra_path_loss_db
        eirp = eirp_dbm(self.tx_power_dbm, self.tx_gain_dbi)
        rx = eirp + self.rx_gain_dbi - path - self.misc_loss_db
        noise = noise_floor_dbm(self.bandwidth_hz, self.noise_figure_db)
        snr = rx - noise
        steps = [
            ("Transmit power", self.tx_power_dbm, self.tx_power_dbm),
            ("Tx antenna gain", self.tx_gain_dbi, eirp),
            ("Path loss", -path, eirp - path),
            ("Rx antenna gain", self.rx_gain_dbi, eirp - path + self.rx_gain_dbi),
            ("Cable and misc", -self.misc_loss_db, rx),
        ]
        return LinkResult(
            eirp_dbm=eirp,
            path_loss_db=path,
            rx_power_dbm=rx,
            noise_dbm=noise,
            snr_db=snr,
            margin_db=snr - self.required_snr_db,
            capacity_bps=shannon_capacity_bps(self.bandwidth_hz, snr),
            steps=steps,
        )


@dataclass(frozen=True)
class LinkResult:
    eirp_dbm: float
    path_loss_db: float
    rx_power_dbm: float
    noise_dbm: float
    snr_db: float
    margin_db: float
    capacity_bps: float
    steps: list = field(default_factory=list)

    @property
    def closes(self) -> bool:
        return self.margin_db >= 0

    def as_text(self) -> str:
        lines = [f"  {name:<18} {delta:+8.1f} dB   -> {level:+7.1f} dBm" for name, delta, level in self.steps]
        lines += [
            f"  {'Received power':<18} {self.rx_power_dbm:+8.1f} dBm",
            f"  {'Noise floor':<18} {self.noise_dbm:+8.1f} dBm",
            f"  {'SNR':<18} {self.snr_db:+8.1f} dB",
            f"  {'Margin':<18} {self.margin_db:+8.1f} dB   ({'closes' if self.closes else 'FAILS'})",
            f"  {'Shannon bound':<18} {self.capacity_bps / 1e6:8.1f} Mbit/s",
        ]
        return "\n".join(lines)
