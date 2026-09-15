# 01 · Propagation: wavelength, free-space loss, gain and line of sight

`METHOD` Every quantity below is a screening estimate for a clear line-of-sight path. It bounds what is physically possible; it does not predict a measured result on real terrain.

## 1.1 Wavelength and bands

$$\lambda = \frac{c}{f}, \qquad c \approx 3 \times 10^8\ \text{m/s}$$

| Signal | Frequency | Wavelength |
|---|---|---|
| Common control and video link | 2.4 GHz | 0.125 m |
| Common video link | 5.8 GHz | 0.052 m |
| GPS L1 / Galileo E1 | 1575.42 MHz | 0.190 m |

Lower frequencies diffract around obstacles and penetrate foliage better but need larger antennas and give less bandwidth. Higher frequencies give bandwidth and compact high-gain antennas but suffer more blockage. The first question for any detector or jammer is "which bands, at what bandwidth". "All common drone frequencies" is not an answer.

```python
from rflink import wavelength_m
wavelength_m(2.4e9)   # 0.1249 m
```

## 1.2 Free-space path loss (FSPL)

$$\text{FSPL(dB)} = 20\log_{10}(d_{km}) + 20\log_{10}(f_{MHz}) + 32.44$$

The constant is $20\log_{10}(4\pi \cdot 10^9 / c)$ for distance in km and frequency in MHz. The loss is between two isotropic antennas; the frequency term exists because an isotropic antenna's capture area shrinks with wavelength, not because air absorbs higher frequencies.

**Worked example.** 2.4 GHz over 5 km: $13.98 + 67.60 + 32.44 = 114.0$ dB. Double the distance and the loss rises by 6.02 dB. The same path at 5.8 GHz costs $20\log_{10}(5800/2400) = 7.66$ dB more: 121.7 dB.

**Rules of thumb.** 6 dB of extra budget doubles free-space range. 20 dB multiplies it by ten.

```python
from rflink import fspl_db, range_factor
fspl_db(5, 2400)     # 114.02
range_factor(6.02)   # 2.0
```

## 1.3 Antenna gain and beamwidth

$$G \approx \frac{41{,}253}{\theta_{az}\,\theta_{el}}\ \text{(ideal)}, \qquad G \approx \frac{30{,}000}{\theta_{az}\,\theta_{el}}\ \text{(practical)}$$

Beamwidths are half-power angles in degrees. A 30° by 30° patch gives 16.6 dBi ideal and about 15.2 dBi in practice. The aperture form $G = 4\pi A_e / \lambda^2$ explains why the same dish gains more at higher frequency.

Receive gain counts exactly as much as transmit gain: 10 dBi on receive is worth ten times the transmitter power. Compare equipment on EIRP and receive gain, never on transmitter watts alone.

## 1.4 Radio horizon

$$d_{km} \approx 4.12\left(\sqrt{h_1} + \sqrt{h_2}\right)$$

Heights in metres, smooth Earth, standard refraction (effective Earth radius factor $k = 4/3$). A 2 m ground antenna and a drone at 100 m: $4.12(1.41 + 10) = 47$ km. A drone at 30 m and an operator at 1.5 m: about 27.6 km. Terrain shields low drones from detectors and jammers alike.

## 1.5 Fresnel zone clearance

$$r_n = 17.32\sqrt{\frac{n\,d_1\,d_2}{f_{GHz}\,d}}\ \text{m}, \qquad r_1^{mid} = 17.32\sqrt{\frac{d}{4 f_{GHz}}}\ \text{m}$$

Distances in km. At 2.4 GHz over 2 km the first Fresnel zone at mid-path has a radius of 7.9 m. A controller held at 1.5 m over flat ground intrudes into that zone, so real loss exceeds FSPL even with visual line of sight. A common planning rule keeps at least 60 % of the first zone clear.

```python
from rflink import radio_horizon_km, fresnel_radius_m
radio_horizon_km(2, 100)     # 47.03
fresnel_radius_m(2, 2.4)     # 7.91
```

## Assumptions and limits

- Far field, single direct path, no multipath, no diffraction, no foliage or building loss (see ITU-R P.526 and P.833 for those).
- Horizon uses a smooth sphere with $k = 4/3$. Anomalous propagation (ducting) can extend it, terrain shortens it.
- Gain-from-beamwidth is an approximation for a single main lobe; it does not replace a measured pattern.
