import math
import numpy as np


class UnitConversionException(Exception):
    pass


class Atmosphere:
    def __init__(self):
        self.FarenheitTemperature = None
        self.pressure = None
        
        
    def convert_F_to_C(self, T):
        C = round((T - 32) * .5556, 2)
        return C
    
    def convert_C_to_F(self, T):
        F = round(T * 1.8 + 32, 2)
        return F
        
    def convert_C_to_K(self, T):
        K = round(T + 273.15, 2)
        return K
        
    def convert_F_to_K(self, T):
        K = round(self.convert_F_to_C(T) + 273.15, 2)
        return K
    
    def convert_K_to_C(self, T):
        C = round(T - 273.15, 2)
        
    def heat_index(self, T, rh):
        """Calculate the heat index with degrees F and Relative Humidity"""
        heatIndex = -42.379 + (2.04901523 * T) + (10.14333127 * rh) - (0.22475541 * T * rh) - (6.83783 * 10**-3 * T**2) - (5.481717 * 10**-2 * rh**2) + (1.22874 * 10**-3 * T**2 * rh) + (8.5282 * 10**-4 * T * rh**2) - (1.99 * 10**-6 * T**2 * rh**2)
        return math.ceil(heatIndex)
    
    def wind_chill(self, T, mph):
        """Calculate the wind chill using degrees F and wind speed in MPH"""
        windChill = 35.74 + (.6215 * T) - (35.75 * mph**.16) + (.4275 * T * mph**.16)
        return math.floor(windChill)
    
    def relative_humidity(self, T, Td):
        e = self.act_vapor_pressure(Td)
        es = self.sat_vapor_pressure(T)
        rh = e/es * 100
        return rh
    
    def dew_point(self, T, rh):
        es = self.sat_vapor_pressure(T) #no need to convert the temperature here; the called method does the conversion to C.
        Td = round((237.3 * math.log((es * rh)/611)) / (7.5 * math.log(10) - math.log((es * rh) / 611)), 2)
        Td = self.convert_C_to_F(Td)
        return Td
    
    def actual_mixing_ratio(self, T, Td, P):
        w = 621.97 * e/P - e
        return w
    
    def act_vapor_pressure(self, Td):
        """Returns the actual vapor pressure given the temperature in degrees F."""
        Td = self.convert_F_to_C(Td)
        n = (7.5 * Td) / (237.3 + Td)
        e = 6.11 * 10**n
        return e
        
    def sat_vapor_pressure(self, T):
        """Returns the saturation vapor pressure given the temperature in degrees F."""
        T = self.convert_F_to_C(T)
        n = (7.5 * T) / (237.3 + T)
        es = 6.11 * 10**n
        return es
    
    def sat_mixing_ratio(self, T, Td, P):
        pass
    
    def virtual_temp(self, T, Td, P):
        n = (7.5 * Td) / (237.7 + Td)
        Tv = (T + 273.15) / (1 - .379 * (6.11 * 10**n) / P)
        return Tv
    
    def calc_cape(self):
        data = [
        {'level':400, 'hgt':7605, 'Pt':-8.2, 'Tc':-19.1, 'WDIR':1, 'WSPD':1},
        {'level':375, 'hgt':8082, 'Pt':-11.2, 'Tc':-22.9, 'WDIR':1, 'WSPD':1},
        {'level':350, 'hgt':8583, 'Pt':-14.6, 'Tc':-26.9, 'WDIR':1, 'WSPD':1}
        ]
        
        c = ((264-253)/253)*(8082-7605)
        CAPE = ((self.convert_C_to_K(data[0]['Pt']) - self.convert_C_to_K(data[0]['Tc'])) / self.convert_C_to_K(data[0]['Tc'])) * (data[1]['hgt'] - data[0]['hgt'])
        return CAPE
        
        
a = Atmosphere()

# print(A.wind_chill(30, 50))

# t = 85

# print(a.dew_point(t, 100))

# rh = math.ceil(a.relative_humidity(t, 71))

# print(rh)

# print(a.heat_index(t, rh))

print(a.calc_cape())
