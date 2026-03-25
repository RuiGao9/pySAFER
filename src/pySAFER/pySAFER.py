import numpy as np


## Step 1: Extraterrestrial radiation (Ra) calculation
def calc_ra(latitude, doy, year):
    """
    Calculate extraterrestrial radiation (Ra)
    Supports scalar values, Numpy arrays, or Pandas Series.
    Torres, A. F., Walker, W. R., & McKee, M. (2011). 
    Forecasting daily potential evapotranspiration using machine learning and limited climatic data. 
    Agricultural Water Management, 98(4), 553-562.
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
    Calculate the incoming solar radiation (Rs)。
    
    Logic of this function:
    1. if rs_obs (observation) is provided, use the observations directly
    2. if rs_obs is None, use Hargreaves's method for estimation
    
    parameters:
    ra: Extraterrestrial radaition (MJ/m2/day), calculated by function calc_ra 
    rs_obs: observations from the meteorological station (optional)
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
    ra: extraterrestrial radiation (Ra) 
    rs_est: incoming solar radiation (MJ/m2/day)
    albedo: a0
    
    return
    r_reflect: reflected global radiation
    """
    if r_up_obs is not None:
        r_reflect = np.asarray(r_up_obs)
    r_reflect = rs_est * albedo

    return r_reflect

# Step 5: Net radiation calculation (Rn)
def calc_r_net(rs_est, ra, albedo, tmax, tmin, rn_obs=None, para_c=6.99, para_d=39.93):
    """
    
    """
    if rn_obs is not None:
        return np.asarray(rn_est)
    al = para_c * (tmax+tmin)/2 - para_d
    rn_est = (1 - albedo) * rs_est - al * (rs_est/ra)

    return rn_est


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