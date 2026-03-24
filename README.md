# pySAFER

# How To Use This Repository?

## Installation
```bash
pip install "git+https://github.com/RuiGao9/pySAFER.git" 
```

### Required inputs
- Satellite remote sensing inputs
  - **Normalized Difference Vegetation Index (NDVI):** Calculated from Red ($\rho_{Red}$) and Near-Infrared ($\rho_{NIR}$) bands
  - **Surface Albedo ($\alpha_0$):** Calculated using a weighted sum of multiple bi-directional reflectance bands (Visible and Shortwave).
- Agrometeorological inputs (Point data)
  - **Air temperature ($T_a$):** Daily average temperature ($\degree C$)
  - **Global solar radiation ($R_{s24}$):** Daily total incident shortwave radiation ($MJ/m^2/day$ or $W/m^2$).
  - **Reference evapotranspiration $ET_o$:** Daily depth ($mm/day$)
- Physical & empirical constants
  - **Regression coefficients ($a, b, c$):** Empirical values
  - **Day of year ($DOY$):** Used for the calculation of the inverse relative distance Earth-Sun and solar declination for radiation balance
  - **Geospatial metadata:** Station latitude and elevation (for atmospheric pressure and psychrometric constants)

### Extraterrestrial radiation ($$)
$$R_a=\frac{37.6 \cdot d_r \cdot [w_s \cdot sin(\phi_l)sin(\delta) + cos(\phi_l) \cdot sin(w_s)]}{\lambda}$$

$$\delta = 0.4093 \cdot sin(\frac{2 \pi (284+DOY)}{365})$$

$$d_r = 1 + 0.033 \cdot cos(\frac{2 \pi \cdot DOY}{365})$$

$$w_s = cos(tan(\phi_l) \cdot tan(\delta))$$

where:
- $d_r$: relative distance from the earth to the sun
- $DOY$: day of the year
- $w_s$: sunset hour angle (rad)
- $\phi_l$: latitude (rad)
- $\delta$: declination of the sun (rad) 
- $\lambda$: latent heat of vvaporization, $\lambda=2.54 MJ/kg$

$$LST={\frac{R_{s24}-\alpha_0 \cdot R_{s24} + \epsilon_A \cdot \sigma \cdot T_a^4 - R_n}{\epsilon_s \cdot \sigma}}^{0.25}$$
- $T_a:$ average air temperature ($\degree C$)

![alt text](Figures/SAFER-Workflow.png)
# Reference
Safre, A.L.S., Nassar, A., Torres-Rua, A. et al. Performance of Sentinel-2 SAFER ET model for daily and seasonal estimation of grapevine water consumption. Irrig Sci 40, 635–654 (2022). https://doi.org/10.1007/s00271-022-00810-1<br>
Gao, R., Khan, M., & Viers, J. (2026). A Python Toolkit for Reference Evapotranspiration ($ET_o$) Calculation Directly from Pandas DataFrames (Initial). Zenodo. https://doi.org/10.5281/zenodo.19197914