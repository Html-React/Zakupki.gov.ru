import requests
from datetime import datetime
from fake_useragent import UserAgent
import time
import logging
import os


class HTTPClient:
    def __init__(self):
        user_agent = UserAgent()
        self.headers = {
            "User-Agent": user_agent.random,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Connection": "keep-alive",
        }

    def fetch_url(self, url, timeout=120, max_retries=3):
        for _ in range(max_retries):
            try:
                response = requests.get(url, headers=self.headers, timeout=timeout)
                response.raise_for_status()
                logging.debug(f"Успешно получен URL: {url}")
                return response.content.decode('cp1251')
            except requests.exceptions.Timeout as e:
                logging.error(f"Время ожидания истекло при получении URL-адреса: {e}")
            except requests.exceptions.HTTPError as e:
                logging.error(f"Ошибка HTTP при получении URL-адреса: {e}")
            except requests.exceptions.RequestException as e:
                logging.error(f"Произошла ошибка при получении URL-адреса: {e}")
            logging.info("Повторная попытка выполнения запроса...")
            time.sleep(5)  # Пауза перед повторной попыткой
        logging.error(f"Попытки получить URL после {max_retries} не увенчались успехом: {url}")
        return None


class DataFetcher:
    def __init__(self, client):
        self.http_client = client

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

    def fetch_data(self, url_template, customer_place, customer_place_codes):
        for file_p in self.get_file_periods():
            full_url = url_template.format(
                customer_place=customer_place,
                customer_place_codes=customer_place_codes,
                file_p=file_p
            )
            logging.debug(f"Получение данных из URL-адреса: {full_url}")
            response_content = self.http_client.fetch_url(full_url)
            if response_content:
                logging.debug(f"Успешно получены данные за период: {file_p}")
                yield response_content


class DataSave:
    def __init__(self):
        self.date_file = datetime.now().strftime('%Y-%m-%d')
        self.directory_file = 'result'
        self.extension_file = 'csv'
        
    @staticmethod
    def save_to_file(name_file, data):
        file_path = f'{directory_file}/{name_file}_{date_file}.{extension_file}'
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            logging.debug(f"Каталог '{os.path.dirname(file_path)}' создан или уже существует")
        except Exception as e:
            logging.error(f"Произошла ошибка при создании каталога: {e}")

        try:
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(data)
            logging.info(f"Содержимое успешно сохранено в файл '{file_path}'.")
        except Exception as e:
            logging.error(f"Произошла ошибка при сохранении файла: {e}")


class RegionDataProcessor:
    URL_TEMPLATE = (
        """https://zakupki.gov.ru/epz/order/orderCsvSettings/download.html?morphology=on&search-filter=%D0%94%D0%B0
        %D1%82%D0%B5+%D1%80%D0%B0%D0%B7%D0%BC%D0%B5%D1%89%D0%B5%D0%BD%D0%B8%D1%8F&pageNumber=1&sortDirection=false
        &recordsPerPage=_10&showLotsInfoHidden=false&sortBy=UPDATE_DATE&fz44=on&pc=on&currencyIdGeneral=-1
        &customerPlace={customer_place}&customerPlaceCodes={customer_place_codes}&gws=%D0%92%D1%8B%D0%B1%D0%B5%D1%80%
        D0%B8%D1%82%D0%B5+%D1%82%D0%B8%D0%BF+%D0%B7%D0%B0%D0%BA%D1%83%D0%BF%D0%BA%D0%B8&OrderPlacementSmall
        BusinessSubject=on&OrderPlacementRnpData=on&OrderPlacementExecutionRequirement=on&orderPlacement94_0=0
        &orderPlacement94_1=0&orderPlacement94_2=0&from={file_p}&registryNumberCsv=true""")

    def __init__(self):
        self.data_fetcher = DataFetcher(HTTPClient())
        self.result = []

    def fetch_and_process_data(self, name, customer_place, customer_place_codes):
        logging.debug(f"Начало обработки данных для региона: {name}")
        for response_content in self.data_fetcher.fetch_data(self.URL_TEMPLATE, customer_place, customer_place_codes):
            self.result.append(self.clean_content(response_content))
        logging.debug(f"Завершение обработки данных для региона: {name}")

    @staticmethod
    def clean_content(content):
        return content.replace('Реестровый номер закупки', '').replace('№', '').strip()
