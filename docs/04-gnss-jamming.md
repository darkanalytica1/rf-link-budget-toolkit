# 04 · GNSS jamming at distance

Satellite navigation signals arrive weaker than the thermal noise in their own bandwidth. That single fact explains why low-power jammers deny large areas.

## 4.1 How weak is GNSS?

- Minimum received GPS L1 C/A power at the Earth's surface: **−158.5 dBW = −128.5 dBm** (IS-GPS-200).
- Thermal noise in the 2.046 MHz C/A main-lobe bandwidth: $-174 + 10\log_{10}(2.046\times10^6) = -110.9$ dBm.
- The signal is therefore about 18 dB **below** noise. Correlation against the known spreading code recovers it, giving a nominal carrier-to-noise density $C/N_0$ near 45 dB-Hz for an unobstructed sky.

## 4.2 Jammer J/S at a receiver

$$J = P_j + G_j - \text{FSPL}(d_j, f), \qquad \frac{J}{S} = J - S_{GNSS}$$

$$d_{max} = d \cdot 10^{(J/S - J/S_{lock})/20}$$

Each 20 dB of spare J/S multiplies the denial distance by ten, up to the radio horizon.

## 4.3 Worked example

A 1 W (30 dBm) jammer with a 0 dBi antenna, 10 km from a drone, GPS L1:

| Quantity | Value |
|---|---|
| FSPL at 10 km, 1575.42 MHz | $20 + 63.95 + 32.44 = 116.4$ dB |
| Jamming at the receiver | $30 - 116.4 = -86.4$ dBm |
| J/S against −128.5 dBm | **42.1 dB** |
| Lock-loss planning assumption | 30 dB J/S |
| Spare | 12.1 dB, a distance factor of about 4 |
| Free-space denial distance | about **40 km** |
| Radio horizon, jammer at 2 m, drone at 100 m | 47 km |

```python
from rflink import gnss_js, radio_horizon_km
g = gnss_js(jammer_power_dbm=30, jammer_gain_dbi=0, dist_km=10, lock_loss_js_db=30)
g.js_db                                             # 42.11
g.denial_range_km(10, horizon_km=radio_horizon_km(2, 100))   # 40.33
```

## 4.4 Honest failure and dangerous failure

**Jamming** is the honest failure: the receiver reports that it has no fix, and a well-designed flight controller knows it has lost GNSS and can switch to a fallback. **Spoofing** is the dangerous one: counterfeit signals produce a plausible, wrong position and time that nothing downstream questions. J/S arithmetic tells you how far jamming reaches; it says nothing about whether a receiver can be deceived. For the estimator side of that problem, see the companion repository [gnss-denied-navigation-primer](https://github.com/darkanalytica1/gnss-denied-navigation-primer).

## 4.5 Mitigations, in engineering terms

| Mitigation | What it changes in the equation |
|---|---|
| Controlled reception pattern antenna (CRPA) | Reduces $G_{rj}$ toward the jammer by placing nulls; an $N$-element array nulls up to $N-1$ directions |
| Antenna placement and ground plane shielding | Reduces gain toward low-elevation, ground-based jammers |
| Inertial and visual aiding | Lets tracking loops survive a higher J/S and bridges outages |
| Multi-constellation, multi-frequency receivers | Forces the jammer to cover more bands |
| GNSS-independent navigation | Removes the dependency; J/S no longer decides navigation |

## Assumptions and limits

- The lock-loss J/S is a **planning assumption**, not a constant of nature. Published figures for unaided civil receivers vary widely with receiver design, tracking loop bandwidth, aiding and antenna; treat 30 dB as a placeholder and substitute measured values.
- The received GNSS power used is the specification minimum; real signals are often 2 to 5 dB stronger, which slightly shortens denial distance.
- Free space and line of sight only. Terrain and the receiving antenna's low gain toward the horizon usually reduce real jamming effect at long range.
- Transmitting in GNSS bands without authorisation is illegal in most jurisdictions and endangers aviation and timing users.
