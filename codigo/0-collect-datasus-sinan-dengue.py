"""Usando o pacote datasus-fetcher, coletamos os dados do SINAN Dengue para o Brasil, no período de 2023 a 2024.

Para instalar o pacote datasus-fetcher, execute o comando abaixo no terminal:

    pip install datasus-fetcher

"""

from pathlib import Path
from datasus_fetcher import fetcher
from datasus_fetcher.slicer import Slicer

# Definindo o diretório de saída
output_dir = Path("output")

# Coletando os dados do SINAN Dengue
fetcher.download_data(
    datasets=["sinan-deng"],
    destdir=output_dir,
    threads=1,
    slicer=Slicer(start_time="2023", end_time="2024"),
)
