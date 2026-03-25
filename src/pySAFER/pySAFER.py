import numpy as np
import warnings


### === === === === === ###
### Component 1
### Main process for net radiation and ground heat flux estimation
### === === === === === ###
## Step 1: Extraterrestrial radiation (Ra) calculation
def calc_ra(latitude, doy, year):
    """
    Calculate extraterrestrial radiation (Ra)
    Details about the calculation can follow the paper below:
    Torres, A. F., Walker, W. R., & McKee, M. (2011). 
    Forecasting daily potential evapotranspiration using machine learning and limited climatic data. 
    Agricultural Water Management, 98(4), 553-562.

    Inputs:
    latitude: latitude of the site
    doy: day of year
    year: calendar year

    return: 
    ra: extraterrestrial radiation in MJ/m2/day
    """
    # Convert latitude to radians
    lat_rad = np.radians(latitude)
    
    # Determine leap year and calculate days in the year
    is_leap = (year % 4 == 0) & ((year % 100 != 0) | (year % 400 == 0))
    days_in_year = np.where(is_leap, 366, 365)
    
    # 1. Declination of the sun
    ds = 0.409 * np.sin((2 * np.pi * doy / days_in_year) - 1.39)
    
    # 2. Relative distance earth-sun
    dr = 1 + 0.033 * np.cos(2 * np.pi * doy / days_in_year)
    
    # 3. Sunset hour angle
    # Correction: Use arccos directly and ensure the input is within the valid range
    tmp = -np.tan(lat_rad) * np.tan(ds)
    # Restrict the range to [-1, 1] to prevent numerical overflow resulting in nan
    tmp = np.clip(tmp, -1, 1)
    ws = np.arccos(tmp)
    
    # 4. Calculate Ra [MJ/(m^2 day)]
    # Constant 37.6 corresponds to Gsc = 0.0820 MJ/m2/min
    ra = (24 * 60 / np.pi) * 0.0820 * dr * (
        ws * np.sin(lat_rad) * np.sin(ds) + 
        np.cos(lat_rad) * np.cos(ds) * np.sin(ws)
    )
    return ra


## Step 2: Global solar radiation (Rs) at the surface
## Either measured or estimated
def calc_incoming_solar_radiation(ra, rs_obs=None, tmax=None, tmin=None, coastal=False):
    """
    Calculate the incoming solar radiation (Rs)
    The unit of the output is MJ/m2/day
    
    Logic of this function:
    1. if rs_obs (observation) is provided, use the observations directly
    2. if rs_obs is None, use Hargreaves's method for estimation
    
    parameters:
    ra: Extraterrestrial radaition (MJ/m2/day), calculated by function calc_ra 
    rs_obs: observations from the meteorological station (optional)
    rs_obs_unit: normally, the unit provided by the meteorological station is in W/m2
    tmax: the maximum air temperature (Celsius)
    tmin: the minimum air temperature (Celsius)
    coastal: if it is a coastal area (K_RS = 0.19 for coastal area; K_RS = 0.16 for inner land)
    """
    # Option 1: Use observation directly
    if rs_obs is not None:
        return np.asarray(rs_obs)
    
    # Option 2: Using Hargraves's method
    # Hargreaves, G. H., & Allen, R. G. (2003). 
    # History and evaluation of Hargreaves evapotranspiration equation. 
    # Journal of irrigation and drainage engineering, 
    # 129(1), 53-63.
    if tmax is not None and tmin is not None:
        k_rs = 0.19 if coastal else 0.16
        # Make sure the input is numpy array
        tmax = np.asarray(tmax)
        tmin = np.asarray(tmin)
        ra = np.asarray(ra)
        
        tdiff = np.maximum(tmax - tmin, 0)
        rs_est = k_rs * np.sqrt(tdiff) * ra
        return rs_est
    
    # Raise errors if needed inputs are missing
    raise ValueError("Either global solar radiation observations or"
                      "the extreme air temperature (Tmax and Tmin) need to be provided.")


## Step 3: Albedo (a0) calculation based on Red and NIR bands
def calc_albedo(red, nir, method='Teixeira_2015'):
    """
    Calculate albedo based on red and nir reflectance
    The reflectance value ranges between 0 and 1
    method can only pick from 'Teixeira_2015'
    """
    supported_methods = ['Teixeira_2015','Demo']
    if method not in supported_methods:
        raise ValueError(
            f"Error: '{method}' is not supported。 "
            f"Please find a method among {supported_methods}"
        )
    red = np.asarray(red)
    nir = np.asarray(nir)
    if method == 'Teixeira_2015':
        albedo = 0.08 + 0.41*red + 0.14*nir
    elif method == 'Demo': # Change this if a new method was found
        albedo = 0.07 + 0.40*red + 0.13*nir
    else:
        albedo = "None"

    # Put a physical value range for albedo (0.0 <= albedo <= 1.0)
    return np.clip(albedo, 0.0, 1.0)


# Step 4: Reflected global radiation (upwelling shortwave radiation) Rr
# If this is observed, use the observation directly
def calc_up_shortwave(rs_est, albedo, r_up_obs=None):
    """
    The unit of the output is MJ/m2/day

    ra: extraterrestrial radiation (Ra) 
    rs_est: incoming solar radiation (MJ/m2/day)
    albedo: a0
    r_up_obs: upwelling shortwave radiation observations in W/m2
    
    return
    r_reflect: reflected global radiation
    """
    if r_up_obs is not None:
        return np.asarray(r_up_obs)

    r_reflect = rs_est * albedo

    return r_reflect

# Step 5: Net radiation calculation (Rn)
def calc_r_net(rs_est, ra, albedo, tmax, tmin, 
               rn_obs=None, para_c=6.99, para_d=39.93):
    """
    The unit of the output is MJ/m2/day

    rs_est: global solar radiation (Rs), MJ/m2/day
    ra: extraterrestrial radiation (Ra), MJ/m2/day
    albedo
    tmax: maximum air temperature, Celsius 
    tmin: minimum air temperature, Celsius
    rn_obs: tell the function if the observation is available. If yes, the observation will be used directly
    para_c and para_d: empirical values from:
    Teixeira, A. H. D. C., Padovani, C. R., Andrade, R. G., Leivas, J. F., Victoria, D. D. C., & Galdino, S. (2015). 
    Use of MODIS images to quantify the radiation and energy balances in the Brazilian Pantanal. 
    Remote Sensing, 7(11), 14597-14619. 
    https://doi.org/10.3390/rs71114597
    """
    if rn_obs is not None:
        return np.asarray(rn_est)

    al = para_c * (tmax+tmin)/2 - para_d
    rn_est = (1 - albedo) * rs_est/0.0864 - al * (rs_est/ra)
    # Adjusting the unit from W/m2 to MJ/m2/day
    rn_est = rn_est * 0.0864

    return rn_est


# Step 6: Ground heat flux estimation/observation (G)
def calc_flux_g(rn_est, albedo, a_g=3.98, b_g=-25.47, g_obs=None):
    """
    Inputs:
    rn_est: either estimated or observed net radiation
    g_obs: if observation is provided, the unit should be W/m2

    return:
    flux_g: ground heat flux, MJ/m2/day
    """
    if g_obs is not None:
        return np.asarray(g_obs) * 0.0864
    
    g_est = (rn_est/0.0864 * a_g * np.exp(b_g * albedo)) * 0.0864

    return g_est


### === === === === === ###
### Component 2
### LST estimation and energy components estimation when NDVI > 0
### === === === === === ###
def calc_ndvi(red, nir):
    """
    Calculate NDVI
    Support inputs: single record, Pandas Series (columns) or NumPy array (image)
    
    parameters:
    red: reflectance of the red band (0-1)
    nir: reflectance of the near infrared band (0-1)
    
    return:
    ndvi: value ranges at [-1, 1]
    """
    # Covert input as numpy, make sure it could be calculated
    red = np.asarray(red)
    nir = np.asarray(nir)
    # Avoid 0 for the denominator 
    denominator = nir + red
    # Using np.where to process denominator whose value is 0, NaN for that situation
    ndvi = np.where(denominator != 0, (nir - red) / denominator, np.nan)
    
    return ndvi


def calc_flux_le_h(ndvi, albedo, rs_est, ra,
                   tmax, tmin,
                   rn_est, g_est,
                   eto=None,
                   p=None, elevation=None, 
                   para_as=0.06, para_bs=1.00, 
                   para_aa=0.94, para_ba=0.10,
                   para_a=1.8, para_b=-0.008,
                   sigma = 5.67e-8,
                   param_lambda=2.45,
                   epsilon=0.622,
                   cp=1.013e-3):
    """
    Inputs:
    ndvi:
    albedo:
    rs_est:
    ra:
    tmax and tmin: the unit is Celsius
    rn_est: net radiation, MJ/m2/day
    g_est: ground heat flux, MJ/m2/day
    eto: reference ET (mm/day) is obtained from another github repository called py-eto (https://github.com/RuiGao9/py-eto)
    cp: the specific heat of moist air, ~1.013e-3

    para_as and para_bs can refer to the paper below:
    Teixeira, A. H. D. C., Padovani, C. R., Andrade, R. G., Leivas, J. F., Victoria, D. D. C., & Galdino, S. (2015). 
    Use of MODIS images to quantify the radiation and energy balances in the Brazilian Pantanal. 
    Remote Sensing, 7(11), 14597-14619. 
    https://doi.org/10.3390/rs71114597
    
    para_a and para_b can refer to the paper below:
    Safre, A.L.S., Nassar, A., Torres-Rua, A. et al. 
    Performance of Sentinel-2 SAFER ET model for daily and seasonal estimation of grapevine water consumption. 
    Irrig Sci 40, 635–654 (2022). 
    https://doi.org/10.1007/s00271-022-00810-1

    returns:
    le_est: latent heat flux, MJ/m2/day
    h_est: sensible heat flux, MJ/m2/day
    """
    le_est = np.zeros_like(ndvi, dtype=float)
    h_est = np.zeros_like(ndvi, dtype=float)
    flux_avaliable = rn_est - g_est
    # Temperature is K
    ta_C = (tmax + tmin)/2
    ta_K = ta_C + 273.15

    # When NDVI > 0
    mask_veg = ndvi > 0
    if np.any(mask_veg):
        epsilon_a = para_aa * (-np.log(rs_est/ra))**para_ba
        epsilon_s = para_as * (np.log(ndvi)) + para_bs
        # LST calculation
        # Numerator
        numerator = rs_est/0.0864 - (albedo * rs_est/0.0864) + (epsilon_a * sigma * (ta_K**4)) - rn_est
        invalid_mask = numerator <= 0
        num_invalid = np.sum(invalid_mask)
        if num_invalid > 0:
            warnings.warn(
                f"{num_invalid} elements were below or equal to 0 during the LST estimation."
                f"This was forced to be 0.1 to make the model running!"
            )
        # Denominator
        denominator = epsilon_s * sigma

        # LST finanizing
        lst_K = (np.maximum(numerator, 0.1) / denominator)**0.25
        lst_C = lst_K - 273.15

        # Calculate 
        et_fr = np.exp(para_a + para_b * lst_C[mask_veg]/(albedo[mask_veg]*ndvi[mask_veg]))

        le_est[mask_veg] = (et_fr * eto[mask_veg])*param_lambda
        h_est[mask_veg] = rn_est[mask_veg] - g_est[mask_veg] - le_est[mask_veg]

    # When NDVI <= 0
    mask_nonveg = ndvi <= 0
    if np.any(mask_nonveg):
        e_sat = 0.6108 * np.exp(17.27*ta_C[mask_nonveg]/ta_C[mask_nonveg]+237.3)
        delta = (4098 * e_sat)/(ta_C[mask_nonveg] + 237.3)**2
        # Psychrometric constant equation
        if p is None:
            if elevation is not None:
                p_val = 101.3 * ((293 - 0.0065*elevation[mask_nonveg])/293)**5.26
            else:
                warnings.war(
                    "Pressure and Elevation are both None."
                    "Using default sea-level pressure 101.3 kPa"
                )
                p_val = 101.3
        gamma = (cp * p_val)/(param_lambda *  epsilon)
        le_est[mask_nonveg] = (delta * (rn_est[mask_nonveg] - g_est[mask_nonveg])/(delta + gamma))
        h_est[mask_nonveg] = rn_est[mask_nonveg] - le_est[mask_nonveg] - g_est[mask_nonveg]

    return le_est, h_est