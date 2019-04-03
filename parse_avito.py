import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import requests
from bs4 import BeautifulSoup
import requests
from time import sleep
import csv


class AvitoParser():
    def __init__(self,n_slice=8, max_price=2000000):
        self.brands = ['alfa_romeo', 'alpina', 'aro', 'asia', 'aston_martin', 'audi', 'bajaj', 'baw', 'bentley', 'bmw',
                       'brilliance', 'bufori', 'bugatti', 'buick', 'byd', 'cadillac', 'caterham', 'changan',
                       'changfeng', 'chery', 'chevrolet', 'chrysler', 'citroen', 'dacia', 'dadi', 'daewoo', 'daihatsu',
                       'daimler', 'datsun', 'derways', 'dodge', 'dongfeng', 'doninvest', 'ds', 'dw_hower', 'eagle',
                       'ecomotors', 'faw', 'ferrari', 'fiat', 'ford', 'foton', 'gac', 'geely', 'genesis', 'geo', 'gmc',
                       'great_wall', 'hafei', 'haima', 'haval', 'hawtai', 'honda', 'huanghai', 'hummer', 'hyundai',
                       'infiniti', 'iran_khodro', 'isuzu', 'iveco', 'jac', 'jaguar', 'jeep', 'jinbei', 'jmc', 'kia',
                       'koenigsegg', 'lamborghini', 'lancia', 'land_rover', 'landwind', 'ldv', 'lexus', 'lifan',
                       'lincoln', 'lotus', 'luxgen', 'mahindra', 'marussia', 'maserati', 'maybach', 'mazda', 'mclaren',
                       'mercedes-benz', 'mercury', 'metrocab', 'mg', 'mini', 'mitsubishi', 'mitsuoka', 'morgan',
                       'morris', 'nissan', 'noble', 'oldsmobile', 'opel', 'pagani', 'peugeot', 'plymouth', 'pontiac',
                       'porsche', 'proton', 'puch', 'ravon', 'renault', 'rolls-royce', 'ronart', 'rover', 'saab',
                       'saleen', 'saturn', 'scion', 'seat', 'shuanghuan', 'skoda', 'sma', 'smart', 'spyker',
                       'ssangyong', 'subaru', 'suzuki', 'talbot', 'tata', 'tesla', 'tianma', 'tianye', 'toyota',
                       'trabant', 'volkswagen', 'volvo', 'vortex', 'wartburg', 'westfield', 'wiesmann', 'xin_kai',
                       'zibar', 'zotye', 'zx', 'vaz_lada', 'vis', 'gaz', 'zaz', 'zil', 'izh', 'luaz', 'moskvich', 'raf',
                       'smz', 'tagaz', 'uaz']
        self.num_holders = ['odin_vladelec', 'ne_bolee_dvuh', 'tri_i_bolee']
        self.max_price = max_price
        self.n_slice = n_slice
        self.conditions = []
        self.result_car_list = []
        self.base_url = 'https://www.avito.ru/rossiya/avtomobili/s_probegom/'
        self.page = 'page15/'
        self.base_cond = '&pts=2&order=price&damaged=2&mileage_condition=2&go_search=2'
        self.pages = []
        self.df = pd.DataFrame()
        self.get_conditions()
        pass

    def get_conditions(self):
        step = round(self.max_price / self.n_slice, 0)
        for i in range(self.n_slice):
            cond = 'pmax=' + str(int((i + 1) * step)) + '&pmin=' + str(int(i * step + 1))
            if i == 0:
                cond = 'pmax=' + str(int(step)) + '&pmin=0'
            if i == self.n_slice - 1:
                cond = 'pmin=' + str(int(self.max_price + 1))
            self.conditions.append(cond)
        pass

    def parse_data(self, n_brands):
        def get_cars_avito(page, holder):
            def get_page(url):
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.117 Safari/537.36'}
                page = requests.get(url, headers=headers).text
                return page

            soup = BeautifulSoup(get_page(page), 'lxml')
            cards = soup.find_all('div', class_='item_table')
            cars = []
            for card in cards:
                title = card.find('h3', class_='title').text.strip()
                price = card.find('div', class_='about').contents[0].strip()
                specs = card.find('div', class_='about').contents[1].text.strip().split(',')
                if len(specs) == 5:
                    specs.insert(0, 'не битый')
                stats_list = [title, price, holder]
                stats_list += specs
                cars.append(stats_list)
            return cars

        for brand in self.brands[:n_brands]:
            for holder in self.num_holders:
                for cond in self.conditions:
                    for p in range(1, 10):
                        page = self.base_url + holder + '/' + brand + '?p=' + str(p) + '&' + cond
                        self.pages.append(page)
                        try:
                            cars = get_cars_avito(page, holder)
                        except:
                            continue
                        time_sleep = np.random.uniform(1, 4)
                        # print('waiting for {n} seconds before next big page'.format(n=time_sleep))
                        sleep(time_sleep)
                        if len(cars) == 0:
                            break
                        self.result_car_list += cars
        pass

    def create_df(self):
        self.df = pd.DataFrame(self, result_car_list,
                               columns=['name', 'price', 'n_holders', 'status', 'mileage', 'engine', 'car_type',
                                        'drive_type', 'engine_type'])
        self.df.dropna(inplace=True)
        self.df['year'] = self.df.name.str[-4:].astype(int)
        self.df['brand'] = self.df.name.str.partition()[0]
        self.df['model'] = self.df.name.str.partition()[2].str[:-6]
        self.df['brand'] = self.df['brand'].str.replace(',', '').replace(' ', '').str.lower()
        self.df['model'] = self.df['model'].str.replace(',', '').replace(' ', '').str.lower()
        self.df['mileage'] = self.df['mileage'].str[:-3].str.replace(' ', '').astype(int)
        self.df['price'] = self.df['price'].str[:-5].str.replace(' ', '').astype(int)
        self.df['engine_vol'] = 0.01
        self.df.loc[(self.df['engine'].str.startswith(' A')) | (self.df['engine'].str.startswith(' M')) | (
            self.df['engine'].str.startswith(' C')), 'engine_vol'] = np.nan
        self.df.loc[self.df['engine_vol'].isnull() == False, 'engine_vol'] = self.df['engine'][self.df[
                                                                                                   'engine_vol'].isnull() == False].str[
                                                                             1:4].astype(float)
        self.df['hp'] = self.df['engine'].str[-9:-5].str.replace('(', '').astype(float)
        self.df['box_type'] = self.df['engine'].str[-14:-10].str.replace('\xa0', '').str.replace('\d+', '').str.replace(
            "+", '').str.replace(".", '').str.replace("(", '').str.replace(' ', '')
        # self.df['box_type'] = self.df['engine'].str.split('\xa0').str[-2].str.replace(' ','').astype(str)
        self.df.loc[self.df['box_type'].str.endswith('T'), 'box_type'] = self.df['box_type'][
                                                                             self.df['box_type'].str.endswith('T')].str[
                                                                         :-1]
        self.df.loc[self.df['status'] == 'не битый', 'status'] = 0.
        self.df.loc[self.df['status'] == 'Битый', 'status'] = 1.
        self.df['age'] = 2018 - self.df['year']
        return self.df


AP = AvitoParser()
AP.parse_data(2)
df = AP.create_df
