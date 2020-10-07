import enum
import re
import shutil
import requests
from PIL import Image
from bs4 import BeautifulSoup
from dateutil import parser


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
            return r'https://www.spc.noaa.gov/products/outlook/archive/'

    @property
    def base_image_url(self):
        return r'https://www.spc.noaa.gov/products/outlook/archive'

    @property
    def url(self):
        if self.forecast_period is Outlooks.DAY1:
            return self.base_url \
                   + str(self.forecast_date.year) \
                   + '/' \
                   + self.construct_file_name(self.forecast_date,
                                              'day1otlk',
                                              '0100',
                                              'html')
        elif self.forecast_period is Outlooks.DAY2:
            return self.base_url \
                   + str(self.forecast_date.year) \
                   + '/' \
                   + self.construct_file_name(self.forecast_date,
                                              'day2otlk',
                                              '0100',
                                              'html')
        elif self.forecast_period is Outlooks.DAY3:
            return self.base_url \
                   + str(self.forecast_date.year) \
                   + '/' \
                   + self.construct_file_name(self.forecast_date,
                                              'day3otlk',
                                              '0100',
                                              'html')
        elif self.forecast_period is Outlooks.DAY4:
            return self.base_url + 'day4-8_' + self.forecast_date.strftime('%Y%m%d') + '.html'
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

    @property
    def forecast_date(self):
        return self.__forecast_date

    def __init__(self, selected_outlook, f_date):
        self.__forecast_date = parser.parse(f_date)
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
        graphic_url = self.construct_graphic_url('0100', 'torn')
        r = requests.get(graphic_url, stream=True)

        if r.status_code == 200:
            r.raw.decode_content = True

            with open('forecast_graphic.gif', 'wb') as f:
                shutil.copyfileobj(r.raw, f)

            image_file_location = 'forecast_graphic.gif'
            image = Image.open(image_file_location)
            image.show()

    @staticmethod
    def construct_file_name(date, start_text, time, file_extension) -> str:
        return "{start_text}_{date}_{time}.{extension}" \
            .format(start_text=start_text,
                    date=date.strftime('%Y%m%d'),
                    time=time,
                    extension=file_extension)

    def construct_graphic_url(self, hour, g_type):
        if g_type == 'cat':
            return "{base}/{year}/day1otlk_{date}_{hour}_prt.gif".format(
                base=self.base_image_url,
                year=self.forecast_date.year,
                date=self.forecast_date,
                hour=hour,
                g_type=g_type
            )
        else:
            return "{base}/{year}/day1probotlk_{date}_{hour}_{g_type}_prt.gif".format(
                base=self.base_image_url,
                year=self.forecast_date.year,
                date=self.forecast_date,
                hour=hour,
                g_type=g_type
            )
