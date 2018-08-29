from bs4 import BeautifulSoup
import requests
import re
import enum


class Outlooks(enum.Enum):
    DAY1 = 0
    DAY2 = 1
    DAY3 = 2
    DAY4 = 3


class ConvectiveOutlook(object):
    @property
    def base_url(self):
        if self.forecast_period is Outlooks.DAY4:
            return r'https://www.spc.noaa.gov/products/exper/'
        else:
            return r'https://www.spc.noaa.gov/products/outlook/'

    @property
    def url(self):
        if self.forecast_period is Outlooks.DAY1:
            return self.base_url + 'day1otlk.html'
        elif self.forecast_period is Outlooks.DAY2:
            return self.base_url + 'day2otlk.html'
        elif self.forecast_period is Outlooks.DAY3:
            return self.base_url + 'day3otlk.html'
        elif self.forecast_period is Outlooks.DAY4:
            return self.base_url + 'day4-8/'
        else:
            raise IndexError("That outlook doesn't exist.")

    @property
    def forecast_period(self):
        return self.__forecast_period

    @forecast_period.setter
    def forecast_period(self, value):
        self.__forecast_period = value

    @property
    def max_category(self):
        if self.forecast_period != Outlooks.DAY4:
            match = re.search(r"ENHANCED|SLIGHT|MODERATE|HIGH|MARGINAL|NO SEVERE]*", self.forecast_text, flags=0)
            return match.group().capitalize()
        else:
            return 'Not available'

    def __init__(self, outlook):
        self.__forecast_period = outlook
        self.forecast_text = self.get_forecast_text()
        self.categorical_graphic = self.base_url + 'day1otlk_2000_prt.gif'
        self.probabilistic_tornado_graphic = self.base_url + 'day1probotlk_2000_torn_prt.gif'
        self.probabilistic_damaging_wind_graphic = None
        self.probabilistic_large_hail_graphic = None

    def get_forecast_text(self):
        r = requests.get(self.url)
        data = r.text
        soup = BeautifulSoup(data, "lxml")
        for text in soup.find('pre'):
            return text


o = ConvectiveOutlook(Outlooks.DAY1)
print(o.forecast_text)
print('The max category is: ' + o.max_category)
