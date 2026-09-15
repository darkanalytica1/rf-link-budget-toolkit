"""Command-line interface: python -m rflink <command> [options]."""
from __future__ import annotations

import argparse
import sys

from . import examples
from .budget import LinkBudget, noise_floor_dbm
from .jamming import burn_through, comms_js_db, gnss_js
from .propagation import fresnel_radius_m, fspl_db, gain_from_beamwidth_dbi, radio_horizon_km, wavelength_m


def _p(label: str, value: float, unit: str, digits: int = 2) -> None:
    print(f"{label:<31} {value:10.{digits}f} {unit}")


def cmd_examples(_a) -> None:
    ex = examples.all_examples()
    print("Worked examples (free space, stated assumptions in docs/)\n")
    _p("wavelength 2.4 GHz", ex["wavelength_2g4_m"], "m", 3)
    _p("wavelength GPS L1", ex["wavelength_L1_m"], "m", 3)
    _p("FSPL 2.4 GHz, 5 km", ex["fspl_2g4_5km_db"], "dB")
    _p("FSPL 5.8 GHz, 5 km", ex["fspl_5g8_5km_db"], "dB")
    _p("gain 30x30 deg (ideal)", ex["gain_30x30_ideal_dbi"], "dBi")
    _p("gain 30x30 deg (practical)", ex["gain_30x30_practical_dbi"], "dBi")
    _p("horizon 2 m to 100 m", ex["horizon_2m_100m_km"], "km")
    _p("Fresnel r1 2.4 GHz 2 km", ex["fresnel_2g4_2km_mid_m"], "m")
    print("\nVideo downlink, 2.4 GHz, 5 km")
    print(ex["link_5km"].as_text())
    print("\nSame link at 10 km")
    print(ex["link_10km"].as_text())
    u = ex["uplink_jamming"]
    print("\nUplink jamming geometry (pilot 3 km, jammer 1 km)")
    _p("S at drone", u["S_dbm"], "dBm")
    _p("J at drone", u["J_dbm"], "dBm")
    _p("J/S", u["JS_db"], "dB")
    _p("spare over 10 dB needed", u["spare_db"], "dB")
    _p("pilot burn-through distance", u["pilot_burn_through_km"] * 1000, "m")
    _p("jammer standoff (LOS)", u["jammer_standoff_km"], "km")
    g = ex["gnss_10km"]
    print("\nGNSS L1 jammer, 1 W, 10 km")
    _p("FSPL", g["fspl_db"], "dB")
    _p("J at receiver", g["J_dbm"], "dBm")
    _p("J/S vs -128.5 dBm", g["JS_db"], "dB")
    _p("denial range (30 dB lock loss)", g["denial_range_km"], "km")
    _p("radio horizon 2 m / 100 m", g["horizon_km_2m_100m"], "km")


def cmd_fspl(a) -> None:
    _p("FSPL", fspl_db(a.dist_km, a.freq_mhz), "dB")
    _p("wavelength", wavelength_m(a.freq_mhz * 1e6), "m", 3)


def cmd_link(a) -> None:
    lb = LinkBudget(
        freq_mhz=a.freq_mhz, dist_km=a.dist_km, tx_power_dbm=a.tx_dbm, tx_gain_dbi=a.tx_gain,
        rx_gain_dbi=a.rx_gain, bandwidth_hz=a.bw_hz, noise_figure_db=a.nf, misc_loss_db=a.misc,
        required_snr_db=a.req_snr,
    )
    print(lb.evaluate().as_text())


def cmd_noise(a) -> None:
    _p("noise floor", noise_floor_dbm(a.bw_hz, a.nf), "dBm")


def cmd_horizon(a) -> None:
    _p("radio horizon (k=4/3)", radio_horizon_km(a.h1, a.h2), "km")


def cmd_fresnel(a) -> None:
    _p("first Fresnel radius", fresnel_radius_m(a.dist_km, a.freq_ghz, a.d1_km), "m")


def cmd_gain(a) -> None:
    _p("gain (practical)", gain_from_beamwidth_dbi(a.az, a.el), "dBi")
    _p("gain (ideal)", gain_from_beamwidth_dbi(a.az, a.el, practical=False), "dBi")


def cmd_js(a) -> None:
    js = comms_js_db(a.jam_dbm, a.jam_gain, a.tx_dbm, a.tx_gain, a.ds_km, a.dj_km,
                     a.rx_gain_jam, a.rx_gain_tx, a.rx_bw_hz, a.jam_bw_hz)
    bt = burn_through(js, a.required)
    _p("J/S", js, "dB")
    _p("spare over required", bt.spare_db, "dB")
    _p("wanted tx burn-through dist", bt.signal_distance_to_burn_through_km(a.ds_km), "km")
    _p("jammer standoff", bt.jammer_standoff_km(a.dj_km), "km")


def cmd_gnss(a) -> None:
    g = gnss_js(a.jam_dbm, a.jam_gain, a.dist_km, a.freq_mhz, a.signal_dbm, a.lock_loss)
    _p("FSPL", g.fspl_db, "dB")
    _p("J at receiver", g.jammer_rx_dbm, "dBm")
    _p("J/S", g.js_db, "dB")
    _p("denial range", g.denial_range_km(a.dist_km), "km")


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="rflink", description="RF link budget and jamming geometry calculator.")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("examples", help="print every worked example").set_defaults(fn=cmd_examples)

    s = sub.add_parser("fspl", help="free-space path loss")
    s.add_argument("--freq-mhz", type=float, required=True)
    s.add_argument("--dist-km", type=float, required=True)
    s.set_defaults(fn=cmd_fspl)

    s = sub.add_parser("link", help="full link budget")
    s.add_argument("--freq-mhz", type=float, required=True)
    s.add_argument("--dist-km", type=float, required=True)
    s.add_argument("--tx-dbm", type=float, required=True)
    s.add_argument("--tx-gain", type=float, default=0.0)
    s.add_argument("--rx-gain", type=float, default=0.0)
    s.add_argument("--bw-hz", type=float, required=True)
    s.add_argument("--nf", type=float, default=6.0)
    s.add_argument("--misc", type=float, default=0.0)
    s.add_argument("--req-snr", type=float, default=0.0)
    s.set_defaults(fn=cmd_link)

    s = sub.add_parser("noise", help="thermal noise floor")
    s.add_argument("--bw-hz", type=float, required=True)
    s.add_argument("--nf", type=float, default=0.0)
    s.set_defaults(fn=cmd_noise)

    s = sub.add_parser("horizon", help="radio horizon, k = 4/3")
    s.add_argument("--h1", type=float, required=True, help="height 1 (m)")
    s.add_argument("--h2", type=float, default=0.0, help="height 2 (m)")
    s.set_defaults(fn=cmd_horizon)

    s = sub.add_parser("fresnel", help="first Fresnel zone radius")
    s.add_argument("--dist-km", type=float, required=True)
    s.add_argument("--freq-ghz", type=float, required=True)
    s.add_argument("--d1-km", type=float, default=None)
    s.set_defaults(fn=cmd_fresnel)

    s = sub.add_parser("gain", help="antenna gain from beamwidths")
    s.add_argument("--az", type=float, required=True)
    s.add_argument("--el", type=float, required=True)
    s.set_defaults(fn=cmd_gain)

    s = sub.add_parser("js", help="communications J/S and burn-through")
    s.add_argument("--jam-dbm", type=float, required=True)
    s.add_argument("--jam-gain", type=float, default=0.0)
    s.add_argument("--tx-dbm", type=float, required=True)
    s.add_argument("--tx-gain", type=float, default=0.0)
    s.add_argument("--ds-km", type=float, required=True, help="wanted transmitter to receiver")
    s.add_argument("--dj-km", type=float, required=True, help="jammer to receiver")
    s.add_argument("--rx-gain-jam", type=float, default=0.0)
    s.add_argument("--rx-gain-tx", type=float, default=0.0)
    s.add_argument("--rx-bw-hz", type=float, default=None)
    s.add_argument("--jam-bw-hz", type=float, default=None)
    s.add_argument("--required", type=float, default=10.0, help="J/S at which the link fails (dB)")
    s.set_defaults(fn=cmd_js)

    s = sub.add_parser("gnss", help="GNSS jammer J/S and denial range")
    s.add_argument("--jam-dbm", type=float, required=True)
    s.add_argument("--jam-gain", type=float, default=0.0)
    s.add_argument("--dist-km", type=float, required=True)
    s.add_argument("--freq-mhz", type=float, default=1575.42)
    s.add_argument("--signal-dbm", type=float, default=-128.5)
    s.add_argument("--lock-loss", type=float, default=30.0)
    s.set_defaults(fn=cmd_gnss)
    return p


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    try:
        args.fn(args)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0
