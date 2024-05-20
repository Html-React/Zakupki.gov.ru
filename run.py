import logging
from src import DataPreparation


def main():
    data_preparation = DataPreparation()
    data_preparation.run()


if __name__ == "__main__":
    logging.basicConfig(level=20, filename="logfile.log", filemode="w", format="%(asctime)s %(levelname)s %(message)s",
                        encoding='utf-8')
    main()
