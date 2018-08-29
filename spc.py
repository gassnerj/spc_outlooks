from bs4 import BeautifulSoup
import requests
import re
import enum


class Outlooks(enum.Enum):
    DAY1 = 0
    DAY2 = 1
    DAY3 = 2
    DAY4 = 3


class ConvectiveOutlook:
    def __init__(self, outlook):
        self.forecast_period = outlook
        self.url = self.base_url + self.__get__outlook_url()
        self.base_url = None
        self.forecast_text = self.__get_forecast_text()
        self.max_category = self.__get_max_category()
        self.categorical_graphic = self.base_url + 'day1otlk_2000_prt.gif'
        self.probabilistic_tornado_graphic = self.base_url + 'day1probotlk_2000_torn_prt.gif'
        self.probabilistic_damaging_wind_graphic = None
        self.probabilistic_large_hail_graphic = None

    @property
    def base_url(self):
        return r'https://www.spc.noaa.gov/products/outlook/'

    @base_url.setter
    def base_url(self, base_url):
        self.base_url = base_url

    def __get__outlook_url(self):
        if self.forecast_period is Outlooks.DAY1:
            return 'day1otlk.html'
        elif self.forecast_period is Outlooks.DAY2:
            return 'day2otlk.html'
        elif self.forecast_period is Outlooks.DAY3:
            return 'day3otlk.html'
        elif self.forecast_period is Outlooks.DAY4:
            self.base_url(r'https://www.spc.noaa.gov/products/exper/')
            return 'day4-8/'
        else:
            raise IndexError("That outlook doesn't exist.")

    def __get_forecast_text(self):
        r = requests.get(self.url)
        data = r.text
        soup = BeautifulSoup(data, "lxml")
        for text in soup.find('pre'):
            return text

    def __get_max_category(self):
        if self.forecast_period != Outlooks.DAY4:
            match = re.search(r"ENHANCED|SLIGHT|MODERATE|HIGH|MARGINAL|NO SEVERE]*", self.forecast_text, flags=0)
            return match.group()
        else:
            return 'Not available'


o = ConvectiveOutlook(Outlooks.DAY4)
print(o.forecast_text)
print('The max category is: ' + o.max_category.capitalize())
