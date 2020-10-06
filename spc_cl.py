import argparse
from spc import ConvectiveOutlook


arg_parser = argparse.ArgumentParser(description="Get SPC Outlook.")
arg_parser.add_argument('-o',
                        metavar='--outlook',
                        type=str,
                        help='The outlook, DAY1, DAY2, DAY3, or DAY4',
                        required=True)

arg_parser.add_argument('-d',
                        metavar='--date',
                        type=str,
                        help='The date of the outlook. mm-dd-yyy 05-31-2013',
                        required=True)

args = arg_parser.parse_args()

outlook = args.o
date = args.d

o = ConvectiveOutlook(outlook, date)
print(o.forecast_text)
print('The max category is: ' + o.max_category)
o.show_forecast_graphic()
