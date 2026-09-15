# 02 · Link budget, noise floor and SNR

A link budget is bookkeeping: gains added, losses subtracted, and the result compared with the noise the receiver cannot avoid. Any range claim that does not come with these numbers cannot be checked.

## 2.1 The equations

$$P_r = P_t + G_t + G_r - L_{path} - L_{misc}$$

$$N = -174 + 10\log_{10}(B_{Hz}) + NF$$

$$\text{SNR} = P_r - N, \qquad \text{Margin} = \text{SNR} - \text{SNR}_{req}$$

| Symbol | Meaning | Unit |
|---|---|---|
| $P_t$, $P_r$ | transmitted and received power | dBm |
| $G_t$, $G_r$ | antenna gains toward each other | dBi |
| $L_{path}$ | path loss (FSPL here) | dB |
| $L_{misc}$ | cables, connectors, polarisation mismatch, body blockage | dB |
| $-174$ | thermal noise density $kT_0$ at 290 K | dBm/Hz |
| $B$ | receiver noise bandwidth | Hz |
| $NF$ | receiver noise figure | dB |
| $\text{SNR}_{req}$ | SNR the waveform needs at the target error rate | dB |

EIRP is $P_t + G_t$ minus feed losses. Regulatory limits and real reach are both set in EIRP.

## 2.2 Worked example: 2.4 GHz video downlink at 5 km

![Link budget waterfall](../assets/link-budget-waterfall.svg)

| Step | Value | Running level |
|---|---|---|
| Transmit power | +20 dBm | +20.0 dBm |
| Transmit antenna | +2 dBi | +22.0 dBm (EIRP) |
| Free-space loss, 5 km | −114.0 dB | −92.0 dBm |
| Receive antenna | +10 dBi | −82.0 dBm |
| Cable and misc | −2 dB | **−84.0 dBm** |
| Noise floor, 20 MHz, NF 6 dB | −174 + 73.0 + 6 | **−95.0 dBm** |
| SNR | | **11.0 dB** |
| Required SNR (illustrative) | 8 dB | margin **+3.0 dB** |

At 10 km the path loss grows by 6 dB, SNR falls to about 5 dB and the margin becomes −3 dB: the link fails. The Shannon bound at 11 dB SNR over 20 MHz is $20 \times \log_2(1 + 12.6) \approx 75$ Mbit/s, an upper limit no real modem reaches.

```python
from rflink import LinkBudget
lb = LinkBudget(freq_mhz=2400, dist_km=5, tx_power_dbm=20, tx_gain_dbi=2, rx_gain_dbi=10,
                bandwidth_hz=20e6, noise_figure_db=6, misc_loss_db=2, required_snr_db=8)
print(lb.evaluate().as_text())
```

## 2.3 The noise trap

The floor rises 3 dB for every doubling of bandwidth. A detector watching 80 MHz instead of 20 MHz has a floor 6 dB higher, which halves its free-space range against the same emitter. In a city, the effective floor is set by other emitters, not by thermal noise, and it is higher still. This is why "HD video costs range" and why wideband detectors quote shorter ranges than their narrowband equivalents.

## 2.4 Reading a range claim

Ask for the inputs, not the output:

1. Transmit power and antenna gain on both ends (or EIRP).
2. Receiver bandwidth and noise figure.
3. The SNR the waveform needs, and at what error or frame-loss rate.
4. Heights of both antennas and whether the path had first Fresnel zone clearance.
5. The noise environment where the range was measured.

## Assumptions and limits

- Free space only: add terrain, foliage and body loss to `extra_path_loss_db` when you have a justified number.
- The required SNR depends on modulation, coding and acceptable error rate; the 8 dB in the example is illustrative.
- Noise floor assumes thermal noise at 290 K; interference is not modelled.
- The Shannon capacity is a theoretical bound, not a throughput prediction.
