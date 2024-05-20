import requests
from fake_useragent import UserAgent
import time
from datetime import datetime
from tqdm import tqdm
import logging
import os


class RegionDataProcessor:
    def __init__(self, name, customer_place, customer_place_codes):
        self.name = name
        self.customer_place = customer_place
        self.customer_place_codes = customer_place_codes
        self.result = []
        self.result_clean = []

    @staticmethod
    def get_file_periods():
        return [
            '1&to=500',
            '501&to=1000',
            '1001&to=1500',
            '1501&to=2000',
            '2001&to=2500',
            '2501&to=3000',
            '3001&to=3500',
            '3501&to=4000',
            '4001&to=4500',
            '4501&to=5000'
        ]

    def fetch_data(self, headers):
        for file_p in self.get_file_periods():
            region_url = (
                'https://zakupki.gov.ru/epz/order/orderCsvSettings/download.html?morphology=on&search-filter=%D0'
                '%94%D0%B0%D1%82%D0%B5+%D1%80%D0%B0%D0%B7%D0%BC%D0%B5%D1%89%D0%B5%D0%BD%D0%B8%D1%8F&pageNumber'
                '=1&sortDirection=false&recordsPerPage=_10&showLotsInfoHidden=false&sortBy=UPDATE_DATE&fz44=on'
                '&pc=on&currencyIdGeneral=-1&customerPlace={customer_place}&customerPlaceCodes={'
                'customer_place_codes}&gws=%D0%92%D1%8B%D0%B1%D0%B5%D1%80%D0%B8%D1%82%D0%B5+%D1%82%D0%B8%D0%BF'
                '+%D0%B7%D0%B0%D0%BA%D1%83%D0%BF%D0%BA%D0%B8&OrderPlacementSmallBusinessSubject=on'
                '&OrderPlacementRnpData=on&OrderPlacementExecutionRequirement=on&orderPlacement94_0=0'
                '&orderPlacement94_1=0&orderPlacement94_2=0&from={file_p}&registryNumberCsv=true').format(
                customer_place=self.customer_place, customer_place_codes=self.customer_place_codes, file_p=file_p)

            for _ in range(3):  # Попробовать 3 раза
                try:
                    response = requests.get(region_url, headers=headers, timeout=300)
                    if response.status_code == 404:
                        logging.error("Ресурс не найден. Проверьте URL-адрес.")
                    else:
                        self.result_clean.append(response.content.decode('cp1251'))
                        self.result.extend(self.clean_content(self.result_clean))
                        break
                except requests.exceptions.Timeout:
                    logging.error("Запрос превысил время ожидания.")
                except requests.exceptions.RequestException as e:
                    logging.error(f"Произошла ошибка при выполнении запроса: {e}")
                time.sleep(5)  # Задержка перед повторной попыткой

    @staticmethod
    def clean_content(purchase_list):
        if purchase_list[0].startswith('Реестровый номер закупки'):
            purchase_list[0] = purchase_list[0].replace('Реестровый номер закупки', '').strip()

        cleaned_list = []
        for item in purchase_list[0].split('\n'):
            cleaned_list.append(item.replace('№', '').strip())

        return cleaned_list

    def save_to_file(self, directory, current_date):
        file_name = f'{self.name}_{current_date}.csv'
        file_path = os.path.join(directory, file_name)

        try:
            os.makedirs(directory, exist_ok=True)
            logging.debug(f"Каталог '{directory}' создан или уже существует")
        except Exception as e:
            logging.error(f"Произошла ошибка при создании каталога: {e}")

        try:
            with open(file_path, 'w', encoding='utf-8') as file:
                for data in self.result:
                    file.write(data + '\n')
            logging.info(f"Содержимое успешно сохранено в файл '{file_name}'.")
        except Exception as e:
            logging.error(f"Произошла ошибка при сохранении файла: {e}")


class DataPreparation:
    def __init__(self):
        self.ua = UserAgent()
        self.headers = {
            "User-Agent": self.ua.random,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Connection": "keep-alive",
        }
        logging.debug(self.headers)
        self.current_date = datetime.now().strftime("%Y-%m-%d")

    @staticmethod
    def regions():
        return [
            ("Dalnevostochnyy_federalnyy_okrug", "5277399", "OKER36"),
            ("Privolzhskiy_federalnyy_okrug", "5277362", "OKER33"),
            ("Severo-Zapadnyy_federalnyy_okrug", "5277336", "OKER31"),
            ("Severo-Kavkazskiy_federalnyy_okrug", "9409197", "OKER38"),
            ("Sibirskiy_federalnyy_fokrug", "5277384", "OKER35"),
            ("Uralskiy_federalnyy_okrug", "5277384", "OKER34"),
            ("Tsentralnyy_federalnyy_okrug", "5277317", "OKER30"),
            ("Yuzhnyy_federalnyy_okrug", "6325041", "OKER37")
        ]

    def run(self):
        for region_info in tqdm(self.regions(), desc='Выполняется процесс подготовки данных, подождите',
                                bar_format='{l_bar}{bar}', colour='green'):
            region_processor = RegionDataProcessor(*region_info)
            region_processor.fetch_data(self.headers)
            region_processor.save_to_file('result', self.current_date)

        print(f"Данные подготовлены и записаны")
        logging.info(f"Данные подготовлены и записаны: {self.current_date}")
