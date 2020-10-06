from bs4 import BeautifulSoup
import requests
import re
import enum
import argparse
from PIL import Image
import shutil
from dateutil import parser
import time

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
    def base_image_url(self):
        return r'https://www.spc.noaa.gov/products/outlook/archive'

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

    def __init__(self, selected_outlook):
        self.__forecast_period = self.parse_text_argument(selected_outlook)
        self.forecast_text = self.get_forecast_text()
        self.categorical_graphic = self.base_url + 'day1otlk_2000_prt.gif'
        self.probabilistic_tornado_graphic = self.base_url + 'day1probotlk_2000_torn_prt.gif'
        self.probabilistic_damaging_wind_graphic = None
        self.probabilistic_large_hail_graphic = None

    @staticmethod
    def parse_text_argument(arg='DAY1'):
        if arg == 'DAY1':
            return Outlooks.DAY1
        elif arg == 'DAY2':
            return Outlooks.DAY2
        elif arg == 'DAY3':
            return Outlooks.DAY3
        elif arg == 'DAY4':
            return Outlooks.DAY4
        else:
            return None

    def get_forecast_text(self):
        r = requests.get(self.url)
        data = r.text
        soup = BeautifulSoup(data, "lxml")
        for text in soup.find('pre'):
            return text

    def show_forecast_graphic(self):
        graphic_url = self.construct_graphic_url('05/31/2013', '0100', 'torn')
        r = requests.get(graphic_url, stream=True)

        if r.status_code == 200:
            r.raw.decode_content = True

            with open('forecast_graphic.gif', 'wb') as f:
                shutil.copyfileobj(r.raw, f)

            image_file_location = 'forecast_graphic.gif'
            image = Image.open(image_file_location)
            image.show()

    def construct_graphic_url(self, date, hour, g_type):
        date = parser.parse(date)
        year = date.year
        parsed_date = date.strftime('%Y%m%d')

        if g_type == 'cat':
            return "{base}/{year}/day1otlk_{date}_{hour}_prt.gif".format(
                base=self.base_image_url,
                year=year,
                date=parsed_date,
                hour=hour,
                g_type=g_type
            )
        else:
            return "{base}/{year}/day1probotlk_{date}_{hour}_{g_type}_prt.gif".format(
                base=self.base_image_url,
                year=year,
                date=parsed_date,
                hour=hour,
                g_type=g_type
            )


arg_parser = argparse.ArgumentParser(description="Get SPC Outlook.")
arg_parser.add_argument('-o',
                        metavar='--outlook',
                        type=str,
                        help='The outlook, DAY1, DAY2, DAY3, or DAY4',
                        required=True)

args = arg_parser.parse_args()

outlook = args.o

o = ConvectiveOutlook(outlook)
print(o.forecast_text)
print('The max category is: ' + o.max_category)
o.show_forecast_graphic()
