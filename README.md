[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.19210748.svg)](https://doi.org/10.5281/zenodo.19210748)
![Visitors Badge](https://visitor-badge.laobi.icu/badge?page_id=RuiGao9/pySAFER-123)
# pySAFER: A Python Toolkit for the Simple Algorithm For actual Evapotranspiration Retrieving
This toolkit is designed to streamline $ET_a$ estimation using the Simple Algorithm for Evapotranspiration Retrieving (SAFER). Whether you are working with station-based point data or satellite-derived imagery, `pySAFER` provides the necessary workflows to quantify water loss.
This repository is structured to help you:
- **Apply the Model:** Follow hands-on tutorials to run $ET_a$ estimations using your own datasets.
- **Understand the Science:** Explore the core concepts and mathematical logic that drive the SAFER framework.

## Model Installation
```bash
pip install "git+https://github.com/RuiGao9/pySAFER.git" 
```

## Model Inputs
- **Albedo ($\alpha_0$):** The ratio between reflected and incident sunlight. A general method to get the $\alpha_0$ has two steps:
  - **$\alpha_P$ calculation:** $\alpha_P$ is the albedo for the visible and infrared partition of the electromagnetic spectrum. $w_{band}$ represents different narrow-band reflectances. $w_{band}$ represents weights for each band. The weights for the different bands was computed as the ration of the amount of the incoming shortwave radiation from the sum in each band and the sum of incoming shortwave radiation from the sum in each band and the sum of incoming shortwave radiation for the bands at the top of the atmosphere (TOA).
  
$$\alpha_P=\sum{w_{band} \cdot r_{band}}$$

<div align="center">
  <figure>
    <img src="Figures/weights.png" alt="weights" width="35%" />
      <p><i>One case from the paper called agriwater: An R package for spatial modelling of energy balance and actual evapotranspiration using satellite images and agrometeorological data</i></p>
  </figure>
</div>

  - **$\alpha_0$:** the daily $\alpha_0$ is then obtained by:
  
  $$\alpha_0=b\cdot \alpha_P+c$$

## Running the Model
The easiest way to get started is by exploring the provided Jupyter Notebook: `pySAFER_Run.ipynb`. This notebook serves as a comprehensive template that demonstrates the end-to-end workflow:
- **Environment Setup:** How to properly import the pySAFER library and its core modules.
- **Data Ingestion:** Loading and preprocessing the included demo datasets (e.g., `point_samples.txt`).
- **Core Computations:** Step-by-step execution of the SAFER algorithm, including:
  - Vegetation indices (NDVI)
  - Extraterrestrial radiation ($R_a$)
  - Surface solar radiation ($R_s$) using both observed and estimated (Hargreaves) methods.
- **Results & Visualization:** Generating $ET_a$ estimates and validating them with built-in plotting tools.

```python

```

# SAFER Concepts
## Model Flowchart
  <div align="center">
    <figure>
      <img src="Figures/energy_balance.png" alt="weights" width="35%" />
      <p><i>Energy balance model described by Silva, et al. (2019).</i></p>
    </figure>
  </div>

## Physical Principles and Govering Equations of SAFER
### Extraterrestrial radiation ($R_a$, $MJ \cdot m^{-2} \cdot day$)
A physical upper limit calculation, where the equation could be found in [Torres-Rua et al., (2011)](https://www.sciencedirect.com/science/article/pii/S0378377410003331). Two required inputs are:
- Latitude (radians)
- DOY (day of year)

$$R_a=\frac{37.6 \cdot d_r \cdot [w_s \cdot sin(\phi_l)sin(\delta) + cos(\phi_l) \cdot sin(w_s)]}{\lambda}$$
$$\delta = 0.4093 \cdot sin(\frac{2 \pi (284+DOY)}{365})$$
$$d_r = 1 + 0.033 \cdot cos(\frac{2 \pi \cdot DOY}{365})$$
$$w_s = cos(tan(\phi_l) \cdot tan(\delta))$$

where:
- $d_r$: Relative distance from the earth to the sun, dimensionless.
- $DOY$: Day of the year.
- $w_s$: Sunset hour angle, radians.
- $\phi_l$: Latitude, radians.
- $\delta$: Declination of the sun, radians. 
- $\lambda$: Latent heat of vvaporization, $\lambda=2.54~MJ/kg$

### Incoming solar radiation ($R_s$, $MJ \cdot m^{-2} \cdot day$)
This can be either measured by sensors or estimated by the equation from [Hargreaves et al., (2003)](https://ascelibrary.org/doi/10.1061/%28ASCE%290733-9437%282003%29129%3A1%2853%29). Three required inputs are:
- Extraterrestrial radiation ($MJ \cdot m^{-2} \cdot day$), estimated from above
- The mean maximum air temperature ($\degree C$)
- The mean minimum air temperature ($\degree C$)
- 
$$R_s=K_{RS} \cdot R_a \cdot \sqrt{T_{max}-T_{min}}$$

where the $K_{RS}$ is the empirical coefficient fitted to $R_s/R_a$ versus $\sqrt{T_{max}-T_{min}}$ data. $K_{RS}$ = 0.19 for coastal area; $K_{RS}$ = 0.16 for inner land.

### Albedo ($\alpha_0$)
Albedo will be obtained based on remote sensing (spectral) image data. Methods vary, and one method based on the reflectand in red ($\rho_{Red}$) and near-infrared ($\rho_{NIR}$).

$$\alpha_0=0.08 + 0.41 \times \rho_{Red}+ 0.14 \times \rho_{NIR}$$


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


$$LST=({\frac{R_{s24}-\alpha_0 \cdot R_{s24} + \epsilon_A \cdot \sigma \cdot T_a^4 - R_n}{\epsilon_s \cdot \sigma}})^{0.25}$$
- $T_a:$ average air temperature ($\degree C$)


# Reference
Silva, C. D. O. F., de Castro Teixeira, A. H., & Manzione, R. L. (2019). Agriwater: An R package for spatial modelling of energy balance and actual evapotranspiration using satellite images and agrometeorological data. Environmental modelling & software, 120, 104497. https://doi.org/10.1016/j.envsoft.2019.104497<br>
Teixeira, A. H. D. C., Padovani, C. R., Andrade, R. G., Leivas, J. F., Victoria, D. D. C., & Galdino, S. (2015). Use of MODIS images to quantify the radiation and energy balances in the Brazilian Pantanal. Remote Sensing, 7(11), 14597-14619. https://doi.org/10.3390/rs71114597<br>
Teixeira, A. H. D. C., Victoria, D. C., Andrade, R. G., Leivas, J. F., Bolfe, E. L., & Cruz, C. R. (2014, October). Coupling MODIS images and agrometeorological data for agricultural water productivity analyses in the Mato Grosso state, Brazil. In Remote Sensing for Agriculture, Ecosystems, and Hydrology XVI (Vol. 9239, pp. 278-291). SPIE. https://doi.org/10.1117/12.2065967<br>
Safre, A.L.S., Nassar, A., Torres-Rua, A. et al. Performance of Sentinel-2 SAFER ET model for daily and seasonal estimation of grapevine water consumption. Irrig Sci 40, 635–654 (2022). https://doi.org/10.1007/s00271-022-00810-1<br>
Task Committee on Revision of Manual 70. (2016, April). Evaporation, evapotranspiration, and irrigation water requirements. American Society of Civil Engineers. https://doi.org/10.1061/9780784414057<br>
Gao, R., Khan, M., & Viers, J. (2026). A Python Toolkit for Reference Evapotranspiration ($ET_o$) Calculation Directly from Pandas DataFrames (Initial). Zenodo. https://doi.org/10.5281/zenodo.19197914

## How to cite this work
Gao, R. (2026). pySAFER: A Python Toolkit for the Simple Algorithm for actual Evapotranspiration Retrieving (Initial). Zenodo. https://doi.org/10.5281/zenodo.19210748

## Repository update information
- Creation date: 2026-03-24
- Last update: 2026-03-24
- **Contact:** If you encounter any issues or have questions, please contact Rui Gao:
    - Rui.Ray.Gao@gmail.com
    - RuiGao@ucmerced.edu
