import math
import numpy as np
import enum
from decimal import *

"""
************************************************************************************************************
*Resources:                                                                                                *
*                                                                                                          *
*    References:                                                                                           *
*        Mixing Ratio: https://www.weather.gov/media/epz/wxcalc/mixingRatio.pdf                            *
*        Temperature Conversions: https://www.weather.gov/media/epz/wxcalc/tempConvert.pdf                 *
*        Wet-bulb Temperature and Dew Point: https://www.weather.gov/media/epz/wxcalc/wetBulbTdFromRh.pdf  *
*        LCL: https://en.wikipedia.org/wiki/Lifted_condensation_level                                      *
*    Calculators:                                                                                          *
*        Vapor Pressure: https://www.weather.gov/epz/wxcalc_vaporpressure                                  *
*        Mixing Ratio: https://www.weather.gov/epz/wxcalc_mixingratio                                      *
*        Virtual Temperature: https://www.weather.gov/epz/wxcalc_virtualtemperature                        *
*                                                                                                          *
*    Thermodynamics: http://www.inscc.utah.edu/~krueger/3510/Thermo.2007.pdf                               *
*                                                                                                          *
*    theWeatherPrediction (basic equations): http://www.theweatherprediction.com/basic/equations/          *
************************************************************************************************************
"""


class TemperatureUnits(enum.Enum):
    C = 1
    F = 2
    K = 3


class PressureUnits(enum.Enum):
    mb = 1
    hPa = 2
    inches = 3


class Temperature:
    def __init__(self, temperature=None, units=None):
        self.value = temperature
        self.units = units

    def convert(self, temperature, output_units=None):
        if temperature.units == TemperatureUnits.C and output_units == TemperatureUnits.F:
            return self.__convert_celsius_to_fahrenheit(temperature.value)
        elif temperature.units == TemperatureUnits.C and output_units == TemperatureUnits.K:
            return self.__convert_celsius_to_kelvin(temperature.value)
        elif temperature.units == TemperatureUnits.F and output_units == TemperatureUnits.C:
            return self.__convert_fahrenheit_to_celsius(temperature.value)
        elif temperature.units == TemperatureUnits.F and output_units == TemperatureUnits.K:
            return self.__convert_fahrenheit_to_kelvin(temperature.value)
        elif temperature.units == TemperatureUnits.K and output_units == TemperatureUnits.C:
            return self.__convert_kelvin_to_celsius(temperature.value)
        elif temperature.units == TemperatureUnits.K and output_units == TemperatureUnits.F:
            return self.__convert_kelvin_to_fahrenheit(temperature.value)
        else:
            raise InvalidOperation('You cannot do that conversion.')

    @staticmethod
    def __convert_fahrenheit_to_celsius(temperature):
        return Temperature((temperature - 32) * .5556, TemperatureUnits.C)

    @staticmethod
    def __convert_celsius_to_fahrenheit(temperature):
        return Temperature(temperature * 1.8 + 32, TemperatureUnits.F)

    @staticmethod
    def __convert_celsius_to_kelvin(temperature):
        return Temperature(temperature + 273.15, TemperatureUnits.K)

    def __convert_fahrenheit_to_kelvin(self, temperature):
        return Temperature(self.__convert_fahrenheit_to_celsius(temperature).value + 273.15, TemperatureUnits.K)

    @staticmethod
    def __convert_kelvin_to_celsius(temperature):
        return Temperature(temperature - 273.15, TemperatureUnits.C)

    def __convert_kelvin_to_fahrenheit(self, temperature):
        c = __convert_kelvin_to_celsius(temperature)
        return Temperature(self.__convert_celsius_to_fahrenheit(c.value), TemperatureUnits.F)


class Pressure:
    def __init__(self, pressure=None, units=None):
        self.value = pressure
        self.units = units


class Atmosphere:
    def __init__(
            self,
            temperature=Temperature(None, TemperatureUnits.C),
            pressure=Pressure(None, PressureUnits.mb),
            dew_point=Temperature(None, TemperatureUnits.C),
            wind_speed=None,
            temperature_units=TemperatureUnits.C
    ):
        self.temperature = temperature
        self.pressure = pressure
        self.dew_point = dew_point
        self.temperature_units = temperature_units
        self.pressure_units = PressureUnits.mb
        self.relative_humidity = self.relative_humidity()
        self.wind_speed = wind_speed

    def heat_index(self, temperature=None, rh=None):
        """Calculate the heat index with degrees F and Relative Humidity"""
        if temperature is None:
            temperature = self.temperature
        if rh is None:
            rh = self.relative_humidity
        if self.temperature.units != TemperatureUnits.F:
            temperature = self.temperature.convert(temperature, TemperatureUnits.F)

        heat_index = -42.379 + (2.04901523 * temperature.value) + \
                               (10.14333127 * rh) - \
                               (0.22475541 * temperature.value * rh) - \
                               (6.83783 * 10**-3 * temperature.value ** 2) - \
                               (5.481717 * 10**-2 * rh**2) + \
                               (1.22874 * 10**-3 * temperature.value ** 2 * rh) + \
                               (8.5282 * 10**-4 * temperature.value * rh ** 2) - \
                               (1.99 * 10**-6 * temperature.value ** 2 * rh ** 2)
        return Temperature(math.ceil(heat_index), TemperatureUnits.F)

    def wind_chill(self, temperature=None, mph=None):
        """Calculate the wind chill using degrees F and wind speed in MPH"""
        if temperature is None:
            temperature = self.temperature
        if mph is None:
            mph = self.wind_speed
        if self.temperature.units != TemperatureUnits.F:
            temperature = temperature.convert(temperature, TemperatureUnits.F)
        wind_chill = 35.74 + (.6215 * temperature.value) - \
                             (35.75 * mph**.16) + \
                             (.4275 * temperature.value * mph**.16)
        return Temperature(math.floor(wind_chill), TemperatureUnits.F)

    def relative_humidity(self, temperature=None, dew_point_temperature=None):
        if temperature is None:
            temperature = self.temperature
        if dew_point_temperature is None:
            dew_point_temperature = self.dew_point
        if temperature.units != TemperatureUnits.C:
            temperature.convert(temperature, TemperatureUnits.C)
        if dew_point_temperature.units != TemperatureUnits.C:
            dew_point_temperature.convert(dew_point_temperature, TemperatureUnits.C)

        e = self.vapor_pressure(dew_point_temperature)
        es = self.vapor_pressure(temperature)
        relative_humidity = e/es * 100
        return relative_humidity

    def dew_point(self, temperature=None, relative_humidity=None):
        if temperature is None:
            temperature = self.temperature
        if relative_humidity is None:
            relative_humidity = self.relative_humidity
        if self.temperature.units != TemperatureUnits.C:
            temperature = temperature.convert(temperature, TemperatureUnits.C)

        es = self.vapor_pressure(temperature)
        dew_point_temperature = round((237.3 * math.log((es * relative_humidity)/611)) /
                                      (7.5 * math.log(10) - math.log((es * relative_humidity) / 611)), 2)
        # dew_point_temperature = self.convert_celsius_to_fahrenheit(dew_point_temperature)
        return Temperature(dew_point_temperature, TemperatureUnits.C)

    def mixing_ratio(self, temperature=None, pressure=None):
        if temperature is None:
            temperature = self.temperature
        if pressure is None:
            pressure = self.pressure

        actual_vapor_pressure = self.vapor_pressure(temperature)
        return 621.97 * (actual_vapor_pressure / (pressure.value - actual_vapor_pressure))

    """Clausius-Clapeyron equation given the temperature in degrees Fahrenheit."""
    def vapor_pressure(self,
                       temperature=None,
                       p_units=PressureUnits.mb
                       ):
        """Returns the saturation vapor pressure."""
        if temperature is None:
            temperature = self.temperature
        n = (7.5 * temperature.value) / (237.3 + temperature.value)
        es = 6.11 * (10**n)
        if p_units is PressureUnits.hPa:
            es = es / 10
        return es

    def virtual_temp(self, temperature=None, dew_point_temperature=None, pressure=None):
        if temperature is None:
            temperature = self.temperature
        if dew_point_temperature is None:
            dew_point_temperature = self.dew_point
        if pressure is None:
            pressure = self.pressure
        if temperature.units != TemperatureUnits.C:
            temperature.convert(temperature, TemperatureUnits.C)

        n = (7.5 * dew_point_temperature.value) / (237.7 + dew_point_temperature.value)
        return Temperature(
            (temperature.value + 273.15) /
            (1 - .379 * (6.11 * 10**n) / pressure.value), TemperatureUnits.K)

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

    def convert_millibars_to_pascals(self, pressure):
        return pressure * 100

    def potential_temperature(self, pressure=None, temperature=None):
        if pressure is None:
            pressure = self.pressure
        if temperature is None:
            temperature = self.temperature
        t = temperature.convert(temperature, TemperatureUnits.K).value
        p = 1000 / pressure.value
        return Temperature(t * p ** .286, TemperatureUnits.K)

    """Equivalent potential temperature, Theta-E. Greater Theta-E equals greater potential
       for positive buoyancy."""
    def equivalent_potential_temperature(self,
                                         pressure=None,
                                         temperature=None,
                                         round_result=False):
        if pressure is None:
            pressure = self.pressure
        if temperature is None:
            temperature = self.temperature
        if temperature.units != TemperatureUnits.K:
            temperature = temperature.convert(temperature, TemperatureUnits.K)

        w = 11.56  # saturation mixing ratio in g/kg.
        theta_e = temperature.value * (1000 / pressure.value) ** .286 + 3 * w
        if round_result is True:
            theta_e = round(theta_e, 2)
        return Temperature(theta_e, TemperatureUnits.K)


a = Atmosphere(temperature=Temperature(85, TemperatureUnits.F), pressure=Pressure(850, PressureUnits.mb),
               dew_point=Temperature(65, TemperatureUnits.F), wind_speed=10)

vp = a.vapor_pressure()
rh = round(a.relative_humidity, 2)
te = a.potential_temperature()
ept = a.equivalent_potential_temperature()
vt = a.virtual_temp()
wc = a.wind_chill()
hi = a.heat_index()

print('The vapor pressure is {0}{1}.'.format(round(vp, 2), a.pressure_units.name))

print('The RH is: {0}%.'.format(rh))

print('Theta-E temperature is {0}{1}{2}.'.format(
    round(te.value, 0), chr(176), te.units.name))

print('The equivalent potential temperature is {0}{1}{2}.'.format(round(ept.value, 2), chr(176), ept.units.name))

print('The mixing ratio is {0}.'.format(round(a.mixing_ratio(), 2)))

print('The virtual temperature is {0}{1}{2}.'.format(round(vt.value, 2), chr(176), vt.units.name))

print('The wind chill is {0}{1}{2}.'.format(round(wc.value, 2), chr(176), wc.units.name))

print('The heat index is {0}{1}{2}.'.format(round(hi.value, 2), chr(176), hi.units.name))
