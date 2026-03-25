import numpy as np


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