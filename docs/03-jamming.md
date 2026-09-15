# 03 · Jamming: J/S ratio and burn-through

`ASSESSMENT` Jamming is decided by the ratio of jamming to wanted power **at the victim receiver**. Transmitter watts matter only through that ratio, which geometry, antenna gain and bandwidth shape at least as much as power does.

## 3.1 Which receiver is being jammed?

A drone system has at least two receivers worth attacking, and they sit in different places:

- **The drone's command uplink receiver.** The jammer must reach the drone. The wanted signal comes from the pilot.
- **The pilot's video or telemetry receiver.** The jammer must reach the pilot. The wanted signal comes from the drone.

Swapping them changes every distance in the calculation. Always state which one you mean.

## 3.2 Communications J/S

$$\frac{J}{S}\,(\text{dB}) = (P_j + G_j + G_{rj}) - (P_t + G_t + G_{rt}) + 20\log_{10}\frac{d_s}{d_j} + 10\log_{10}\frac{B_r}{B_j}$$

| Symbol | Meaning |
|---|---|
| $P_j$, $P_t$ | jammer and wanted transmitter power (dBm) |
| $G_j$, $G_t$ | their antenna gains toward the victim (dBi) |
| $G_{rj}$, $G_{rt}$ | victim antenna gain toward the jammer and toward the wanted transmitter (dBi) |
| $d_s$, $d_j$ | wanted-transmitter and jammer distances to the victim |
| $B_r$, $B_j$ | victim receiver and jammer bandwidths; the term applies only when $B_j > B_r$ |

The distance term comes from FSPL on both paths at the same frequency: the frequency terms cancel and only the ratio of distances remains.

## 3.3 Worked example

![Jamming geometry](../assets/jamming-geometry.svg)

Drone 3 km from its pilot, jammer 1 km from the drone, 2.4 GHz. Pilot 20 dBm into 2 dBi. Jammer 40 dBm (10 W) into 12 dBi, spread over 80 MHz. Victim receiver 20 MHz, 0 dBi antenna.

Absolute powers at the drone:

- $S = 22 - \text{FSPL}(3\text{ km}) = 22 - 109.6 = -87.6$ dBm
- $J = 52 - \text{FSPL}(1\text{ km}) - 6.0 = 52 - 100.0 - 6.0 = -54.1$ dBm

Formula: $30 + 9.5 - 6.0 = 33.5$ dB. Both routes agree, which is a useful self-check.

```python
from rflink import comms_js_db, burn_through
js = comms_js_db(jammer_power_dbm=40, jammer_gain_dbi=12, tx_power_dbm=20, tx_gain_dbi=2,
                 dist_signal_km=3, dist_jammer_km=1, rx_bandwidth_hz=20e6, jammer_bandwidth_hz=80e6)
bt = burn_through(js, js_required_db=10)
bt.signal_distance_to_burn_through_km(3)   # 0.200
bt.jammer_standoff_km(1)                   # 15.0
```

## 3.4 Burn-through

If this link fails above about 10 dB J/S (an illustrative figure; it depends on the waveform), there is 23.5 dB to spare. In free space that is a distance factor of $10^{23.5/20} \approx 15$:

- the pilot would have to come within about **200 m** of the drone to restore the link, or
- the jammer could stand off to about **15 km**, if it keeps line of sight.

**Radar is different.** Radar burn-through is the range at which the target echo, which grows as $R^{-4}$ as the radar closes, overtakes a self-screening jammer whose power grows only as $R^{-2}$. For communications both paths are one-way, so the balance moves with the ratio of distances, not a power of range.

## 3.5 What jamming does and does not do

- Barrage, spot, swept, partial-band, pulsed and follower jamming spread power differently in time and frequency; J/S is computed per technique over the victim's bandwidth.
- Frequency hopping forces a jammer to dilute power or chase hops. It raises the cost of jamming. It does not remove the emission, and it does not prevent direction finding.
- A jammed control link usually triggers the drone's failsafe (hover, land or return). A drone flying a pre-programmed route, or one that is not listening, is unaffected by command-link jamming.

## Assumptions and limits

- Both paths free space at the same frequency, line of sight, no multipath.
- The J/S a receiver tolerates is waveform-, coding- and implementation-dependent. Use measured values where they exist.
- Jammer duty cycle, polarisation mismatch and antenna pointing errors are not modelled.
- Operating a jammer is regulated. In most jurisdictions only specifically authorised bodies may do so. This repository is a calculator for understanding, not operational guidance.
