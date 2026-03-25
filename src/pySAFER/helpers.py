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


## Step 2: Global solar radiation at the surface
## Either measured or estimated
def get_solar_radiation(ra, rs_obs=None, tmax=None, tmin=None, coastal=False):
    """
    获取地表太阳辐射 (Rs/R_GS)。
    
    逻辑:
    1. 如果提供 rs_obs (观测值)，直接返回观测值。
    2. 如果 rs_obs 为 None，则使用 Hargreaves 公式根据气温估算。
    
    参数:
    ra: 大气外层辐射 (MJ/m2/day)，由 calc_ra 计算。
    rs_obs: 气象站直接观测的太阳辐射 (可选)。
    tmax: 最高温 (Celsius, 估算时必需)。
    tmin: 最低温 (Celsius, 估算时必需)。
    coastal: 是否为沿海地区 (k_Rs 系数不同)。
    """
    # 选项 1: 使用观测值
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

## Step 3:
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