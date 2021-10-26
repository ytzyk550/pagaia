import numpy as np
import pandas as pd
from time import sleep
import math
import page_parser
import helpers


class ZillowScraping:

    def __init__(self, url: str) -> None:
        self.url = url
        self.content = page_parser.get_page_html(url)

    def get_all_ticks(self, element):
        try:
            ticks = page_parser.html_to_bs(str(element)).find_all(
                'g', class_="tick")
            points = []
            for t in ticks:
                text = t.text
                point = t['transform'][10:-1].split(',')
                points.append({'label': text, 'points': point})
            return points
        except Exception as e:
            print('get_all_ticks error: ' + str(e))

    def parse_ticks_data(self, element, type):
        try:
            ticks = self.get_all_ticks(element)
            points = []
            if type == 'YEARS':
                points = [{'x': float(t['points'][0]), 'y': t['label']}
                          for t in ticks]
            elif type == 'PRICES':
                points = [{'x': float(t['points'][1]), 'y': t['label'][1:-1]}
                          for t in ticks]
            return points
        except Exception as e:
            print('parse_ticks_data error: ' + str(e))

    def calculate_data_m_slope(self, data):
        try:
            if len(data) < 2:
                raise Exception('Can\'t calculate less then 2 points')

            x1 = data[0]['x']
            x2 = data[1]['x']
            y1 = data[0]['y']
            y2 = data[1]['y']

            return helpers.calculate_m_slope(x1, x2, y1, y2)
        except Exception as e:
            print('calculate_data_m_slope error: ' + str(e))

    def get_max_label(self, data_obj_array):
        try:
            return max(data_obj_array, key=lambda obj: obj['y'])
        except Exception as e:
            print('get_max_label error: ' + str(e))

    def get_min_label(self, data_obj_array):
        try:
            return min(data_obj_array, key=lambda obj: obj['y'])
        except Exception as e:
            print('get_min_label error: ' + str(e))

    def get_years_equation_params(self, data):
        try:
            m = self.calculate_data_m_slope(data)

            # Remove the top-label distance from x-axis
            min_label = self.get_min_label(data)
            distance = helpers.calculate_point_sum(
                float(min_label['x']+3), m, 0)
            # print(distance, min_label)

            b = float(min_label['y']) - distance
            return m, b
        except Exception as e:
            print('get_years_equation_params error: ' + str(e))

    def get_price_equation_params(self, data):
        try:
            m = self.calculate_data_m_slope(data)

            # Remove the top-label distance from x-axis
            max_label = self.get_max_label(data)
            distance = helpers.calculate_point_sum(
                float(max_label['x']), m, 1.3)
            print(m, distance, max_label)

            b = float(max_label['y']) - distance
            return m, b
        except Exception as e:
            print('get_price_equation_params error: ' + str(e))

    def extruct_path(self, path_part):
        graph = page_parser.html_to_bs(str(path_part)).find('path')['d']
        return graph.split(',')

    def parse_svg(self, svg):
        try:
            parts = svg.find_all(recursive=False)
            years = self.parse_ticks_data(parts[0], type='YEARS')
            prices = self.parse_ticks_data(parts[1], type='PRICES')
            points = self.extruct_path(parts[2])

            # The graph is created with relation of px & actual data, so we need to calculate it.
            y_m, y_b = self.get_price_equation_params(prices)
            x_m, x_b = self.get_years_equation_params(years)

            column_names = []
            monthly = []
            for i, d in enumerate(points[1:]):
                column_title = i
                point = d.split('L')
                sum = helpers.calculate_point_sum(
                    float(point[0]), y_m, y_b)

                if len(point) > 1:
                    month = helpers.calculate_point_sum(
                        float(point[1]), x_m, x_b)

                    month_frac, year = math.modf(month)
                    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May',
                                   'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
                    column_title = f'Historical {round(month_frac*12)} {month_names[round(month_frac*12)-1]} {round(year)}'
                # Else if it is last item = Today
                elif i == len(points)-2:
                    column_title = 'Today'
                column_names.append(column_title)
                monthly.append(f'${str(round(sum, 1))}K')

            return column_names, monthly
        except Exception as e:
            print('parse_svg error: ' + str(e))

    def get_price_and_address(self):
        try:
            sum = ''
            address = ''

            # Extract Home current price
            sum_element = self.content.find(
                'div', class_='ds-chip-removable-content')
            if sum_element:
                sum_span = sum_element.find_all('span')
                if sum_span:
                    sum = sum_span[-1].text
            if not sum:
                raise Exception('Can\'t find \'sum\' element')

            # Extract Home-address
            address_element = self.content.find(
                'h1', id='ds-chip-property-address')
            if address_element:
                address = address_element.text
            if not address:
                raise Exception('Can\'t find \'address\' element')
            return address, sum
        except Exception as e:
            print('get_price_and_address error: ' + str(e))

    def get_table_data(self):
        try:
            values = self.content.find('div', id='ds-home-values')
            svg = values.find('svg')
            return self.parse_svg(svg)
        except Exception as e:
            print('get_table_data error: ' + str(e))

    def scrap_to_table(self):
        try:
            address, current_price = self.get_price_and_address()
            month_names, historical_monthly = self.get_table_data()

            print('Creating the data table...')
            columns = ['Full Address', 'Current Value'] + month_names
            values = np.array([[address, current_price]+historical_monthly])

            df = pd.DataFrame(values, columns=columns)
            print(df)
            print('Write to file...')
            file_name = 'static/extracted_data.html'
            html = df.to_html(open(file_name, 'w'))
            # helpers.open_url_on_chrome(file_name)
            # print(html)
            print('Task done!')
        except Exception as e:
            print('scrap_to_table error: ' + str(e))


def main():
    url = "https://www.zillow.com/homes/32022-Poppy-Way-Lake-Elsinore,-CA-92532_rb/17937295_zpid/"

    z = ZillowScraping(url)
    sleep(2)
    z.scrap_to_table()


if __name__ == "__main__":
    main()
