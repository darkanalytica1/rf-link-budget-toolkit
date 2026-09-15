"""Every worked example quoted in the README and docs is reproduced here."""
import math

import pytest

from rflink import (
    LinkBudget, burn_through, comms_js_db, fresnel_radius_m, fspl_db, gain_from_beamwidth_dbi,
    gnss_js, noise_floor_dbm, radio_horizon_km, range_factor, shannon_capacity_bps, wavelength_m,
)
from rflink import examples


def test_wavelengths():
    assert wavelength_m(2.4e9) == pytest.approx(0.125, abs=1e-3)
    assert wavelength_m(5.8e9) == pytest.approx(0.052, abs=1e-3)
    assert wavelength_m(1575.42e6) == pytest.approx(0.190, abs=1e-3)


def test_fspl_2g4_5km():
    assert fspl_db(5, 2400) == pytest.approx(114.0, abs=0.05)


def test_fspl_doubling_and_frequency_scaling():
    assert fspl_db(10, 2400) - fspl_db(5, 2400) == pytest.approx(6.02, abs=0.01)
    assert fspl_db(5, 5800) == pytest.approx(121.7, abs=0.05)


def test_six_db_doubles_range():
    assert range_factor(6.0206) == pytest.approx(2.0, abs=1e-3)
    assert range_factor(20) == pytest.approx(10.0)


def test_gain_from_beamwidth():
    assert gain_from_beamwidth_dbi(30, 30, practical=False) == pytest.approx(16.6, abs=0.05)
    assert gain_from_beamwidth_dbi(30, 30) == pytest.approx(15.2, abs=0.05)


def test_radio_horizon():
    assert radio_horizon_km(2, 100) == pytest.approx(47.0, abs=0.1)


def test_fresnel_mid_path():
    assert fresnel_radius_m(2, 2.4) == pytest.approx(7.9, abs=0.05)


def test_noise_floor():
    assert noise_floor_dbm(20e6, 6) == pytest.approx(-95.0, abs=0.05)
    # GPS L1 C/A in its 2.046 MHz bandwidth, NF 0
    assert noise_floor_dbm(2.046e6) == pytest.approx(-110.9, abs=0.05)
    # 3 dB per bandwidth doubling
    assert noise_floor_dbm(80e6) - noise_floor_dbm(20e6) == pytest.approx(6.02, abs=0.01)


def test_link_budget_5km():
    r = examples.video_link_5km().evaluate()
    assert r.rx_power_dbm == pytest.approx(-84.0, abs=0.05)
    assert r.snr_db == pytest.approx(11.0, abs=0.05)
    assert r.margin_db == pytest.approx(3.0, abs=0.05)
    assert r.closes
    assert r.capacity_bps / 1e6 == pytest.approx(75, abs=1)


def test_link_budget_10km_fails():
    lb = examples.video_link_5km()
    r = LinkBudget(**{**lb.__dict__, "dist_km": 10}).evaluate()
    assert r.snr_db == pytest.approx(5.0, abs=0.1)
    assert not r.closes


def test_uplink_jamming_example():
    u = examples.uplink_jamming()
    assert u["S_dbm"] == pytest.approx(-87.6, abs=0.05)
    assert u["J_dbm"] == pytest.approx(-54.1, abs=0.1)
    assert u["JS_db"] == pytest.approx(33.5, abs=0.05)
    # consistency: formula equals difference of absolute powers
    assert u["J_dbm"] - u["S_dbm"] == pytest.approx(u["JS_db"], abs=0.01)
    assert u["distance_factor"] == pytest.approx(15.0, abs=0.1)
    assert u["pilot_burn_through_km"] * 1000 == pytest.approx(200, abs=2)
    assert u["jammer_standoff_km"] == pytest.approx(15.0, abs=0.1)


def test_bandwidth_term_only_when_jammer_wider():
    narrow = comms_js_db(40, 0, 20, 0, 1, 1, rx_bandwidth_hz=20e6, jammer_bandwidth_hz=10e6)
    assert narrow == pytest.approx(20.0)


def test_gnss_jammer_10km():
    g = examples.gnss_jammer_10km()
    assert g["fspl_db"] == pytest.approx(116.4, abs=0.05)
    assert g["J_dbm"] == pytest.approx(-86.4, abs=0.05)
    assert g["JS_db"] == pytest.approx(42.1, abs=0.05)
    assert g["denial_range_km"] == pytest.approx(40.3, abs=0.2)
    assert g["horizon_km_2m_100m"] == pytest.approx(47.0, abs=0.1)


def test_gnss_js_plus_20db_per_decade():
    near = gnss_js(30, 0, 1).js_db
    far = gnss_js(30, 0, 10).js_db
    assert near - far == pytest.approx(20.0)


def test_denial_range_capped_by_horizon():
    g = gnss_js(30, 0, 10, lock_loss_js_db=20)
    assert g.denial_range_km(10, horizon_km=47) == 47


def test_burn_through_sign():
    bt = burn_through(5.0, 10.0)
    assert bt.spare_db == -5.0
    assert bt.jammer_standoff_km(1) < 1


def test_shannon_zero_db():
    assert shannon_capacity_bps(1e6, 0) == pytest.approx(1e6)


@pytest.mark.parametrize("fn,args", [
    (fspl_db, (0, 2400)), (wavelength_m, (0,)), (noise_floor_dbm, (0,)),
    (radio_horizon_km, (-1,)), (fresnel_radius_m, (2, 2.4, 3)), (gain_from_beamwidth_dbi, (0, 10)),
])
def test_invalid_inputs(fn, args):
    with pytest.raises(ValueError):
        fn(*args)
