import logging
from tqdm import tqdm
from src import HTTPClient,  DataFetcher, DataSaver, RegionDataProcessor


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, filename="logfile.log", filemode="w",
                        format="%(asctime)s %(levelname)s %(message)s", encoding='utf-8')

    data_save = DataSave()
    region_processor = RegionDataProcessor()

    regions = [
        ("Dalnevostochnyy_federalnyy_okrug", "5277399", "OKER36"),
        ("Privolzhskiy_federalnyy_okrug", "5277362", "OKER33"),
        ("Severo-Zapadnyy_federalnyy_okrug", "5277336", "OKER31"),
        ("Severo-Kavkazskiy_federalnyy_okrug", "9409197", "OKER38"),
        ("Sibirskiy_federalnyy_fokrug", "5277384", "OKER35"),
        ("Uralskiy_federalnyy_okrug", "5277377", "OKER34"),
        ("Tsentralnyy_federalnyy_okrug", "5277317", "OKER30"),
        ("Yuzhnyy_federalnyy_okrug", "6325041", "OKER37")
    ]

    for region_info in tqdm(regions, desc='Выполняется процесс подготовки данных, подождите', bar_format='{l_bar}{bar}',
                            colour='green'):
        region_processor.fetch_and_process_data(*region_info)
        data_save.save_to_file(f"region_info[0]",'\n'.join(region_processor.result))

    print(f"Данные подготовлены и записаны")
    logging.info(f"Данные подготовлены и записаны: {datetime.now().strftime('%Y-%m-%d')}")
