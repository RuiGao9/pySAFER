import numpy as np


def calc_ndvi(red, nir):
    """
    计算归一化植被指数 (NDVI)。
    支持输入：单个数值、Pandas Series (列) 或 NumPy 数组 (图像)。
    
    参数:
    red: 红色波段反射率 (0-1)
    nir: 近红外波段反射率 (0-1)
    
    返回:
    ndvi: 范围在 [-1, 1] 之间的植被指数
    """
    # 将输入转换为 numpy 数组以确保计算兼容性
    red = np.asarray(red)
    nir = np.asarray(nir)
    
    # 防止除以零的错误 (例如在水体或阴影区)
    denominator = nir + red
    
    # 使用 np.where 处理分母为 0 的情况，将其设为 NaN 或 0
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