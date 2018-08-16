import math
import numpy as np
import enum


class UnitConversionException(Exception):
    pass


class TemperatureUnits(enum.Enum):
    celsius = 1
    fahrenheit = 2
    kelvin = 3


class PressureUnits(enum.Enum):
    millibars = 1
    hectoPascals = 2


class Atmosphere:
    def __init__(self):
        self.fahrenheit_temperature = None
        self.pressure = None

    @staticmethod
    def convert_fahrenheit_to_celsius(temperature):
        celsius = (temperature - 32) * .5556
        return celsius

    @staticmethod
    def convert_celsius_to_fahrenheit(temperature):
        fahrenheit = temperature * 1.8 + 32
        return fahrenheit

    @staticmethod
    def convert_celsius_to_kelvin(temperature):
        kelvin = temperature + 273.15
        return kelvin

    def convert_fahrenheit_to_kelvin(self, temperature):
        kelvin = self.convert_fahrenheit_to_celsius(temperature) + 273.15
        return kelvin

    @staticmethod
    def convert_kelvin_to_celsius(temperature):
        celsius = temperature - 273.15
        return celsius

    def convert_kelvin_to_fahrenheit(self, temperature):
        c = self.convert_kelvin_to_celsius(temperature)
        return self.convert_celsius_to_fahrenheit(c)

    @staticmethod
    def heat_index(temperature, rh):
        """Calculate the heat index with degrees F and Relative Humidity"""
        heat_index = -42.379 + (2.04901523 * temperature) + (10.14333127 * rh) - (0.22475541 * temperature * rh)\
                     - (6.83783 * 10**-3 * T**2) - (5.481717 * 10**-2 * rh**2) + (1.22874 * 10**-3 * T**2 * rh)\
                     + (8.5282 * 10**-4 * T * rh**2) - (1.99 * 10**-6 * T**2 * rh**2)
        return math.ceil(heat_index)

    @staticmethod
    def wind_chill(temperature, mph):
        """Calculate the wind chill using degrees F and wind speed in MPH"""
        wind_chill = 35.74 + (.6215 * temperature) - (35.75 * mph**.16) + (.4275 * temperature * mph**.16)
        return math.floor(wind_chill)

    def relative_humidity(self, temperature, dew_point_temperature):
        e = self.vapor_pressure(dew_point_temperature)
        es = self.vapor_pressure(temperature)
        relative_humidity = e/es * 100
        return relative_humidity

    def dew_point(self, temperature, relative_humidity):
        es = self.saturation_vapor_pressure(temperature)
        dew_point_temperature = round((237.3 * math.log((es * relative_humidity)/611)) /
                                      (7.5 * math.log(10) - math.log((es * relative_humidity) / 611)), 2)
        dew_point_temperature = self.convert_celsius_to_fahrenheit(dew_point_temperature)
        return dew_point_temperature

    def mixing_ratio(self, temperature, pressure):
        actual_vapor_pressure = self.vapor_pressure(temperature)
        return 621.97 * (actual_vapor_pressure / (pressure - actual_vapor_pressure))

    """Clausius-Clapeyron equation given the temperature in degrees Fahrenheit."""
    def vapor_pressure(self, temperature, t_units=TemperatureUnits.celsius, p_units=PressureUnits.millibars):
        """Returns the saturation vapor pressure."""
        if t_units is not TemperatureUnits.celsius:
            if t_units is TemperatureUnits.fahrenheit:
                temperature = self.convert_fahrenheit_to_celsius(temperature)
            elif t_units is TemperatureUnits.kelvin:
                temperature = self.convert_kelvin_to_celsius(temperature)
        n = (7.5 * temperature) / (237.3 + temperature)
        es = 6.11 * (10**n)
        if p_units is PressureUnits.hectoPascals:
            es = es / 10
        return es

    @staticmethod
    def virtual_temp(temperature, dew_point_temperature, pressure):
        n = (7.5 * dew_point_temperature) / (237.7 + dew_point_temperature)
        virtual_temperature = (temperature + 273.15) / (1 - .379 * (6.11 * 10**n) / pressure)
        return virtual_temperature

    def calc_cape(self):
        data = [
                {'level': 400, 'hgt': 7605, 'Pt': -8.2, 'Tc': -19.1, 'WDIR': 1, 'WSPD': 1},
                {'level': 375, 'hgt': 8082, 'Pt': -11.2, 'Tc': -22.9, 'WDIR': 1, 'WSPD': 1},
                {'level': 350, 'hgt': 8583, 'Pt': -14.6, 'Tc': -26.9, 'WDIR': 1, 'WSPD': 1}
        ]

        c = ((264-253)/253)*(8082-7605)
        CAPE = ((self.convert_celsius_to_kelvin(data[0]['Pt']) - self.convert_C_to_K(data[0]['Tc']))
                / self.convert_celsius_to_kelvin(data[0]['Tc'])) * (data[1]['hgt'] - data[0]['hgt'])
        return CAPE

    @staticmethod
    def convert_millibars_to_pascals(pressure):
        return pressure * 100

    def potential_temperature(self, pressure, temperature):
        t = self.convert_celsius_to_kelvin(temperature)
        p = 1000 / pressure
        return t * p ** .286

    """Equivalent potential temperature, Theta-E. Greater Theta-E equals greater potential
       for positive buoyancy."""
    def equivalent_potential_temperature(self, pressure, temperature, round_result=False):
        t = self.convert_celsius_to_kelvin(temperature)
        w = 11.56  # saturation mixing ratio in g/kg.
        theta_e = t * (1000 / pressure) ** .286 + 3 * w
        if round_result is True:
            theta_e = round(theta_e, 2)
        return theta_e


a = Atmosphere()

print(a.vapor_pressure(50.00))

print(round(a.relative_humidity(70, 50), 0))

print(round(a.potential_temperature(500, 0), 0))

print(a.equivalent_potential_temperature(850, 38, True))

print(a.mixing_ratio(16, 850))

# print(A.wind_chill(30, 50))

# t = 85

# print(a.dew_point(t, 100))

# rh = math.ceil(a.relative_humidity(t, 71))

# print(rh)

# print(a.heat_index(t, rh))

# print(a.calc_cape())
