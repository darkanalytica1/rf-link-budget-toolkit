# Sources

All formulas below are standard and public. The worked examples and the code are original; the numbers in them were computed by the author from the stated inputs and are reproduced by `tests/test_worked_examples.py`. No measured result from any organisation is used.

## Standards and specifications

1. ITU-R Recommendation P.525, *Calculation of free-space attenuation*. Free-space path loss.
2. ITU-R Recommendation P.526, *Propagation by diffraction*. Fresnel zones and obstruction loss.
3. ITU-R Recommendation P.453, *The radio refractive index: its formula and refractivity data*. Effective Earth radius and the $k = 4/3$ convention.
4. IS-GPS-200, *Navstar GPS Space Segment / Navigation User Segment Interfaces*. L1 carrier frequency and minimum received C/A power (−158.5 dBW).
5. European GNSS (Galileo) Open Service Signal-In-Space Interface Control Document. E1, E5a, E5b and E6 carrier frequencies.
6. IEEE Std 521, *Standard Letter Designations for Radar-Frequency Bands*.

## Textbooks and papers

7. H. T. Friis, "A Note on a Simple Transmission Formula", *Proceedings of the IRE*, 34(5), 1946. The transmission equation.
8. C. A. Balanis, *Antenna Theory: Analysis and Design*, 4th ed., Wiley, 2016. Gain, beamwidth and effective aperture.
9. B. Sklar, *Digital Communications: Fundamentals and Applications*, 2nd ed., Prentice Hall, 2001. Link budgets, noise figure, required SNR.
10. C. E. Shannon, "A Mathematical Theory of Communication", *Bell System Technical Journal*, 27, 1948. Channel capacity.
11. D. Adamy, *EW 101: A First Course in Electronic Warfare* and *EW 102: A Second Course in Electronic Warfare*, Artech House. J/S, burn-through, one-way and two-way link geometry.
12. R. A. Poisel, *Modern Communications Jamming Principles and Techniques*, 2nd ed., Artech House, 2011. Communications jamming techniques and J/S.
13. E. D. Kaplan and C. J. Hegarty (eds.), *Understanding GPS/GNSS: Principles and Applications*, 3rd ed., Artech House, 2017. Signal power, $C/N_0$, processing gain, interference effects.
14. P. D. Groves, *Principles of GNSS, Inertial, and Multisensor Integrated Navigation Systems*, 2nd ed., Artech House, 2013. Interference, CRPA and aiding.
15. M. L. Psiaki and T. E. Humphreys, "GNSS Spoofing and Detection", *Proceedings of the IEEE*, 104(6), 2016. Jamming versus spoofing.

## Confidence

| Claim type | Confidence | Why |
|---|---|---|
| Formulas and constants | High | Standards and canonical textbooks |
| Worked-example arithmetic | High | Reproduced by unit tests |
| Required SNR (8 dB) and link-failure J/S (10 dB) | Illustrative | Waveform-dependent; chosen to teach the method |
| GNSS lock-loss J/S (30 dB) | Low, planning only | Receiver-dependent; substitute measured values |
