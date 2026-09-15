"""The worked examples used throughout the docs, as reproducible code.

Each function returns the numbers and states its assumptions, so the docs,
the CLI and the tests all draw on one source.
"""
from __future__ import annotations

from .budget import LinkBudget
from .jamming import burn_through, comms_js_db, gnss_js
from .propagation import fresnel_radius_m, fspl_db, gain_from_beamwidth_dbi, radio_horizon_km, wavelength_m


def video_link_5km():
    """2.4 GHz video downlink at 5 km: 20 dBm, 2 dBi Tx, 10 dBi Rx, 2 dB misc, 20 MHz, NF 6 dB, 8 dB required SNR."""
    return LinkBudget(
        freq_mhz=2400, dist_km=5, tx_power_dbm=20, tx_gain_dbi=2, rx_gain_dbi=10,
        bandwidth_hz=20e6, noise_figure_db=6, misc_loss_db=2, required_snr_db=8,
    )


def uplink_jamming():
    """Drone 3 km from its pilot, jammer 1 km from the drone, 2.4 GHz.

    Pilot 20 dBm / 2 dBi; jammer 40 dBm (10 W) / 12 dBi spread over 80 MHz;
    victim receiver 20 MHz with a 0 dBi antenna; link assumed to fail above 10 dB J/S.
    """
    js = comms_js_db(
        jammer_power_dbm=40, jammer_gain_dbi=12, tx_power_dbm=20, tx_gain_dbi=2,
        dist_signal_km=3, dist_jammer_km=1, rx_bandwidth_hz=20e6, jammer_bandwidth_hz=80e6,
    )
    s_dbm = 20 + 2 - fspl_db(3, 2400)
    j_dbm = 40 + 12 - fspl_db(1, 2400) - 6.02
    bt = burn_through(js, 10.0)
    return {
        "S_dbm": s_dbm,
        "J_dbm": j_dbm,
        "JS_db": js,
        "spare_db": bt.spare_db,
        "distance_factor": bt.distance_factor,
        "pilot_burn_through_km": bt.signal_distance_to_burn_through_km(3),
        "jammer_standoff_km": bt.jammer_standoff_km(1),
    }


def gnss_jammer_10km():
    """1 W, 0 dBi jammer 10 km from a GPS L1 receiver at the -128.5 dBm minimum signal; 30 dB lock-loss assumption."""
    g = gnss_js(jammer_power_dbm=30, jammer_gain_dbi=0, dist_km=10, lock_loss_js_db=30)
    horizon = radio_horizon_km(2, 100)
    return {
        "fspl_db": g.fspl_db,
        "J_dbm": g.jammer_rx_dbm,
        "JS_db": g.js_db,
        "spare_db": g.spare_db,
        "denial_range_km": g.denial_range_km(10),
        "horizon_km_2m_100m": horizon,
    }


def all_examples() -> dict:
    vb = video_link_5km()
    r5 = vb.evaluate()
    r10 = LinkBudget(**{**vb.__dict__, "dist_km": 10}).evaluate()
    return {
        "wavelength_2g4_m": wavelength_m(2.4e9),
        "wavelength_L1_m": wavelength_m(1575.42e6),
        "fspl_2g4_5km_db": fspl_db(5, 2400),
        "fspl_5g8_5km_db": fspl_db(5, 5800),
        "gain_30x30_ideal_dbi": gain_from_beamwidth_dbi(30, 30, practical=False),
        "gain_30x30_practical_dbi": gain_from_beamwidth_dbi(30, 30),
        "horizon_2m_100m_km": radio_horizon_km(2, 100),
        "fresnel_2g4_2km_mid_m": fresnel_radius_m(2, 2.4),
        "link_5km": r5,
        "link_10km": r10,
        "uplink_jamming": uplink_jamming(),
        "gnss_10km": gnss_jammer_10km(),
    }
