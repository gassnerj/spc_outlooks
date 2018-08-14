import json
import urllib.request as request


class Features:
    def __init__(self):
        self.BASE_URL = 'https://api.weather.gov/alerts/'
        self.BROWSER_HEADER = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) ' \
                              'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'
        self.__features = None

    def get_json_data(self):
        try:
            q = request.Request(self.BASE_URL)
            q.add_header('User-Agent', self.BROWSER_HEADER)
            q.add_header('Accept', 'application/json')
            print('Getting data...')
            with request.urlopen(q) as response:
                data = response.read()
                encoding = response.info().get_content_charset('utf-8')
                self.__features = json.loads(data.decode(encoding))
                print('Data retrieved.')
                return True
        except request.HTTPError as e:
            print(e)
            return False

    def print_features(self):
        for feature in self.__features['features']:
            print(feature)


f = Features()
if f.get_json_data():
    f.print_features()
else:
    print("No data.")
