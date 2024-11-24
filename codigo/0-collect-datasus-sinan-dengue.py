"""Usando o pacote datasus-fetcher, coletamos os dados do SINAN Dengue para o Brasil, no período de 2023 a 2024.

Para instalar o pacote datasus-fetcher, execute o comando abaixo no terminal:

    pip install datasus-fetcher

"""

import logging
from pathlib import Path
from datasus_fetcher import fetcher
from datasus_fetcher.slicer import Slicer


def main():
    logging.basicConfig(level=logging.DEBUG)

    # Definindo o diretório de saída
    output_dir = Path("data", "datasus")

    # Coletando os dados do SINAN Dengue
    fetcher.download_data(
        datasets=["sinan-deng", "sinan-deng-preliminar"],
        destdir=output_dir,
        threads=1,
        slicer=Slicer(start_time="2020", end_time="2024"),
        callback=print,
    )


if __name__ == "__main__":
    main()
