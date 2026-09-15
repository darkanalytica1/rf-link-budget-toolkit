"""rflink: small, dependency-free RF link budget and jamming geometry calculations."""
from .budget import (
    THERMAL_NOISE_DBM_HZ,
    LinkBudget,
    LinkResult,
    dbm_to_w,
    eirp_dbm,
    noise_floor_dbm,
    shannon_capacity_bps,
    w_to_dbm,
)
from .jamming import (
    GPS_L1_MHZ,
    GPS_L1_MIN_RX_DBM,
    burn_through,
    comms_js_db,
    gnss_js,
)
from .propagation import (
    fresnel_radius_m,
    fspl_db,
    gain_from_beamwidth_dbi,
    radio_horizon_km,
    range_factor,
    range_for_loss_km,
    wavelength_m,
)

__all__ = [
    "THERMAL_NOISE_DBM_HZ", "LinkBudget", "LinkResult", "dbm_to_w", "eirp_dbm", "noise_floor_dbm",
    "shannon_capacity_bps", "w_to_dbm", "GPS_L1_MHZ", "GPS_L1_MIN_RX_DBM", "burn_through",
    "comms_js_db", "gnss_js", "fresnel_radius_m", "fspl_db", "gain_from_beamwidth_dbi",
    "radio_horizon_km", "range_factor", "range_for_loss_km", "wavelength_m",
]
__version__ = "0.1.0"
